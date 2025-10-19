from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from .const import DOMAIN

async def async_setup(hass: HomeAssistant, config: dict):
    """Set up integration (YAML not used)."""
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Ampere StoragePro E3 from a config entry."""
    update_interval = entry.options.get("update_interval", 30)
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = {"update_interval": update_interval}

    # Setup sensors
    await hass.config_entries.async_forward_entry_setups(entry, ["sensor"])

    # Watch for option changes
    entry.async_on_unload(entry.add_update_listener(_update_listener))
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload entry."""
    unload_ok = await hass.config_entries.async_forward_entry_unload(entry, "sensor")
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id, None)
    return unload_ok


async def _update_listener(hass: HomeAssistant, entry: ConfigEntry):
    """Handle options update by reloading entry."""
    # ✅ reload asynchronously (prevents HA freeze)
    hass.async_create_task(hass.config_entries.async_reload(entry.entry_id))