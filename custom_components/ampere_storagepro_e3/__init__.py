"""Ampere StoragePro E3 Integration."""
from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import PLATFORMS
from .coordinator import AmpereStorageProE3Coordinator

AmpereConfigEntry = ConfigEntry[AmpereStorageProE3Coordinator]


async def async_setup_entry(hass: HomeAssistant, entry: AmpereConfigEntry) -> bool:
    """Set up integration from ConfigEntry."""
    coordinator = AmpereStorageProE3Coordinator(hass, entry)
    await coordinator.async_config_entry_first_refresh()

    entry.runtime_data = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(async_reload_entry))
    return True


async def async_unload_entry(hass: HomeAssistant, entry: AmpereConfigEntry) -> bool:
    """Unload integration."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        await entry.runtime_data.async_shutdown_client()
    return unload_ok


async def async_reload_entry(hass: HomeAssistant, entry: AmpereConfigEntry) -> None:
    """Reload integration when options change."""
    await hass.config_entries.async_reload(entry.entry_id)
