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
            _LOGGER.info("Successfully read block %s-%s", start_address, start_address + count - 1)
            return rr.registers
    except Exception as e:
        _LOGGER.error("Error reading block %s-%s: %s", start_address, start_address + count - 1, e)
        return None

# ------------------------------------------------------------
# Sensor definition
# ------------------------------------------------------------
class ModbusSensor(SensorEntity):
    """A safe Modbus sensor with automatic updates."""

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

    def update_value(self, raw_value):
        """Convert raw value to scaled value based on data_type."""
        if raw_value is None:
            self._available = False
            self._fail_count += 1
            if self._fail_count % 5 == 0:
                _LOGGER.warning("%s: No data received (%d consecutive failures)", self._attr_name, self._fail_count)
            return

        if self.data_type == "int32" and raw_value >= 0x80000000:
            raw_value -= 0x100000000
        elif self.data_type == "int16" and raw_value >= 0x8000:
            raw_value -= 0x10000

        self._attr_native_value = round(raw_value * self.scale, 2)
        self._available = True
        self._fail_count = 0
        _LOGGER.info("%s updated: %s %s", self._attr_name, self._attr_native_value, self._attr_native_unit_of_measurement)

    async def async_added_to_hass(self):
        """Start periodic updates."""
        _LOGGER.info("%s: Starting updates every %ss", self._attr_name, self._interval)

# ------------------------------------------------------------
# Sensor setup and batch read
# ------------------------------------------------------------
SENSOR_DEFINITIONS = [
    # name, start_address, count, scale, unit, data_type
    ("FoxESS Today Total Charging Capacity", 39607, 2, 0.01, "kWh", "uint32"),
    ("FoxESS PV Power Total", 39601, 2, 0.01, "kWh", "uint32"),
    ("FoxESS PV Power Today", 39603, 2, 0.01, "kWh", "uint32"),
    ("FoxESS Total Charging Capacity", 39605, 2, 0.01, "kWh", "uint32"),
    ("FoxESS Charge Discharge Power", 39612, 2, 0.1, "W", "uint32"),
    ("FoxESS BMS1 SoC", 37612, 1, 1, "%", "uint16"),
]

async def async_setup_entry(hass, entry, async_add_entities):
    """Initialize sensors and start batch updates."""
    host = entry.data.get("host", "127.0.0.1")
    port = entry.data.get("port", 502)
    slave = entry.data.get("slave_id", 247)
    update_interval = entry.options.get("update_interval", 30)

    sensors = [
        ModbusSensor(hass, host, port, slave, *s)
        for s in SENSOR_DEFINITIONS
    ]

    async_add_entities(sensors)
    _LOGGER.info("Ampere StoragePro E3: Sensors successfully registered")

    async def batch_update(now):
        asyncio.create_task(do_batch_read())

    async def do_batch_read():
        """Read all blocks and update sensors."""
        for name, addr, count, scale, unit, dtype in SENSOR_DEFINITIONS:
            regs = await safe_read_block(host, port, slave, addr, count)
            if regs:
                # Combine 16-bit registers to one value
                value = 0
                for reg in regs:
                    value = (value << 16) + reg
                # Update the sensor
                for sensor in sensors:
                    if sensor._attr_name == name:
                        sensor.update_value(value)
                        sensor.async_write_ha_state()

    async_track_time_interval(hass, batch_update, timedelta(seconds=update_interval))