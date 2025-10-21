import logging
import asyncio
from datetime import timedelta
from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.event import async_track_time_interval
from pymodbus.client import AsyncModbusTcpClient

_LOGGER = logging.getLogger(__name__)
DOMAIN = "ampere_storagepro_e3"

# ------------------------------------------------------------
# Safe Modbus block read
# ------------------------------------------------------------
async def safe_read_block(host, port, slave, start_address, count, timeout=5):
    """Read Modbus registers safely as a block."""
    try:
        async with AsyncModbusTcpClient(host=host, port=port) as client:
            rr = await client.read_input_registers(
                address=start_address, count=count, device_id=slave
            )
            if rr is None or rr.isError():
                _LOGGER.warning("Failed Modbus read for block %s-%s", start_address, start_address + count - 1)
                return None
            return rr.registers
    except Exception as e:
        _LOGGER.error("Error reading block %s-%s: %s", start_address, start_address + count - 1, e)
        return None


# ------------------------------------------------------------
# Modbus Sensor (für Zahlen)
# ------------------------------------------------------------
class ModbusSensor(SensorEntity):
    """Numeric Modbus sensor with auto updates."""

    _attr_should_poll = False

    def __init__(self, hass, host, port, slave, name, address, count, scale, unit, interval, data_type="uint16"):
        self.hass = hass
        self.host = host
        self.port = port
        self.slave = slave
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
        self._fail_count = 0

    def update_value(self, regs):
        """Convert raw registers to value."""
        if regs is None:
            self._available = False
            self._fail_count += 1
            if self._fail_count % 5 == 0:
                _LOGGER.warning("%s: No data (%d consecutive fails)", self._attr_name, self._fail_count)
            return

        raw_value = 0
        for reg in regs:
            raw_value = (raw_value << 16) + reg

        # Datentyp anpassen
        if self.data_type == "int32" and raw_value >= 0x80000000:
            raw_value -= 0x100000000
        elif self.data_type == "int16" and raw_value >= 0x8000:
            raw_value -= 0x10000

        self._attr_native_value = round(raw_value * self.scale, 2)
        self._available = True
        self._fail_count = 0
        _LOGGER.debug("%s updated: %s %s", self._attr_name, self._attr_native_value, self._attr_native_unit_of_measurement)


# ------------------------------------------------------------
# Modbus String Sensor (für Model Name)
# ------------------------------------------------------------
class ModbusStringSensor(SensorEntity):
    """Reads ASCII strings from Modbus registers."""

    _attr_should_poll = False

    def __init__(self, hass, host, port, slave, name, address, count, interval):
        self.hass = hass
        self.host = host
        self.port = port
        self.slave = slave
        self._attr_name = name
        self.address = address
        self.count = count
        self._attr_native_value = None
        self._available = True
        self._interval = interval
        self._fail_count = 0

    def update_value(self, regs):
        """Decode Modbus registers as ASCII string."""
        if regs is None:
            self._fail_count += 1
            if self._fail_count % 5 == 0:
                _LOGGER.warning("%s: No string data (%d consecutive fails)", self._attr_name, self._fail_count)
            return

        try:
            raw_bytes = b''.join(reg.to_bytes(2, 'big') for reg in regs)
            text = raw_bytes.decode('ascii', errors='ignore').strip('\x00').strip()
            self._attr_native_value = text
            self._available = True
            self._fail_count = 0
            _LOGGER.info("%s updated: %s", self._attr_name, text)
        except Exception as e:
            _LOGGER.error("%s: String decode error: %s", self._attr_name, e)
            self._available = False


# ------------------------------------------------------------
# Sensor definitions
# ------------------------------------------------------------
SENSOR_DEFINITIONS = [
    # (name, start_address, count, scale, unit, data_type)
    ("FoxESS BMS1 SoC", 37612, 1, 1, "%", "uint16"),
    ("FoxESS PV Power Total", 39601, 2, 0.01, "kWh", "uint32"),
    ("FoxESS PV Power Today", 39603, 2, 0.01, "kWh", "uint32"),
    ("FoxESS Total Charging Capacity", 39605, 2, 0.01, "kWh", "uint32"),
    ("FoxESS Todays Total Charging Capacity", 39607, 2, 0.01, "kWh", "uint32"),
    ("FoxESS Total Discharge Power", 39609, 2, 0.01, "kWh", "uint32"),
    ("FoxESS Todays Total Discharge Power", 39611, 2, 0.01, "kWh", "uint32"),
    ("FoxESS Total Power of Feeder Network", 39613, 2, 0.01, "kWh", "uint32"),
    ("FoxESS Todays Total Feeder Power", 39615, 2, 0.01, "kWh", "uint32"),
    ("FoxESS Total Power Taken", 39617, 2, 0.01, "kWh", "uint32"),
    ("FoxESS Todays Total Electricity Consumption", 39619, 2, 0.01, "kWh", "uint32"),
    ("FoxESS Output Total Power", 39621, 2, 0.01, "kWh", "uint32"),
    ("FoxESS Total Power Output Today", 39623, 2, 0.01, "kWh", "uint32"),
    ("FoxESS Enter Total Power", 39625, 2, 0.01, "kWh", "uint32"),
    ("FoxESS Enter Total Power Today", 39627, 2, 0.01, "kWh", "uint32"),
    ("FoxESS Total Load Power", 39629, 2, 0.01, "kWh", "uint32"),
    ("FoxESS Total Load Power Today", 39631, 2, 0.01, "kWh", "uint32"),
]

# ------------------------------------------------------------
# Setup
# ------------------------------------------------------------
async def async_setup_entry(hass, entry, async_add_entities):
    host = entry.data.get("host", "127.0.0.1")
    port = entry.data.get("port", 502)
    slave = entry.data.get("slave_id", 247)
    update_interval = entry.options.get("update_interval", 30)

    sensors = [
        ModbusStringSensor(hass, host, port, slave, "FoxESS Model Name", 30000, 16, update_interval),
        *[
            ModbusSensor(hass, host, port, slave, name, addr, count, scale, unit, update_interval, dtype)
            for name, addr, count, scale, unit, dtype in SENSOR_DEFINITIONS
        ],
    ]

    async_add_entities(sensors)
    _LOGGER.info("Ampere StoragePro E3: %s sensors registered", len(sensors))

    async def batch_update(now):
        asyncio.create_task(do_batch_read())

    async def do_batch_read():
        for sensor in sensors:
            regs = await safe_read_block(sensor.host, sensor.port, sensor.slave, sensor.address, sensor.count)
            if hasattr(sensor, "update_value"):
                sensor.update_value(regs)
                sensor.async_write_ha_state()

    async_track_time_interval(hass, batch_update, timedelta(seconds=update_interval))