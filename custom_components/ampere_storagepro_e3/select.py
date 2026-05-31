"""Select-Plattform für die Ampere StoragePro E3 Integration (Betriebsmodus)."""
from __future__ import annotations

from typing import Any

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .coordinator import AmpereStorageProE3Coordinator, ampere_device_info

_WORKMODE_REGISTER = 49203

# Gültige Work-Modi des H3 Pro (Register 49203 akzeptiert nur diese Werte)
_OPTION_TO_VALUE = {
    "Self Use": 1,
    "Feed-in First": 2,
    "Back-up": 3,
    "Peak Shaving": 4,
}
_VALUE_TO_OPTION = {value: option for option, value in _OPTION_TO_VALUE.items()}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Select-Entitäten anlegen."""
    coordinator: AmpereStorageProE3Coordinator = entry.runtime_data
    async_add_entities([AmpereWorkModeSelect(coordinator)])


class AmpereWorkModeSelect(
    CoordinatorEntity[AmpereStorageProE3Coordinator], SelectEntity
):
    """Betriebsmodus des Wechselrichters (Work mode, Register 49203)."""

    _attr_name = "Work Mode"
    _attr_entity_category = EntityCategory.CONFIG
    _attr_options = list(_OPTION_TO_VALUE)

    def __init__(self, coordinator: AmpereStorageProE3Coordinator) -> None:
        super().__init__(coordinator)
        self._key = f"ctrl_{_WORKMODE_REGISTER}"
        self._attr_unique_id = (
            f"{coordinator.host}_{coordinator.port}_{coordinator.slave}_work_mode"
        )

    @property
    def device_info(self) -> dict[str, Any]:
        return ampere_device_info(self.coordinator)

    @property
    def available(self) -> bool:
        return super().available and self._key in self.coordinator.data

    @property
    def current_option(self) -> str | None:
        # None (unbekannt), falls das Gerät einen nicht gelisteten Modus meldet
        return _VALUE_TO_OPTION.get(self.coordinator.data.get(self._key))

    async def async_select_option(self, option: str) -> None:
        await self.coordinator.async_write_holding(
            _WORKMODE_REGISTER, _OPTION_TO_VALUE[option]
        )
