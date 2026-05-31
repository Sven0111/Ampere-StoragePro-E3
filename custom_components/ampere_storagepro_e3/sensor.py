"""Sensor-Plattform für die Ampere StoragePro E3 Integration."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .coordinator import AmpereStorageProE3Coordinator, ampere_device_info
from .sensors import SENSOR_DEFINITIONS

_LOGGER = logging.getLogger(__name__)

# Status-Holding-Register (RO), die der Coordinator als ctrl_<addr> bereitstellt
_NETWORK_STATUS_REGISTER = 49240
_GFCI_CURRENT_REGISTER = 49249
_TRIGGER_SIGNAL_REGISTER = 49242

_NETWORK_STATUS_TEXT = {
    0: "Not connected",
    1: "Disconnection",
    2: "Connection",
}

# Präfix -> Schlüssel in coordinator.connected_flags
_CONNECT_PREFIX = {
    "BMS1": "bms1",
    "BMS2": "bms2",
    "Meter1": "meter1",
    "Meter2": "meter2",
}

# Device-Classes, die einen momentanen Messwert darstellen -> state_class measurement
_MEASUREMENT_DEVICE_CLASSES = {
    SensorDeviceClass.POWER,
    SensorDeviceClass.VOLTAGE,
    SensorDeviceClass.CURRENT,
    SensorDeviceClass.TEMPERATURE,
    SensorDeviceClass.FREQUENCY,
    SensorDeviceClass.BATTERY,
}

_ENERGY_UNITS = {"kWh", "Wh"}

# Schlüsselwörter, die einen Metadaten-/Info-Sensor kennzeichnen
_DIAGNOSTIC_KEYWORDS = (
    "version", "connect", "flag", "mfg", "model",
    "number of", "protocol", "reserve", "sn", "pn",
)


def _is_diagnostic(name: str, dtype: str) -> bool:
    """Metadaten-/Info-Sensoren als Diagnose einstufen (String- und Versions-/ID-Werte)."""
    if dtype == "str":
        return True
    lname = name.lower()
    return any(keyword in lname for keyword in _DIAGNOSTIC_KEYWORDS)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Sensoren anhand der Definitionen anlegen."""
    coordinator: AmpereStorageProE3Coordinator = entry.runtime_data
    enable_diag = entry.options.get("enable_diagnostics", True)
    flags = coordinator.connected_flags

    # Entitäten für nicht verbundene Komponenten aus der Registry entfernen
    # (nur Einträge DIESES Config-Entries betrachten).
    entity_registry = er.async_get(hass)
    for reg_entry in er.async_entries_for_config_entry(entity_registry, entry.entry_id):
        name = reg_entry.original_name or reg_entry.name or ""
        for prefix, flag_key in _CONNECT_PREFIX.items():
            if flags.get(flag_key) == 0 and name.startswith(prefix):
                entity_registry.async_remove(reg_entry.entity_id)
                break

    entities: list[AmpereModbusSensor] = []
    for sd in SENSOR_DEFINITIONS:
        name, _addr, _count, _scale, _unit, dtype, _cat, _dc, _enabled, visible = sd

        if not visible:
            continue
        if not enable_diag and _is_diagnostic(name, dtype):
            continue

        # Nicht verbundene BMS/Meter überspringen
        skip = False
        for prefix, flag_key in _CONNECT_PREFIX.items():
            if name.startswith(prefix) and flags.get(flag_key) == 0:
                skip = True
                break
        if skip:
            continue

        entities.append(AmpereModbusSensor(coordinator, entry, sd))

    # Status-Sensoren aus Holding-Registern (unabhängig von SENSOR_DEFINITIONS)
    status_entities: list[CoordinatorEntity] = [
        AmpereNetworkStatusSensor(coordinator),
        AmpereGfciCurrentSensor(coordinator),
        AmpereTriggerSignalSensor(coordinator),
    ]

    async_add_entities([*entities, *status_entities])


