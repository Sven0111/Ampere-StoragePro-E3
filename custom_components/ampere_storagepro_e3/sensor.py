import asyncio
import logging
from datetime import timedelta
from contextlib import suppress

from homeassistant.components.sensor import SensorEntity, SensorDeviceClass
from homeassistant.helpers.event import async_track_time_interval
from homeassistant.helpers.entity import EntityCategory
from pymodbus.client import AsyncModbusTcpClient
from .const import DOMAIN
from .sensors import SENSOR_DEFINITIONS  # <-- Sensor-Definitionen importieren

_LOGGER = logging.getLogger(__name__)
_LOCK = asyncio.Lock()


async def async_setup_entry(hass, entry, async_add_entities):
    host = entry.data["host"]
    port = entry.data["port"]
    slave = entry.data["slave_id"]
    update_interval = entry.options.get("update_interval", 30)
    enable_diag = entry.options.get("enable_diagnostics", True)

    # -----------------------------------------------------------
    # 1. Device-Info VOR dem Erstellen der Sensoren auslesen
    # -----------------------------------------------------------
    async with AsyncModbusTcpClient(host=host, port=port) as client:
        if client.connected:
            # Model
            regs = await safe_read_block(client, slave, 30000, 16)
            model = None
            if regs:
                model = b"".join(reg.to_bytes(2, "big") for reg in regs).decode("ascii", errors="ignore").strip("\x00").strip()

            # Serial
            regs = await safe_read_block(client, slave, 30016, 16)
            serial = None
            if regs:
                serial = b"".join(reg.to_bytes(2, "big") for reg in regs).decode("ascii", errors="ignore").strip("\x00").strip()

            # Manufacturer
            regs = await safe_read_block(client, slave, 30032, 16)
            manufacturer = None
            if regs:
                manufacturer = b"".join(reg.to_bytes(2, "big") for reg in regs).decode("ascii", errors="ignore").strip("\x00").strip()

            BaseModbusSensor._device_info_data = {
                "model": model or "FoxESS",
                "serial": serial or "N/A",
                "manufacturer": manufacturer or "Ampere",
            }

            _LOGGER.warning("Device Info loaded BEFORE sensor creation: %s", BaseModbusSensor._device_info_data)
        else:
            _LOGGER.error("Could not connect to Modbus device for initial device info read.")

    # -----------------------------------------------------------
    # 2. Init-Sensoren wie bisher anlegen (Device-Info schon gelesen)
    # -----------------------------------------------------------
    init_sensors = [
        ModbusInitSensor(hass, entry, host, port, slave, "FoxESS Model Name", 30000, 16),
        ModbusInitSensor(hass, entry, host, port, slave, "FoxESS Serial Number", 30016, 16),
        ModbusInitSensor(hass, entry, host, port, slave, "FoxESS Manufacturer ID", 30032, 16),
    ]

    async_add_entities(init_sensors, update_before_add=True)
    for sensor in init_sensors:
        hass.async_create_task(sensor.async_initialize())

    # -----------------------------------------------------------
    # 3. Alle anderen Sensoren aus sensors.py anlegen
    # -----------------------------------------------------------
    string_sensors = []

    sensors = string_sensors.copy()
    for name, addr, count, scale, unit, dtype, cat, device_class, enabled in SENSOR_DEFINITIONS:
        # Nur aktivierte Sensoren hinzufügen
        if not enabled:
            continue
        if not enable_diag and cat == EntityCategory.DIAGNOSTIC:
            continue

        sensors.append(
            ModbusSensor(
                hass,
                entry,
                host,
                port,
                slave,
                name,
                addr,
                count,
                scale,
                unit,
                update_interval,
                dtype,
                category=cat,
                device_class=device_class,
                enabled=enabled,
            )
        )

    async_add_entities(sensors, update_before_add=True)
    _LOGGER.info("Ampere StoragePro E3: %s sensors registered", len(sensors))

    # Intervall-Update
    async def batch_update(_now):
        hass.async_create_task(do_batch_read(host, port, slave, sensors))

    async_track_time_interval(hass, batch_update, timedelta(seconds=update_interval))


# --------------------- Helferfunktionen ---------------------
async def safe_read_block(client, slave, start_address, count, timeout=5):
    try:
        rr = await asyncio.wait_for(
            client.read_input_registers(address=start_address, count=count, device_id=slave),
            timeout=timeout,
        )
        if rr.isError():
            return None
        return rr.registers
    except Exception:
        return None


