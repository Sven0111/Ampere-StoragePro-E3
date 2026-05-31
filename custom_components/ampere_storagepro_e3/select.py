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
_GRID_CODE_REGISTER = 49079

# Gültige Work-Modi des H3 Pro (Register 49203 akzeptiert nur diese Werte)
_OPTION_TO_VALUE = {
    "Self Use": 1,
    "Feed-in First": 2,
    "Back-up": 3,
    "Peak Shaving": 4,
}
_VALUE_TO_OPTION = {value: option for option, value in _OPTION_TO_VALUE.items()}

# Netz-Standard-Codes (Register 49079), siehe Modbus-Protokoll Tabelle 4-2.
# Enumerationswert -> Standardname (technischer Code lt. Spezifikation).
_GRID_CODE_VALUE_TO_NAME = {
    0: "AS4777_AU", 1: "AS4777_NZ", 2: "G98_UK", 3: "G99_UK", 4: "EN50549_NL",
    5: "CEI021_A", 6: "VDE0126", 7: "VDE4105_DE", 8: "NBR-220_BR", 9: "NBR-240_BR",
    10: "IEC61727", 11: "Philippines", 12: "NRS_SA", 13: "Vietnam", 14: "EN50549_PL",
    15: "EN50549_PT", 16: "PPDS_CR", 17: "UNE-206_SP", 18: "RD1699_SP", 19: "Belgium",
    20: "VFR2019_FR", 21: "UTE_FR", 22: "Singapore", 23: "Indonesia", 24: "Malaysia",
    25: "Cambodia", 26: "PEA_TH", 27: "MEA_TH", 28: "Sri Lanka", 29: "Pakistan",
    30: "Ireland", 31: "Denmark 3.2.1", 32: "Slovakia", 33: "Austria", 34: "Switzerland",
    35: "Slovenia", 36: "Hungary", 37: "Serbia", 38: "Croatia", 39: "Turkey",
    40: "Cyprus", 41: "Bulgaria", 42: "Romania", 43: "Greece", 44: "Latvia",
    45: "Lithuania", 46: "Estonia", 47: "Sweden", 48: "Norway", 49: "Finland",
    50: "Argentina", 51: "Chile BT", 52: "Mexico", 53: "USA", 54: "Hawaii",
    55: "CQC_CN", 56: "Japan", 57: "CQC_CN-1", 58: "Local", 59: "Saudi Arabia",
    60: "AS4777_AU-2020A", 61: "AS4777_AU-2020B", 62: "AS4777_AU-2020C",
    63: "AS4777_NZ-2020", 64: "CQC_CN-2", 65: "CEI021_B", 66: "CEI021_Areti_A",
    67: "CEI021_Areti_B", 68: "NBR-220_BR2022", 69: "Spain", 70: "CQC_CN-3",
    71: "Puerto Rico", 72: "G98_NI", 73: "G99_NI", 74: "USA-208", 75: "VDE4110_DE",
    76: "KSC8564", 77: "KSC8565", 78: "PR-LUMA", 79: "CEI016", 80: "DUBAI",
    81: "Denmark3.2.2", 82: "TR 3.3.1-DK1", 83: "TR 3.3.1-DK2", 84: "Chile MT-A",
    85: "Chile MT-B", 86: "EN50549_FR", 87: "NBR-127_BR2022", 88: "NBR-W220BR2022",
    89: "TWN-T", 90: "TWN-S", 91: "Israel", 92: "EN50549_FR_W", 93: "Test-50Hz",
    94: "Test-60Hz", 95: "CQC_CN-4", 96: "EN 50549-2", 97: "CQC_CN-5",
}
_GRID_CODE_NAME_TO_VALUE = {
    name: value for value, name in _GRID_CODE_VALUE_TO_NAME.items()
}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Select-Entitäten anlegen."""
    coordinator: AmpereStorageProE3Coordinator = entry.runtime_data
    async_add_entities(
        [
            AmpereWorkModeSelect(coordinator),
            AmpereGridStandardCodeSelect(coordinator),
        ]
    )


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


class AmpereGridStandardCodeSelect(
    CoordinatorEntity[AmpereStorageProE3Coordinator], SelectEntity
):
    """Netz-Standard-Code des Wechselrichters (Grid standard code, Register 49079).

    ACHTUNG: sicherheits-/zulassungsrelevante Einstellung. Der Wert muss den
    lokalen regulatorischen Vorgaben entsprechen. Das Schreiben kann am Gerät
    eine Authentifizierung erfordern und schlägt dann mit einem Fehler fehl.
    """

    _attr_name = "Grid Standard Code"
    _attr_entity_category = EntityCategory.CONFIG
    _attr_options = list(_GRID_CODE_VALUE_TO_NAME.values())

    def __init__(self, coordinator: AmpereStorageProE3Coordinator) -> None:
        super().__init__(coordinator)
        self._key = f"ctrl_{_GRID_CODE_REGISTER}"
        self._attr_unique_id = (
            f"{coordinator.host}_{coordinator.port}_{coordinator.slave}"
            "_grid_standard_code"
        )

    @property
    def device_info(self) -> dict[str, Any]:
        return ampere_device_info(self.coordinator)

    @property
    def available(self) -> bool:
        return super().available and self._key in self.coordinator.data

    @property
    def current_option(self) -> str | None:
        # None, falls das Gerät einen nicht gelisteten Code meldet
        return _GRID_CODE_VALUE_TO_NAME.get(self.coordinator.data.get(self._key))

    async def async_select_option(self, option: str) -> None:
        await self.coordinator.async_write_holding(
            _GRID_CODE_REGISTER, _GRID_CODE_NAME_TO_VALUE[option]
        )
