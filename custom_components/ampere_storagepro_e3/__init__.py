from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
import logging

DOMAIN = "ampere_storagepro_e3"
_LOGGER = logging.getLogger(__name__)

async def async_setup(hass: HomeAssistant, config: dict):
    """Setup bei YAML-Konfiguration (nicht benötigt, da UI)."""
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Setup über Config Flow / UI und Weiterleitung an Sensor-Plattform."""
    _LOGGER.info("Ampere StoragePro E3: Setup Entry gestartet für %s", entry.data.get("host"))
    # Weiterleitung an sensor.py
    return await hass.config_entries.async_forward_entry_setups(entry, ["sensor"])

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Unload Integration und alle Sensoren."""
    unload_ok = await hass.config_entries.async_forward_entry_unload(entry, ["sensor"])
    return unload_ok