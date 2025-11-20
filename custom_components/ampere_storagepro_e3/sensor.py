import asyncio
import logging
from datetime import timedelta
from contextlib import suppress

from homeassistant.components.sensor import SensorEntity, SensorDeviceClass
from homeassistant.helpers.event import async_track_time_interval
from homeassistant.helpers.entity import EntityCategory
from pymodbus.client import AsyncModbusTcpClient
from .const import DOMAIN
from .sensors import SENSOR_DEFINITIONS  # Sensor-Definitionen importieren

_LOGGER = logging.getLogger(__name__)
_LOCK = asyncio.Lock()
_MAX_REGS_PER_BATCH = 120  # Maximal 120 Register pro Batch


async def async_setup_entry(hass, entry, async_add_entities):
    host = entry.data["host"]
    port = entry.data["port"]
    slave = entry.data["slave_id"]
    update_interval = entry.options.get("update_interval", 30)
    enable_diag = entry.options.get("enable_diagnostics", True)

    # -----------------------------
    # 1. Device-Info vor dem Erstellen der Sensoren auslesen
    # -----------------------------
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
        else:
            _LOGGER.error("Could not connect to Modbus device for initial device info read.")

    # -----------------------------
    # 2. Init-Sensoren einmalig anlegen
    # -----------------------------
    init_sensors = [
        ModbusInitSensor(hass, entry, host, port, slave, "FoxESS Model Name", 30000, 16),
        ModbusInitSensor(hass, entry, host, port, slave, "FoxESS Serial Number", 30016, 16),
        ModbusInitSensor(hass, entry, host, port, slave, "FoxESS Manufacturer ID", 30032, 16),
    ]

    async_add_entities(init_sensors, update_before_add=True)
    for sensor in init_sensors:
        hass.async_create_task(sensor.async_initialize())

    # -----------------------------
    # 3. Alle anderen Sensoren anlegen
    # -----------------------------
    all_sensors = []
    visible_sensors = []

    for sd in SENSOR_DEFINITIONS:
        try:
            name, addr, count, scale, unit, dtype, cat, device_class, enabled, visible = sd

            if not enable_diag and cat == EntityCategory.DIAGNOSTIC:
                continue

            if dtype == "str":
                sensor_obj = ModbusStringSensor(hass, entry, host, port, slave, name, addr, count, update_interval)
            else:
                sensor_obj = ModbusSensor(
                    hass, entry, host, port, slave, name, addr, count,
                    scale, unit, update_interval, dtype,
                    category=cat, device_class=device_class, enabled=enabled
                )

            all_sensors.append(sensor_obj)

            if visible:
                visible_sensors.append(sensor_obj)

        except Exception as e:
            _LOGGER.error("Error creating sensor %s at %s: %s", name, addr, e)

    ha_sensors = [s for s in visible_sensors if getattr(s, "_attr_name", None)]

    async_add_entities(ha_sensors, update_before_add=True)

    # Batches für alle Sensoren erzeugen
    batches = create_batches(all_sensors)
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = {
        "batches": batches,
        "ha_sensors": ha_sensors,  # <--- hier speichern
    }


    # -----------------------------
    # 5. Intervall-Update
    # -----------------------------
    async def batch_update(_now):
        batches = hass.data[DOMAIN][entry.entry_id].get("batches", [])
        ha_sensors = hass.data[DOMAIN][entry.entry_id].get("ha_sensors", [])
        hass.async_create_task(do_batch_read(host, port, slave, batches, ha_sensors))

    async_track_time_interval(hass, batch_update, timedelta(seconds=update_interval))

    # einmalige Initialabfrage
    hass.async_create_task(do_batch_read(host, port, slave, batches, ha_sensors))


# ----------------------------- Helferfunktionen -----------------------------
async def safe_read_block(client, slave, start_address, count, timeout=5):
    try:
        rr = await asyncio.wait_for(
            client.read_input_registers(address=start_address, count=count, device_id=slave),
            timeout=timeout,
        )
        if rr.isError():
            _LOGGER.warning("Modbus error reading address %s", start_address)
            return None
        return rr.registers
    except Exception as e:
        _LOGGER.error("Exception reading Modbus address %s: %s", start_address, e)
        return None


