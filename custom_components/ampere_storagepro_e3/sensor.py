import asyncio
import logging
from homeassistant.components.sensor import SensorEntity
from pymodbus.client import AsyncModbusTcpClient

_LOGGER = logging.getLogger(__name__)
DOMAIN = "ampere_storagepro_e3"

# =====================================================
# Modbus-Gerät
# =====================================================
class ModbusDevice:
    """Verwaltet die Modbus-TCP-Verbindung."""

    def __init__(self, host, port, slave):
        self.host = host
        self.port = port
        self.slave = slave  # nur dokumentarisch
        self.client: AsyncModbusTcpClient | None = None
        self.lock = asyncio.Lock()

    async def connect(self):
        """Stellt sicher, dass der Client initialisiert ist."""
        if not self.client:
            self.client = AsyncModbusTcpClient(self.host, port=self.port)
            await self.client.connect()

        if self.client and self.client.connected:
            _LOGGER.info("Verbindung zu Modbus-Gerät %s:%s erfolgreich", self.host, self.port)
        else:
            _LOGGER.warning("Keine Verbindung zu Modbus-Gerät %s:%s", self.host, self.port)

    async def read_registers(self, address, count):
        """Liest Input-Register in PyModbus 3.11.3 ohne 'unit'."""
        async with self.lock:
            if not self.client:
                await self.connect()

            if not self.client or not self.client.connected:
                _LOGGER.warning("Modbus-Client nicht verbunden (%s:%s).", self.host, self.port)
                return None

            try:
                rr = await self.client.read_input_registers(address, count)
                if rr is None or rr.isError():
                    _LOGGER.warning("Leere oder fehlerhafte Antwort bei Adresse %s", address)
                    return None
                return rr.registers
            except Exception as e:
                _LOGGER.error("Fehler beim Lesen der Register %s: %s", address, e)
                return None

# =====================================================
# Sensor-Entität
# =====================================================
class ModbusSensor(SensorEntity):
    """Ein einzelner Modbus-Sensor."""

    def __init__(self, device, name, address, count, scale, unit):
        self.device = device
        self._attr_name = name
        self.address = address
        self.count = count
        self.scale = scale
        self._attr_native_value = None
        self._attr_native_unit_of_measurement = unit

    async def async_update(self):
        """Liest die aktuellen Werte vom Gerät."""
        try:
            regs = await self.device.read_registers(self.address, self.count)
            if regs:
                raw_value = 0
                for reg in regs:
                    raw_value = (raw_value << 16) + reg
                self._attr_native_value = round(raw_value * self.scale, 2)
            else:
                self._attr_native_value = None
        except Exception as e:
            _LOGGER.error("Fehler beim Aktualisieren von Sensor %s: %s", self._attr_name, e)
            self._attr_native_value = None

# =====================================================
# Setup der Plattform
# =====================================================
async def async_setup_entry(hass, entry, async_add_entities):
    """Set up Ampere StoragePro E3 sensors via Modbus TCP."""
    host = entry.data.get("host", "127.0.0.1")
    port = entry.data.get("port", 1502)
    slave = entry.data.get("slave_id", 247)  # nur dokumentarisch

    _LOGGER.info(
        "Ampere StoragePro E3: Initialisiere Verbindung zu %s:%s (Slave %s)",
        host, port, slave
    )
    device = ModbusDevice(host, port, slave)

    sensors = [
        ModbusSensor(device, "kWh Gesamt", 39607, 2, 0.01, "kWh"),
    ]

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = {"device": device, "sensors": sensors}
    async_add_entities(sensors, update_before_add=True)

    _LOGGER.info("Ampere StoragePro E3: %d Sensor(en) hinzugefügt", len(sensors))
    return True