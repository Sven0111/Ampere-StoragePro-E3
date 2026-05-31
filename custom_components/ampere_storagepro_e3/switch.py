"""Switch-Plattform für die Ampere StoragePro E3 Integration (Buzzer)."""
from __future__ import annotations

from typing import Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .coordinator import AmpereStorageProE3Coordinator, ampere_device_info

_BUZZER_REGISTER = 49209


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Schalter-Entitäten anlegen."""
    coordinator: AmpereStorageProE3Coordinator = entry.runtime_data
    async_add_entities([AmpereBuzzerSwitch(coordinator)])


class AmpereBuzzerSwitch(
    CoordinatorEntity[AmpereStorageProE3Coordinator], SwitchEntity
):
    """Summer/Alarmton an- und ausschalten (Holding-Register 49209)."""

    _attr_name = "Buzzer"
    _attr_entity_category = EntityCategory.CONFIG

    def __init__(self, coordinator: AmpereStorageProE3Coordinator) -> None:
        super().__init__(coordinator)
        self._key = f"ctrl_{_BUZZER_REGISTER}"
        self._attr_unique_id = (
            f"{coordinator.host}_{coordinator.port}_{coordinator.slave}_buzzer"
        )

    @property
    def device_info(self) -> dict[str, Any]:
        return ampere_device_info(self.coordinator)

    @property
    def available(self) -> bool:
        return super().available and self._key in self.coordinator.data

    @property
    def is_on(self) -> bool | None:
        value = self.coordinator.data.get(self._key)
        return None if value is None else value == 1

    async def async_turn_on(self, **kwargs: Any) -> None:
        await self.coordinator.async_write_holding(_BUZZER_REGISTER, 1)

    async def async_turn_off(self, **kwargs: Any) -> None:
        await self.coordinator.async_write_holding(_BUZZER_REGISTER, 0)
