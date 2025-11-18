from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from .const import DOMAIN

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up integration from ConfigEntry."""
    hass.data.setdefault(DOMAIN, {})
    # Wichtig: update_before_add=True wird in sensor.py genutzt
    await hass.config_entries.async_forward_entry_setups(entry, ["sensor"])
    entry.async_on_unload(entry.add_update_listener(async_reload_entry))
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Unload integration."""
    return await hass.config_entries.async_unload_platforms(entry, ["sensor"])

async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Reload integration when options change."""
    await hass.config_entries.async_reload(entry.entry_id)