from homeassistant.helpers.entity import SensorEntity
from pymodbus.client.asynchronous.tcp import AsyncModbusTCPClient
import asyncio

class ModbusDevice:
    """Gemeinsamer Modbus-Client pro Gerät/Slave."""
    def __init__(self, host, port, slave):
        self.host = host
        self.port = port
        self.slave = slave
        self.client = None
        self.lock = asyncio.Lock()

    async def connect(self):
        if not self.client:
            self.client = AsyncModbusTCPClient(self.host, self.port)
            await self.client.connect()

    async def read_registers(self, address, count):
        async with self.lock:
            await self.connect()
            rr = await self.client.protocol.read_input_registers(address, count, unit=self.slave)
            return rr.registers if rr else None

    async def close(self):
        if self.client:
            await self.client.close()
            self.client = None

class ModbusSensor(SensorEntity):
    """Allgemeiner Sensor, der ModbusDevice nutzt."""
    def __init__(self, device: ModbusDevice, name, address, count=1, scale=1, unit=""):
        self.device = device
        self._name = name
        self.address = address
        self.count = count
        self.scale = scale
        self._state = None
        self.unit = unit

    @property
    def name(self):
        return self._name

    @property
    def native_value(self):
        return self._state

    @property
    def native_unit_of_measurement(self):
        return self.unit

    async def async_update(self):
        try:
            regs = await self.device.read_registers(self.address, self.count)
            if regs:
                raw = sum(reg << (16 * i) for i, reg in enumerate(reversed(regs)))
                self._state = round(raw * self.scale, 2)
            else:
                self._state = None
        except Exception:
            self._state = None