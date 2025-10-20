import logging
import asyncio
from datetime import timedelta
from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.event import async_track_time_interval
from pymodbus.client import AsyncModbusTcpClient

_LOGGER = logging.getLogger(__name__)
DOMAIN = "ampere_storagepro_e3"


# ------------------------------------------------------------
# Sichere Modbus-Lesung mit automatischer Verbindung + Fallback
# ------------------------------------------------------------
async def safe_read(host, port, slave, address, count, timeout=5):
    """Liest Modbus-Register sicher mit Kompatibilität zu verschiedenen pymodbus-Versionen."""
    client = AsyncModbusTcpClient(host, port=port, timeout=timeout)
    try:
        await client.connect()
        if not client.connected:
            _LOGGER.error("Keine Verbindung zu %s:%s", host, port)
            return None

        # Erster Versuch: device_id (ältere pymodbus-Versionen)
        try:
            rr = await asyncio.wait_for(
                client.read_input_registers(address, count=count, device_id=slave),
                timeout=timeout + 2,
            )
        except TypeError:
            # Fallback: unit (neuere pymodbus-Versionen)
            rr = await asyncio.wait_for(
                client.read_input_registers(address, count=count, unit=slave),
                timeout=timeout + 2,
            )

        if rr is None or rr.isError():
            _LOGGER.warning("Fehlerhafte Modbus-Antwort bei Adresse %s", address)
            return None

        return rr.registers

    except asyncio.TimeoutError:
        _LOGGER.error("Timeout beim Lesen von %s", address)
        return None
    except Exception as e:
        _LOGGER.error("Fehler bei Modbus-Lesung %s: %s", address, e)
        return None
    finally:
        await client.close()


# ------------------------------------------------------------
# Sensor-Definition
# ------------------------------------------------------------
class ModbusSensor(SensorEntity):
    """Ein sicherer Modbus Sensor mit automatischer Wiederverbindung."""

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
        self._fail_count = 0  # Zählt aufeinanderfolgende Fehler

    async def async_added_to_hass(self):
        """Starte periodische Updates."""
        _LOGGER.info("%s: Starte Updates alle %ss", self._attr_name, self._interval)
        self._unsub_timer = async_track_time_interval(
            self.hass, self.async_update_wrapper, timedelta(seconds=self._interval)
        )

    async def async_will_remove_from_hass(self):
        """Stoppe Timer beim Entfernen."""
        if self._unsub_timer:
            self._unsub_timer()
            self._unsub_timer = None

    async def async_update_wrapper(self, now):
        """Wrapper mit Fehlerbehandlung."""
        try:
            await self.async_update()
        except Exception as e:
            _LOGGER.error("%s: Fehler beim Update: %s", self._attr_name, e)

    async def async_update(self):
        """Haupt-Update-Funktion."""
        regs = await safe_read(self.host, self.port, self.slave, self.address, self.count)
        if regs:
            # Register in 16-Bit-Schritten zu 32-Bit zusammenfügen
            raw_value = 0
            for reg in regs:
                raw_value = (raw_value << 16) + reg

            # Datentyp korrekt interpretieren
            if self.data_type == "int32" and raw_value >= 0x80000000:
                raw_value -= 0x100000000
            elif self.data_type == "int16" and raw_value >= 0x8000:
                raw_value -= 0x10000

            self._attr_native_value = round(raw_value * self.scale, 2)
            self._available = True
            self._fail_count = 0
            self.async_write_ha_state()
            _LOGGER.debug(
                "Sensor %s aktualisiert: %s %s",
                self._attr_name,
                self._attr_native_value,
                self._attr_native_unit_of_measurement,
            )
        else:
            self._fail_count += 1
            self._available = False
            if self._fail_count % 5 == 0:  # Nur alle 5 Fehlschläge warnen
                _LOGGER.warning("Sensor %s: Keine Daten empfangen (%d Fehler in Folge)", self._attr_name, self._fail_count)


# ------------------------------------------------------------
# Setup der Sensoren
# ------------------------------------------------------------
async def async_setup_entry(hass, entry, async_add_entities):
    """Initialisiert Sensoren für die Integration."""
    host = entry.data.get("host", "127.0.0.1")
    port = entry.data.get("port", 502)
    slave = entry.data.get("slave_id", 247)
    update_interval = entry.options.get("update_interval", 30)
    _LOGGER.info("Ampere StoragePro E3: Update-Intervall = %ss", update_interval)

    sensors = [
        ModbusSensor(hass, host, port, slave, "FoxESS Today Total Charging Capacity", 39607, 2, 0.01, "kWh", update_interval, "uint32"),
        ModbusSensor(hass, host, port, slave, "FoxESS PV Power Total", 39601, 2, 0.01, "kWh", update_interval, "uint32"),
        ModbusSensor(hass, host, port, slave, "FoxESS PV Power Today", 39603, 2, 0.01, "kWh", update_interval, "uint32"),
        ModbusSensor(hass, host, port, slave, "FoxESS Total Charging Capacity", 39605, 2, 0.01, "kWh", update_interval, "uint32"),
        ModbusSensor(hass, host, port, slave, "FoxESS Charge Discharge Power", 39612, 2, 0.1, "W", update_interval, "uint32"),
        ModbusSensor(hass, host, port, slave, "FoxESS BMS1 SoC", 37612, 1, 1, "%", update_interval, "uint16"),
    ]

    async_add_entities(sensors)
    _LOGGER.info("Ampere StoragePro E3: Sensoren erfolgreich registriert.")