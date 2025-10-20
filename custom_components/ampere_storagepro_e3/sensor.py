import logging
import asyncio
from datetime import timedelta
from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.event import async_track_time_interval
from pymodbus.client import AsyncModbusTcpClient

_LOGGER = logging.getLogger(__name__)
DOMAIN = "ampere_storagepro_e3"

# ------------------------------------------------------------
# Hilfsfunktion: Sichere Modbus-Lesung mit persistentem Client
# ------------------------------------------------------------
class ModbusConnection:
    """Verwaltet eine stabile Modbus-Verbindung."""

    def __init__(self, host, port, timeout=5):
        self.host = host
        self.port = port
        self.timeout = timeout
        self.client = None
        self.lock = asyncio.Lock()

    async def connect(self):
        """Stellt sicher, dass der Client verbunden ist."""
        async with self.lock:
            if self.client is None or not self.client.connected:
                self.client = AsyncModbusTcpClient(self.host, port=self.port, timeout=self.timeout)
                await self.client.connect()
                if self.client.connected:
                    _LOGGER.info("Mit Modbus verbunden: %s:%s", self.host, self.port)
                else:
                    _LOGGER.warning("Verbindung zu %s:%s fehlgeschlagen", self.host, self.port)

    async def read(self, slave, address, count):
        """Liest Register mit automatischem Reconnect bei Fehler."""
        try:
            await self.connect()
            if not self.client.connected:
                return None

            rr = await asyncio.wait_for(
                self.client.read_input_registers(address, count=count, slave=slave),
                timeout=self.timeout + 2,
            )
            if rr.isError():
                _LOGGER.warning("Fehlerhafte Antwort bei Adresse %s", address)
                return None
            return rr.registers
        except asyncio.TimeoutError:
            _LOGGER.error("Timeout beim Lesen von %s", address)
            return None
        except Exception as e:
            _LOGGER.error("Fehler bei Modbus-Lesung %s: %s", address, e)
            return None


# ------------------------------------------------------------
# Sensor-Definition
# ------------------------------------------------------------
class ModbusSensor(SensorEntity):
    """Modbus Sensor mit stabiler Verbindung."""

    _attr_should_poll = False

    def __init__(self, hass, conn, slave, name, address, count, scale, unit, interval, data_type="uint16"):
        self.hass = hass
        self.conn = conn
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

    async def async_added_to_hass(self):
        _LOGGER.info("%s: Starte Updates alle %ss", self._attr_name, self._interval)
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
            _LOGGER.error("%s: Fehler beim Update: %s", self._attr_name, e)

    async def async_update(self):
        regs = await self.conn.read(self.slave, self.address, self.count)
        if regs:
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
            self.async_write_ha_state()
            _LOGGER.debug(
                "Sensor %s aktualisiert: %s %s",
                self._attr_name,
                self._attr_native_value,
                self._attr_native_unit_of_measurement,
            )
        else:
            self._available = False
            _LOGGER.warning("Sensor %s: Keine Daten empfangen", self._attr_name)


# ------------------------------------------------------------
# Setup: Verbindung & Sensoren initialisieren
# ------------------------------------------------------------
async def async_setup_entry(hass, entry, async_add_entities):
    host = entry.data.get("host", "127.0.0.1")
    port = entry.data.get("port", 1502)
    slave = entry.data.get("slave_id", 247)
    update_interval = entry.options.get("update_interval", 30)
    _LOGGER.info("Ampere StoragePro E3: Update-Intervall = %ss", update_interval)

    conn = ModbusConnection(host, port)

    sensors = [
        ModbusSensor(hass, conn, slave, "FoxESS Today Total Charging Capacity", 39607, 2, 0.01, "kWh", update_interval, "uint32"),
        ModbusSensor(hass, conn, slave, "FoxESS PV Power Total", 39601, 2, 0.01, "kWh", update_interval, "uint32"),
        ModbusSensor(hass, conn, slave, "FoxESS PV Power Today", 39603, 2, 0.01, "kWh", update_interval, "uint32"),
        ModbusSensor(hass, conn, slave, "FoxESS Total Charging Capacity", 39605, 2, 0.01, "kWh", update_interval, "uint32"),
        ModbusSensor(hass, conn, slave, "FoxESS Charge Discharge Power", 39612, 2, 0.1, "W", update_interval, "uint32"),
        ModbusSensor(hass, conn, slave, "FoxESS BMS1 SoC", 37612, 1, 1, "%", update_interval, "uint16"),
    ]

    async_add_entities(sensors)
    _LOGGER.info("Ampere StoragePro E3: Sensoren erfolgreich registriert.")