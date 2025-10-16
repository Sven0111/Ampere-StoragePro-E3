from homeassistant.components.sensor import SensorEntity
from homeassistant.const import UnitOfTemperature, UnitOfElectricPotential
from pymodbus.exceptions import ModbusException
from .const import DOMAIN

SENSORS = [
    {
        "name": "FoxESS PV Power Total1",
        "address": 39607,
        "unit": "kWh",
        "scale": 0.01,
        "precision": 2
    },
]

async def async_setup_entry(hass, entry, async_add_entities):
    data = hass.data[DOMAIN][entry.entry_id]
    client = data["client"]
    slave = data["slave_id"]

    entities = [ModbusCustomSensor(client, slave, s) for s in SENSORS]
    async_add_entities(entities, True)

class ModbusCustomSensor(SensorEntity):
    def __init__(self, client, slave, config):
        self._client = client
        self._slave = slave
        self._name = config["name"]
        self._address = config["address"]
        self._attr_name = f"Modbus {self._name}"
        self._attr_native_unit_of_measurement = config["unit"]
        self._attr_should_poll = True
        self._state = None

    @property
    def native_value(self):
        return self._state

    async def async_update(self):
        try:
            rr = await self._client.read_holding_registers(self._address, 1, slave=self._slave)
            if rr.isError():
                self._state = None
            else:
                self._state = rr.registers[0]
        except ModbusException:
            self._state = None