"""DataUpdateCoordinator für die Ampere StoragePro E3 Integration."""
from __future__ import annotations

import asyncio
import logging
from datetime import timedelta
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from pymodbus.client import AsyncModbusTcpClient

from .bit_definitions import BIT_TEXTS
from .const import DEFAULT_INTERVAL, DOMAIN
from .sensors import SENSOR_DEFINITIONS

_LOGGER = logging.getLogger(__name__)

_MAX_REGS_PER_BATCH = 120  # Maximal 120 Register pro Batch

# Holding-Register (0x03/0x06), deren Ist-Wert für Steuer-Entitäten gelesen wird
_CONTROL_REGISTERS = (49203, 49209, 49221)  # Work mode, Buzzer, Brightness


# ----------------------------- Dekodier-Helfer -----------------------------
def _decode_string(regs: list[int]) -> str | None:
    """Register als ASCII-String dekodieren."""
    if not regs:
        return None
    raw_bytes = b"".join(reg.to_bytes(2, "big") for reg in regs)
    return raw_bytes.decode("ascii", errors="ignore").strip("\x00").strip()


def _decode_bits(reg: int, bit_count: int, name: str) -> str:
    """Bit-Register in Klartext übersetzen (nutzt BIT_TEXTS, sonst generisch)."""
    active_bits = [bit for bit in range(bit_count) if reg & (1 << bit)]

    if name in BIT_TEXTS:
        mapping = BIT_TEXTS[name]
        text_list = [mapping.get(b, f"Bit {b}") for b in active_bits]
        return ", ".join(text_list) if text_list else "OK"

    return ", ".join(f"Bit{b}" for b in active_bits) if active_bits else "OK"


def _decode_number(regs: list[int], data_type: str, scale: float) -> float:
    """uint16/int16/uint32/int32 dekodieren und skalieren."""
    raw_value = 0
    for reg in regs:
        raw_value = (raw_value << 16) + reg

    if data_type == "int16":
        raw_value = (raw_value + 2**15) % 2**16 - 2**15
    elif data_type == "int32":
        raw_value = (raw_value + 2**31) % 2**32 - 2**31

    return round(raw_value * scale, 2)


def _decode_definition(sd: tuple, regs: list[int]) -> Any:
    """Eine Sensor-Definition anhand der gelesenen Register dekodieren."""
    name, _addr, _count, scale, _unit, dtype, _cat, _dc, _en, _vis = sd
    regs = [r if r is not None else 0 for r in regs]

    if dtype == "str":
        return _decode_string(regs)
    if dtype.startswith("bit"):
        bit_count = int(dtype.replace("bit", ""))
        return _decode_bits(regs[0], bit_count, name)
    # Leerer dtype -> wie bisher als unsigned-Zahl behandeln
    return _decode_number(regs, dtype, scale)


# ----------------------------- Batch-Bildung -----------------------------
def create_batches(definitions: list[tuple]) -> list[tuple[int, int, list[tuple]]]:
    """Sensor-Definitionen in zusammenhängende Lesebatches gruppieren.

    Ein Batch endet bei einer Adress-Lücke oder beim Überschreiten von
    _MAX_REGS_PER_BATCH Registern.
    """
    defs_sorted = sorted(definitions, key=lambda sd: sd[1])  # nach Adresse
    batches: list[tuple[int, int, list[tuple]]] = []
    current: list[tuple] = []
    batch_start: int | None = None
    batch_end: int | None = None

    for sd in defs_sorted:
        addr = sd[1]
        count = sd[2]
        sensor_end = addr + count - 1

        if batch_start is None:
            batch_start, batch_end, current = addr, sensor_end, [sd]
            continue

        if addr > batch_end + 1 or (sensor_end - batch_start + 1) > _MAX_REGS_PER_BATCH:
            batches.append((batch_start, batch_end, current))
            batch_start, batch_end, current = addr, sensor_end, [sd]
        else:
            batch_end = max(batch_end, sensor_end)
            current.append(sd)

    if current:
        batches.append((batch_start, batch_end, current))

    return batches