def create_batches(sensors):
    """Sensoren in Batches zusammenfassen, maximal _MAX_REGS_PER_BATCH Register pro Batch.
       Ein Batch wird auch bei Lücke zwischen Adressen beendet.
       Jetzt berücksichtigt auch die Sensorgröße korrekt.
    """
    sensors_sorted = sorted(sensors, key=lambda s: s.address)
    batches = []
    current_batch = []
    batch_start = None
    batch_end = None

    for sensor in sensors_sorted:
        sensor_end = sensor.address + sensor.count - 1

        if batch_start is None:
            batch_start = sensor.address
            batch_end = sensor_end
            current_batch.append(sensor)
        else:
            # Prüfen, ob Batch durch Lücke oder max Größe überschritten wird
            if sensor.address > batch_end + 1 or (sensor_end - batch_start + 1) > _MAX_REGS_PER_BATCH:
                # Batch abschließen
                batches.append((batch_start, batch_end, current_batch))
                _LOGGER.info("Batch %d: Start=%d, End=%d, Sensors=%d",
                             len(batches), batch_start, batch_end, len(current_batch))
                # neuen Batch starten
                current_batch = [sensor]
                batch_start = sensor.address
                batch_end = sensor_end
            else:
                batch_end = max(batch_end, sensor_end)
                current_batch.append(sensor)

    if current_batch:
        batches.append((batch_start, batch_end, current_batch))
        _LOGGER.info("Batch %d: Start=%d, End=%d, Sensors=%d",
                     len(batches), batch_start, batch_end, len(current_batch))

    return batches


# ----------------------------- Angepasste do_batch_read -----------------------------
async def do_batch_read(host, port, slave, batches, ha_sensors):
    if _LOCK.locked():
        return
    async with _LOCK:
        try:
            async with AsyncModbusTcpClient(host=host, port=port) as client:
                if not client.connected:
                    return

                for start, end, sensors in batches:
                    count = end - start + 1
                    with suppress(Exception):

                        regs = await safe_read_block(client, slave, start, count)

                        if regs:
                            try:
                                for sensor in sensors:
                                    if not sensor or sensor.hass is None:
                                        continue

                                    start_idx = sensor.address - start
                                    end_idx = start_idx + sensor.count
                                    if start_idx < 0 or end_idx > len(regs):
                                        _LOGGER.warning("Sensor %s not in batch range: sensor %d-%d, batch %d-%d",
                                        sensor._attr_name, sensor.address, sensor.address+sensor.count-1, start, end)
                                        continue

                                    sensor_regs = regs[start_idx:end_idx]

                                    try:
                                        sensor.update_value(sensor_regs)
                                        if getattr(sensor, "_attr_name", None) and sensor in ha_sensors:
                                            sensor.async_write_ha_state()
                                    except Exception as e:
                                        _LOGGER.debug(
                                            "Skipping update for sensor %s (not in HA): %s", sensor._attr_name, e
                                        )

                            except Exception as e:
                                _LOGGER.error("Error updating sensor %s at %s: %s", sensor._attr_name, sensor.address, e)
                                continue
                        else:
                            _LOGGER.warning("No registers read for batch: Start=%d, End=%d", start, end)

        except Exception as e:
            _LOGGER.error("Unexpected Modbus error: %s", e)


# ----------------------------- Basis-Klasse -----------------------------
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


# ----------------------------- Modbus Sensor -----------------------------
class ModbusSensor(BaseModbusSensor):
    def __init__(self, hass, entry, host, port, slave, name, address, count, scale, unit, interval, data_type, category=None, device_class=None, enabled=True):
        super().__init__(hass, entry, host, port, slave, name, address, count, interval)
        self.scale = scale
        self.data_type = data_type
        self._attr_native_unit_of_measurement = unit
        self._attr_entity_category = category
        self._attr_device_class = device_class
        self._attr_entity_registry_enabled_default = enabled
        self._fail_count = 0

    def update_value(self, regs):
        if regs is None:
            self._fail_count += 1
            return
        try:
            raw_value = 0
            for reg in regs:
                raw_value = (raw_value << 16) + reg

            if self.data_type == "int16":
                raw_value = (raw_value + 2**15) % 2**16 - 2**15
            elif self.data_type == "int32":
                raw_value = (raw_value + 2**31) % 2**32 - 2**31

            self._attr_native_value = round(raw_value * self.scale, 2)
        except Exception as e:
            _LOGGER.error("%s decode failed: %s", self._attr_name, e)


# ----------------------------- String Sensor -----------------------------
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


# ----------------------------- Init Sensoren -----------------------------
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

                        if self._attr_name == "FoxESS Model Name":
                            BaseModbusSensor._device_info_data["model"] = value
                        elif self._attr_name == "FoxESS Serial Number":
                            BaseModbusSensor._device_info_data["serial"] = value
                        elif self._attr_name == "FoxESS Manufacturer ID":
                            BaseModbusSensor._device_info_data["manufacturer"] = value

                        self.async_write_ha_state()

        except Exception as e:
            _LOGGER.error("%s initial read failed: %s", self._attr_name, e)