class AmpereModbusSensor(CoordinatorEntity[AmpereStorageProE3Coordinator], SensorEntity):
    """Ein einzelner Sensor, dessen Wert aus den Coordinator-Daten stammt."""

    def __init__(
        self,
        coordinator: AmpereStorageProE3Coordinator,
        entry: ConfigEntry,
        definition: tuple,
    ) -> None:
        super().__init__(coordinator)
        name, _addr, _count, _scale, unit, dtype, _cat, device_class, enabled, _vis = (
            definition
        )

        self._key = name
        self._dtype = dtype

        host = coordinator.host
        port = coordinator.port
        slave = coordinator.slave

        is_diagnostic = _is_diagnostic(name, dtype)

        self._attr_name = name
        # unique_id-Schema unverändert beibehalten (keine History-Verluste)
        self._attr_unique_id = f"{host}_{port}_{slave}_{name.replace(' ', '_')}"
        self._attr_native_unit_of_measurement = unit or None
        self._attr_entity_category = (
            EntityCategory.DIAGNOSTIC if is_diagnostic else None
        )
        self._attr_entity_registry_enabled_default = enabled

        # Bit-Sensoren sind reine Text-Sensoren (kein enum mit leeren options)
        if not dtype.startswith("bit"):
            self._attr_device_class = device_class

            if device_class == SensorDeviceClass.ENERGY:
                self._attr_state_class = SensorStateClass.TOTAL_INCREASING
            elif device_class in _MEASUREMENT_DEVICE_CLASSES:
                self._attr_state_class = SensorStateClass.MEASUREMENT
            elif (
                device_class is None
                and unit
                and unit not in _ENERGY_UNITS
                and not is_diagnostic
            ):
                # numerische Messwerte ohne passende device_class (z. B. Var, VA, Ah)
                self._attr_state_class = SensorStateClass.MEASUREMENT

    @property
    def device_info(self) -> dict[str, Any]:
        return ampere_device_info(self.coordinator)

    @property
    def native_value(self) -> Any:
        return self.coordinator.data.get(self._key)

    @property
    def available(self) -> bool:
        return super().available and self._key in self.coordinator.data


class _AmpereStatusSensorBase(
    CoordinatorEntity[AmpereStorageProE3Coordinator], SensorEntity
):
    """Basis für Status-Sensoren, die aus einem Holding-Register (ctrl_<addr>) stammen."""

    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(
        self, coordinator: AmpereStorageProE3Coordinator, register: int, suffix: str
    ) -> None:
        super().__init__(coordinator)
        self._key = f"ctrl_{register}"
        self._attr_unique_id = (
            f"{coordinator.host}_{coordinator.port}_{coordinator.slave}_{suffix}"
        )

    @property
    def device_info(self) -> dict[str, Any]:
        return ampere_device_info(self.coordinator)

    @property
    def available(self) -> bool:
        return super().available and self._key in self.coordinator.data


class AmpereNetworkStatusSensor(_AmpereStatusSensorBase):
    """Netzwerk-/Cloud-Verbindungsstatus (Register 49240)."""

    _attr_name = "Network Status"

    def __init__(self, coordinator: AmpereStorageProE3Coordinator) -> None:
        super().__init__(coordinator, _NETWORK_STATUS_REGISTER, "network_status")

    @property
    def native_value(self) -> str | None:
        value = self.coordinator.data.get(self._key)
        if value is None:
            return None
        return _NETWORK_STATUS_TEXT.get(value, f"Unknown ({value})")


class AmpereGfciCurrentSensor(_AmpereStatusSensorBase):
    """Fehlerstrom (GFCI Current, Register 49249, I16, Gain 100)."""

    _attr_name = "GFCI Current"
    _attr_device_class = SensorDeviceClass.CURRENT
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = "A"

    def __init__(self, coordinator: AmpereStorageProE3Coordinator) -> None:
        super().__init__(coordinator, _GFCI_CURRENT_REGISTER, "gfci_current")

    @property
    def native_value(self) -> float | None:
        value = self.coordinator.data.get(self._key)
        if value is None:
            return None
        # I16: vorzeichenbehaftet interpretieren
        if value >= 0x8000:
            value -= 0x10000
        return round(value / 100, 2)


class AmpereTriggerSignalSensor(_AmpereStatusSensorBase):
    """Trigger-Signale K1–K4 als Klartext (Register 49242, Bitfeld)."""

    _attr_name = "Trigger Signal"

    def __init__(self, coordinator: AmpereStorageProE3Coordinator) -> None:
        super().__init__(coordinator, _TRIGGER_SIGNAL_REGISTER, "trigger_signal")

    @property
    def native_value(self) -> str | None:
        value = self.coordinator.data.get(self._key)
        if value is None:
            return None
        active = [f"K{bit + 1}" for bit in range(4) if value & (1 << bit)]
        return ", ".join(active) if active else "None"
