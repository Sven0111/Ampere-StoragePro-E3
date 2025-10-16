from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType

DOMAIN = "ampere_storagepro_e3"

async def async_setup(hass: HomeAssistant, config: ConfigType):
    """YAML-Setup (optional, falls du config.yaml nutzt)."""
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Setup über die UI (Config Flow)."""
    hass.async_create_task(
        hass.config_entries.async_forward_entry_setup(entry, "sensor")
    )
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Integration entladen."""
    await hass.config_entries.async_forward_entry_unload(entry, "sensor")
    return True