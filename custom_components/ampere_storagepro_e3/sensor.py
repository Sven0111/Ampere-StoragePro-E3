import asyncio
from homeassistant.helpers.entity import SensorEntity
from pymodbus.client import AsyncModbusTcpClient

async def async_setup_entry(hass, entry, async_add_entities):
    """Setup der Sensoren."""
    host = entry.data.get("host")
    port = entry.data.get("port")
    slave = entry.data.get("slave_id", 1)

    device = ModbusDevice(host, port, slave)

    sensors = [
        ModbusSensor(device, "E3 Energie gesamt", 100, 2, 0.01, "kWh"),
        ModbusSensor(device, "E3 Spannung", 110, 1, 0.1, "V"),
        ModbusSensor(device, "E3 Strom", 111, 1, 0.01, "A"),
    ]

    async_add_entities(sensors, update_before_add=True)


class ModbusDevice:
    """Gemeinsamer Modbus-Client pro Gerät/Slave."""

    def __init__(self, host, port, slave):
        self.host = host
        self.port = port
        self.slave = slave
        self.client = None
        self.lock = asyncio.Lock()

    async def connect(self):
        """Stellt Verbindung zum Modbus-Gerät her."""
        if not self.client:
            self.client = AsyncModbusTcpClient(self.host, port=self.port)
            await self.client.connect()

    async def read_registers(self, address, count):
        """Liest Register vom Gerät."""
        async with self.lock:
            await self.connect()
            rr = await self.client.read_input_registers(address, count, slave=self.slave)
            if rr and rr.registers:
                return rr.registers
            return None

    async def close(self):
        if self.client:
            await self.client.close()
            self.client = None


class ModbusSensor(SensorEntity):
    """Allgemeiner Sensor, der ModbusDevice nutzt."""

    def __init__(self, device: ModbusDevice, name, address, count=1, scale=1, unit=""):
        self.device = device
        self._attr_name = name
        self.address = address
        self.count = count
        self.scale = scale
        self._attr_native_value = None
        self._attr_native_unit_of_measurement = unit

    async def async_update(self):
        """Wird von Home Assistant regelmäßig aufgerufen."""
        try:
            regs = await self.device.read_registers(self.address, self.count)
            if regs:
                raw = 0
                for reg in regs:
                    raw = (raw << 16) + reg
                self._attr_native_value = round(raw * self.scale, 2)
            else:
                self._attr_native_value = None
        except Exception as e:
            self._attr_native_value = None