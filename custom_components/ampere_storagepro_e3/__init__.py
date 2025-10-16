from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

DOMAIN = "ampere_storagepro_e3"

async def async_setup(hass: HomeAssistant, config: dict):
    """Setup bei YAML-Konfiguration (nicht nötig, da UI)."""
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Setup über die Benutzeroberfläche (Config Flow)."""
    # Sensor-Plattform registrieren
    hass.async_create_task(
        hass.config_entries.async_forward_entry_setups(entry, "sensor")
    )
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Integration entladen."""
    # unload_ok = True, wenn Sensor-Plattform sauber entladen wurde
    unload_ok = await hass.config_entries.async_forward_entry_unload(entry, "sensor")
    return unload_ok