import logging
import asyncio
from datetime import timedelta
from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.event import async_track_time_interval
from pymodbus.client import AsyncModbusTcpClient

_LOGGER = logging.getLogger(__name__)
DOMAIN = "ampere_storagepro_e3"

class ModbusDevice:
    """Represents a Modbus TCP device connection."""

    def __init__(self, host: str, port: int, slave: int):
        self.host = host
        self.port = port
        self.slave = slave
        self.client: AsyncModbusTcpClient | None = None
        self._is_connecting = False
        self._lock = asyncio.Lock()

    async def connect(self):
        """Ensure connection is established before any read."""
        async with self._lock:
            if self.client and self.client.connected:
                return  # schon verbunden
            _LOGGER.info("Connecting to Modbus device at %s:%s...", self.host, self.port)
            self.client = AsyncModbusTcpClient(self.host, port=self.port)
            await self.client.connect()
            if not self.client.connected:
                _LOGGER.error("Modbus client could not connect to %s:%s", self.host, self.port)

    async def read_registers(self, address: int, count: int):
        """Read input registers safely."""
        try:
            await self.connect()
            if not self.client or not self.client.connected:
                _LOGGER.error("Modbus client not connected when trying to read address %s", address)
                return None

            rr = await self.client.read_input_registers(address, count=count, device_id=self.slave)
            if rr is None or rr.isError():
                _LOGGER.warning("Invalid or no Modbus response at address %s", address)
                return None
            return rr.registers
        except Exception as e:
            _LOGGER.error("Error reading Modbus registers at address %s: %s", address, e)
            return None

class ModbusSensor(SensorEntity):
    """Modbus sensor supporting int16/uint16/int32/uint32."""

    _attr_should_poll = False

    def __init__(self, hass, device: ModbusDevice, name: str, address: int, count: int, scale: float, unit: str, interval: int, data_type="uint16"):
        self.hass = hass
        self.device = device
        self._attr_name = name
        self.address = address
        self.count = count
        self.scale = scale
        self._attr_native_unit_of_measurement = unit
        self._attr_native_value = None
        self._available = True
        self._interval = interval
        self._unsub_timer = None
        self.data_type = data_type.lower()

    async def async_added_to_hass(self):
        """Start polling with interval."""
        _LOGGER.info("%s: Starting updates every %s seconds", self._attr_name, self._interval)
        self._unsub_timer = async_track_time_interval(
            self.hass, self.async_update_wrapper, timedelta(seconds=self._interval)
        )

    async def async_will_remove_from_hass(self):
        if self._unsub_timer:
            self._unsub_timer()
            self._unsub_timer = None

    async def async_update_wrapper(self, now):
        try:
            await self.async_update()
        except Exception as e:
            _LOGGER.error("%s: Exception in update: %s", self._attr_name, e)

    async def async_update(self):
        regs = await self.device.read_registers(self.address, self.count)
        if regs:
            raw_value = 0
            for reg in regs:
                raw_value = (raw_value << 16) + reg

            # int/uint conversion
            if self.data_type == "int32" and raw_value >= 0x80000000:
                raw_value -= 0x100000000
            elif self.data_type == "int16" and raw_value >= 0x8000:
                raw_value -= 0x10000

            self._attr_native_value = round(raw_value * self.scale, 2)
            self._available = True
            _LOGGER.debug("Sensor %s updated: %s %s", self._attr_name, self._attr_native_value, self._attr_native_unit_of_measurement)
            self.async_write_ha_state()
        else:
            _LOGGER.warning("Sensor %s: No data received", self._attr_name)
            self._available = False

async def async_setup_entry(hass, entry, async_add_entities):
    host = entry.data.get("host", "127.0.0.1")
    port = entry.data.get("port", 1502)
    slave = entry.data.get("slave_id", 247)
    update_interval = entry.options.get("update_interval", 30)
    _LOGGER.info("Ampere StoragePro E3: Update interval set to %ss", update_interval)

    device = ModbusDevice(host, port, slave)
    await device.connect()  # Verbindungsaufbau vor Registrierung der Sensoren

    sensors = [
        ModbusSensor(hass, device, "FoxESS Today Total Charging Capacity", 39607, 2, 0.01, "kWh", update_interval, data_type="uint32"),
        ModbusSensor(hass, device, "FoxESS PV Power Total", 39601, 2, 0.01, "kWh", update_interval, data_type="uint32"),
        ModbusSensor(hass, device, "FoxESS PV Power Today", 39603, 2, 0.01, "kWh", update_interval, data_type="uint32"),
        ModbusSensor(hass, device,
            "FoxESS Total Charging Capacity", 39605, 2, 0.01,
            "kWh",
            update_interval,
            data_type="uint32"),
        ModbusSensor(hass, device,
            "FoxESS Charge Discharge Power", 39612, 2, 0.1,
            "W",
            update_interval,
            data_type="uint32"),
        ModbusSensor(hass, device,
            "FoxESS BMS1 SoC", 39612, 1, 1,
            "%",
            update_interval,
            data_type="uint16"),
    ]

    async_add_entities(sensors)
    _LOGGER.info("Ampere StoragePro E3: Sensors registered successfully.")