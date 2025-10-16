from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from .sensor import ModbusKwhSensor, ModbusExampleSensor
from .const import DOMAIN

async def async_setup(hass: HomeAssistant, config: dict):
    """Setup ohne Config Flow (YAML optional)."""
    return True

async def async_setup_entry(hass: HomeAssistant, entry, async_add_devices: AddEntitiesCallback):
    """Setup über UI (Config Flow)."""
    host = entry.data.get("host")
    port = entry.data.get("port")
    slave_id = entry.data.get("slave_id")

    sensors = [
        ModbusKwhSensor(host, port, slave_id),
        ModbusExampleSensor(host, port, slave_id)
    ]

    async_add_devices(sensors)
    return True