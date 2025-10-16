from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import aiohttp_client
from pymodbus.client import AsyncModbusTcpClient

from .const import DOMAIN

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    host = entry.data["host"]
    port = entry.data["port"]

    client = AsyncModbusTcpClient(host, port=port)
    await client.connect()

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {
        "client": client,
        "slave_id": entry.data["slave_id"]
    }

    hass.config_entries.async_setup_platforms(entry, ["sensor"])
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    data = hass.data[DOMAIN].pop(entry.entry_id)
    client = data["client"]
    await client.close()
    return True