# ----------------------------- Coordinator -----------------------------
class AmpereStorageProE3Coordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Hält die Modbus-Verbindung und pollt alle Register zentral."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        self.host: str = entry.data["host"]
        self.port: int = entry.data["port"]
        self.slave: int = entry.data["slave_id"]

        interval = entry.options.get("update_interval", DEFAULT_INTERVAL)

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=interval),
        )

        self._client: AsyncModbusTcpClient | None = None
        # pymodbus benannte den Slave-Parameter um: 3.x = "slave", 4.x = "device_id".
        # Wird beim ersten erfolgreichen Aufruf ermittelt und gemerkt.
        self._slave_kwarg: str | None = None
        # Serialisiert alle Modbus-IO (Polling + Schreibvorgänge) auf der
        # gemeinsamen, persistenten Verbindung.
        self._io_lock = asyncio.Lock()
        self._batches = create_batches(SENSOR_DEFINITIONS)
        self.device_info_data: dict[str, str | None] = {
            "model": None,
            "serial": None,
            "manufacturer": None,
        }
        self.connected_flags: dict[str, int | None] = {
            "bms1": None,
            "bms2": None,
            "meter1": None,
            "meter2": None,
        }

    # -- Verbindung -------------------------------------------------------
    async def _ensure_connected(self) -> AsyncModbusTcpClient:
        """Stellt sicher, dass eine offene Verbindung existiert."""
        if self._client is None:
            self._client = AsyncModbusTcpClient(host=self.host, port=self.port)
        if not self._client.connected:
            await self._client.connect()
        if not self._client.connected:
            raise UpdateFailed(f"Keine Verbindung zu {self.host}:{self.port}")
        return self._client

    async def _call_read(self, client: AsyncModbusTcpClient, start: int, count: int):
        """read_input_registers mit dem passenden slave/device_id-Keyword."""
        if self._slave_kwarg is not None:
            return await client.read_input_registers(
                address=start, count=count, **{self._slave_kwarg: self.slave}
            )
        # Erstaufruf: device_id (pymodbus >=4) bevorzugen, sonst slave (3.x)
        try:
            result = await client.read_input_registers(
                address=start, count=count, device_id=self.slave
            )
        except TypeError:
            result = await client.read_input_registers(
                address=start, count=count, slave=self.slave
            )
            self._slave_kwarg = "slave"
        else:
            self._slave_kwarg = "device_id"
        return result

    async def _read_block(
        self, client: AsyncModbusTcpClient, start: int, count: int, timeout: int = 5
    ) -> list[int] | None:
        """Einen Registerblock lesen (Input Register)."""
        try:
            rr = await asyncio.wait_for(
                self._call_read(client, start, count), timeout=timeout
            )
        except Exception as err:  # noqa: BLE001
            _LOGGER.debug("Fehler beim Lesen von Adresse %s: %s", start, err)
            return None
        if rr.isError():
            _LOGGER.debug("Modbus-Fehler beim Lesen von Adresse %s", start)
            return None
        return rr.registers

    # -- Holding-Register (0x03 / 0x06 / 0x10) ----------------------------
    async def _call_with_slave(self, func, **kwargs):
        """Modbus-Aufruf mit dem passenden slave/device_id-Keyword (3.x/4.x)."""
        if self._slave_kwarg is not None:
            return await func(**kwargs, **{self._slave_kwarg: self.slave})
        try:
            result = await func(**kwargs, device_id=self.slave)
        except TypeError:
            result = await func(**kwargs, slave=self.slave)
            self._slave_kwarg = "slave"
        else:
            self._slave_kwarg = "device_id"
        return result

    async def _read_holding(
        self, client: AsyncModbusTcpClient, address: int, count: int = 1, timeout: int = 5
    ) -> list[int] | None:
        """Holding-Register lesen (0x03)."""
        try:
            rr = await asyncio.wait_for(
                self._call_with_slave(
                    client.read_holding_registers, address=address, count=count
                ),
                timeout=timeout,
            )
        except Exception as err:  # noqa: BLE001
            _LOGGER.debug("Fehler beim Holding-Read %s: %s", address, err)
            return None
        if rr.isError():
            _LOGGER.debug("Modbus-Fehler beim Holding-Read %s", address)
            return None
        return rr.registers

    async def async_write_holding(self, address: int, value: int) -> None:
        """Einzelnes Holding-Register schreiben (0x06) und danach aktualisieren."""
        async with self._io_lock:
            client = await self._ensure_connected()
            rr = await self._call_with_slave(
                client.write_register, address=address, value=int(value)
            )
            if rr.isError():
                raise HomeAssistantError(
                    f"Schreiben auf Register {address} fehlgeschlagen"
                )
        await self.async_request_refresh()

    async def async_write_holding_block(
        self, address: int, values: list[int]
    ) -> None:
        """Mehrere aufeinanderfolgende Holding-Register schreiben (0x10)."""
        async with self._io_lock:
            client = await self._ensure_connected()
            rr = await self._call_with_slave(
                client.write_registers,
                address=address,
                values=[int(v) for v in values],
            )
            if rr.isError():
                raise HomeAssistantError(
                    f"Schreiben ab Register {address} fehlgeschlagen"
                )
        await self.async_request_refresh()

    # -- Einmaliges Setup -------------------------------------------------
    async def _async_setup(self) -> None:
        """Einmalig vor dem ersten Refresh: Geräte-Info + Connect-Flags."""
        client = await self._ensure_connected()

        model = await self._read_block(client, 30000, 16)
        serial = await self._read_block(client, 30016, 16)
        manufacturer = await self._read_block(client, 30032, 16)

        self.device_info_data = {
            "model": _decode_string(model) if model else None,
            "serial": _decode_string(serial) if serial else None,
            "manufacturer": _decode_string(manufacturer) if manufacturer else None,
        }

        for key, addr in (
            ("bms1", 37002),
            ("bms2", 37700),
            ("meter1", 38801),
            ("meter2", 38901),
        ):
            regs = await self._read_block(client, addr, 1)
            self.connected_flags[key] = regs[0] if regs else None

        _LOGGER.debug(
            "Setup: device_info=%s, connected=%s",
            self.device_info_data,
            self.connected_flags,
        )

    # -- Periodisches Update ---------------------------------------------
    async def _async_update_data(self) -> dict[str, Any]:
        """Alle Batches lesen und dekodieren."""
        data: dict[str, Any] = {}
        read_any = False

        async with self._io_lock:
            client = await self._ensure_connected()

            for start, end, defs in self._batches:
                count = end - start + 1
                regs = await self._read_block(client, start, count)
                if regs is None:
                    continue
                read_any = True
                for sd in defs:
                    addr, sd_count = sd[1], sd[2]
                    start_idx = addr - start
                    end_idx = start_idx + sd_count
                    if start_idx < 0 or end_idx > len(regs):
                        continue
                    try:
                        data[sd[0]] = _decode_definition(sd, regs[start_idx:end_idx])
                    except Exception as err:  # noqa: BLE001
                        _LOGGER.debug("Dekodierfehler für %s: %s", sd[0], err)

            if not read_any:
                raise UpdateFailed("Kein einziger Registerblock konnte gelesen werden")

            # Steuer-Register (Holding) lesen – Fehler hier sind nicht fatal,
            # die jeweilige Steuer-Entität wird dann nur "unavailable".
            for addr in _CONTROL_REGISTERS:
                regs = await self._read_holding(client, addr, 1)
                if regs:
                    data[f"ctrl_{addr}"] = regs[0]

        return data

    # -- Aufräumen --------------------------------------------------------
    async def async_shutdown_client(self) -> None:
        """Verbindung schließen (beim Unload)."""
        if self._client is not None:
            self._client.close()
            self._client = None


def ampere_device_info(coordinator: AmpereStorageProE3Coordinator) -> dict[str, Any]:
    """Gemeinsame DeviceInfo für alle Plattformen dieser Integration."""
    info = coordinator.device_info_data
    ident = f"{coordinator.host}_{coordinator.port}_{coordinator.slave}"
    return {
        "identifiers": {(DOMAIN, ident)},
        "name": "Ampere StoragePro E3",
        "manufacturer": info.get("manufacturer") or "Ampere",
        "model": info.get("model") or "FoxESS",
        "serial_number": info.get("serial") or "N/A",
    }
