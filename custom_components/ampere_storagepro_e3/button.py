"""Button-Plattform für die Ampere StoragePro E3 Integration (Uhrzeit-Sync)."""
from __future__ import annotations

from typing import Any

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.util import dt as dt_util

from .coordinator import AmpereStorageProE3Coordinator, ampere_device_info

# Aufeinanderfolgende Register: Year, Month, Day, Hour, Minute, Second
_TIME_START_REGISTER = 49222


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Button-Entitäten anlegen."""
    coordinator: AmpereStorageProE3Coordinator = entry.runtime_data
    async_add_entities([AmpereSyncTimeButton(coordinator)])


class AmpereSyncTimeButton(
    CoordinatorEntity[AmpereStorageProE3Coordinator], ButtonEntity
):
    """Setzt die Geräte-Uhrzeit auf die aktuelle Home-Assistant-Zeit."""

    _attr_name = "Sync time"
    _attr_entity_category = EntityCategory.CONFIG

    def __init__(self, coordinator: AmpereStorageProE3Coordinator) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = (
            f"{coordinator.host}_{coordinator.port}_{coordinator.slave}_sync_time"
        )

    @property
    def device_info(self) -> dict[str, Any]:
        return ampere_device_info(self.coordinator)

    async def async_press(self) -> None:
        now = dt_util.now()
        await self.coordinator.async_write_holding_block(
            _TIME_START_REGISTER,
            [now.year, now.month, now.day, now.hour, now.minute, now.second],
        )