async def do_batch_read(host, port, slave, sensors):
    if _LOCK.locked():
        return
    async with _LOCK:
        try:
            async with AsyncModbusTcpClient(host=host, port=port) as client:
                if not client.connected:
                    return
                for sensor in sensors:
                    with suppress(Exception):
                        regs = await safe_read_block(client, slave, sensor.address, sensor.count)
                        sensor.update_value(regs)
                        sensor.async_write_ha_state()
        except Exception as e:
            _LOGGER.error("Unexpected Modbus error: %s", e)


# --------------------- Basis-Klasse ---------------------
class BaseModbusSensor(SensorEntity):
    _attr_should_poll = False
    _device_info_data = {"model": None, "serial": None, "manufacturer": None}

    def __init__(self, hass, entry, host, port, slave, name, address, count, interval):
        self.hass = hass
        self.entry = entry
        self.host = host
        self.port = port
        self.slave = slave
        self._attr_name = name
        self.address = address
        self.count = count
        self._interval = interval
        self._attr_unique_id = f"{self.host}_{self.port}_{self.slave}_{name.replace(' ', '_')}"

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, f"{self.host}_{self.port}_{self.slave}")},
            "name": "Ampere StoragePro E3",
            "manufacturer": self._device_info_data.get("manufacturer") or "Ampere",
            "model": self._device_info_data.get("model") or "FoxESS",
            "sw_version": self._device_info_data.get("serial") or "N/A",
        }


# --------------------- Modbus Sensor ---------------------
class ModbusSensor(BaseModbusSensor):
    def __init__(self, hass, entry, host, port, slave, name, address, count, scale, unit, interval, data_type, category=None, device_class=None, enabled=True):
        super().__init__(hass, entry, host, port, slave, name, address, count, interval)
        self.scale = scale
        self.data_type = data_type
        self._attr_native_unit_of_measurement = unit
        self._attr_entity_category = category
        self._attr_device_class = device_class
        self._enabled = enabled
        self._fail_count = 0

    def update_value(self, regs):
        if regs is None:
            self._fail_count += 1
            return
        try:
            raw_value = 0
            for reg in regs:
                raw_value = (raw_value << 16) + reg
            self._attr_native_value = round(raw_value * self.scale, 2)
        except Exception as e:
            _LOGGER.error("%s decode failed: %s", self._attr_name, e)


# --------------------- String Sensoren ---------------------
class ModbusStringSensor(BaseModbusSensor):
    def __init__(self, hass, entry, host, port, slave, name, address, count, interval):
        super().__init__(hass, entry, host, port, slave, name, address, count, interval)

    def update_value(self, regs):
        if regs is None:
            return
        try:
            raw_bytes = b"".join(reg.to_bytes(2, "big") for reg in regs)
            self._attr_native_value = raw_bytes.decode("ascii", errors="ignore").strip("\x00").strip()
        except Exception as e:
            _LOGGER.error("%s string decode failed: %s", self._attr_name, e)


# --------------------- Init Sensoren ---------------------
class ModbusInitSensor(BaseModbusSensor):
    """Sensor, der nur einmal beim Setup gelesen wird."""

    def __init__(self, hass, entry, host, port, slave, name, address, count):
        super().__init__(hass, entry, host, port, slave, name, address, count, interval=0)

    async def async_initialize(self):
        try:
            async with AsyncModbusTcpClient(host=self.host, port=self.port) as client:
                if client.connected:
                    regs = await safe_read_block(client, self.slave, self.address, self.count)
                    if regs:
                        raw_bytes = b"".join(reg.to_bytes(2, "big") for reg in regs)
                        value = raw_bytes.decode("ascii", errors="ignore").strip("\x00").strip()
                        self._attr_native_value = value

                        # Geräteinfo aktualisieren
                        if self._attr_name == "FoxESS Model Name":
                            BaseModbusSensor._device_info_data["model"] = value
                        elif self._attr_name == "FoxESS Serial Number":
                            BaseModbusSensor._device_info_data["serial"] = value
                        elif self._attr_name == "FoxESS Manufacturer ID":
                            BaseModbusSensor._device_info_data["manufacturer"] = value

                        _LOGGER.warning("device_info updated: %s", BaseModbusSensor._device_info_data)

                        info = BaseModbusSensor._device_info_data
                        if info["model"] and info["serial"] and info["manufacturer"]:
                            all_sensors = self.hass.data.setdefault(DOMAIN, {}).get("all_sensors", [])
                            for sensor in all_sensors:
                                sensor.async_schedule_update_ha_state(force_refresh=True)

                        self.async_write_ha_state()

        except Exception as e:
            _LOGGER.error("%s initial read failed: %s", self._attr_name, e)