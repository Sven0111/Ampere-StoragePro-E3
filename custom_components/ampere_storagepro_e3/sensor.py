from homeassistant.helpers.entity import SensorEntity
from pymodbus.client import AsyncModbusTcpClient
import asyncio

async def async_setup_entry(hass, entry, async_add_entities):
    host = entry.data.get("host")
    port = entry.data.get("port")
    slave = entry.data.get("slave_id", 1)

    device = ModbusDevice(host, port, slave)

    sensors = [
        ModbusSensor(device, "kWh Gesamt", 39607, 2, 0.01, "kWh"),
    ]

    async_add_entities(sensors, update_before_add=True)


class ModbusDevice:
    def __init__(self, host, port, slave):
        self.host = host
        self.port = port
        self.slave = slave
        self.client = None
        self.lock = asyncio.Lock()

    async def connect(self):
        if not self.client:
            self.client = AsyncModbusTcpClient(self.host, port=self.port)
            await self.client.connect()

    async def read_registers(self, address, count):
        async with self.lock:
            await self.connect()
            rr = await self.client.read_input_registers(address, count, slave=self.slave)
            return rr.registers if rr and rr.registers else None


class ModbusSensor(SensorEntity):
    def __init__(self, device, name, address, count, scale, unit):
        self.device = device
        self._attr_name = name
        self.address = address
        self.count = count
        self.scale = scale
        self._attr_native_value = None
        self._attr_native_unit_of_measurement = unit

    async def async_update(self):
        try:
            regs = await self.device.read_registers(self.address, self.count)
            if regs:
                raw = 0
                for reg in regs:
                    raw = (raw << 16) + reg
                self._attr_native_value = round(raw * self.scale, 2)
            else:
                self._attr_native_value = None
        except Exception:
            self._attr_native_value = None