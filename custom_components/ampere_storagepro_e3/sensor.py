import asyncio
import logging

from homeassistant.helpers.entity import SensorEntity
from pymodbus.client import AsyncModbusTcpClient

_LOGGER = logging.getLogger(__name__)

DOMAIN = "ampere_storagepro_e3"

# ========================
# Setup Entry
# ========================
async def async_setup_entry(hass, entry, async_add_entities):
    """Set up sensors for Ampere StoragePro E3 via Modbus TCP."""
    _LOGGER.info("Ampere StoragePro E3: Setup Entry gestartet für %s:%s", host, port)
    host = entry.data.get("host")
    port = entry.data.get("port", 502)
    slave = entry.data.get("slave_id", 1)

    device = ModbusDevice(host, port, slave)

    sensors = [
        ModbusSensor(device, "kWh Gesamt", 39607, 2, 0.01, "kWh"),
        # Weitere Sensoren hier hinzufügen
    ]

    # Speicher Device & Sensoren für Unload
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = {
        "device": device,
        "sensors": sensors,
    }

    try:
        async_add_entities(sensors, update_before_add=True)
        _LOGGER.info("Ampere StoragePro E3: Sensoren hinzugefügt: %s", [s._attr_name for s in sensors])
        return True
    except Exception as e:
        _LOGGER.error("Fehler beim Hinzufügen der Sensoren: %s", e)
        return False

async def async_unload_entry(hass, entry):
    """Unload sensors and cleanup."""
    data = hass.data.get(DOMAIN, {}).pop(entry.entry_id, None)
    if not data:
        _LOGGER.warning("Config Entry %s wurde nie geladen.", entry.entry_id)
        return True

    device = data.get("device")
    if device and device.client:
        try:
            await device.client.close()
        except Exception as e:
            _LOGGER.error("Fehler beim Schließen der Modbus-Verbindung: %s", e)

    return True

# ========================
# Modbus Device
# ========================
class ModbusDevice:
    def __init__(self, host, port, slave):
        self.host = host
        self.port = port
        self.slave = slave
        self.client = None
        self.lock = asyncio.Lock()

    async def connect(self):
        """Create a Modbus TCP connection if not connected."""
        if not self.client:
            try:
                self.client = AsyncModbusTcpClient(self.host, port=self.port)
                await asyncio.sleep(0.1)  # Delay, um Verbindung aufzubauen
            except Exception as e:
                _LOGGER.error(
                    "Fehler beim Verbinden mit Modbus-Gerät %s:%s - %s",
                    self.host,
                    self.port,
                    e,
                )
                self.client = None

    async def read_registers(self, address, count):
        """Read Modbus input registers safely."""
        async with self.lock:
            await self.connect()
            if not self.client:
                return None
            try:
                rr = await self.client.read_input_registers(address, count, slave=self.slave)
                return rr.registers if rr and rr.registers else None
            except Exception as e:
                _LOGGER.error("Fehler beim Lesen der Register %s: %s", address, e)
                return None

# ========================
# Sensor Entity
# ========================
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
        """Update sensor value from Modbus device."""
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
            _LOGGER.error("Fehler beim Aktualisieren von Sensor %s: %s", self._attr_name, e)
            self._attr_native_value = None