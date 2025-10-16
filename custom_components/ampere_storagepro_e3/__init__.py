from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType
from .const import DOMAIN
from .sensor import ModbusKwhSensor
from homeassistant.helpers.entity_platform import AddEntitiesCallback

async def async_setup(hass: HomeAssistant, config: ConfigType):
    """Setup ohne Config Flow (YAML optional)."""
    return True

async def async_setup_entry(hass, entry, async_add_devices: AddEntitiesCallback):
    """Setup über UI (Config Flow)."""
    host = entry.data.get("host")
    port = entry.data.get("port")
    slave_id = entry.data.get("slave_id")

    sensor = ModbusKwhSensor(host, port, slave_id)
    async_add_devices([sensor])
    return True