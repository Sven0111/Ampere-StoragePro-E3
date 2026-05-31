import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from pymodbus.client import AsyncModbusTcpClient
from .const import DOMAIN, DEFAULT_INTERVAL
import asyncio
import logging

_LOGGER = logging.getLogger(__name__)

# ------------------ Hilfsfunktionen ------------------

async def _read_input_registers(client, slave, address, count):
    """read_input_registers mit dem passenden slave/device_id-Keyword.

    pymodbus benannte den Parameter um: 3.x = "slave", 4.x = "device_id".
    Erst device_id versuchen, bei TypeError auf slave zurueckfallen.
    """
    try:
        return await client.read_input_registers(
            address=address, count=count, device_id=slave
        )
    except TypeError:
        return await client.read_input_registers(
            address=address, count=count, slave=slave
        )


async def read_ascii_registers(client, slave, address, count):
    """Liest eine Reihe Modbus-Register und dekodiert ASCII."""
    try:
        rr = await asyncio.wait_for(
            _read_input_registers(client, slave, address, count),
            timeout=5,
        )
        if rr.isError():
            _LOGGER.warning("Modbus error reading address %s", address)
            return None
        raw_bytes = b"".join(reg.to_bytes(2, "big") for reg in rr.registers)
        return raw_bytes.decode("ascii", errors="ignore").strip("\x00").strip()
    except Exception as e:
        _LOGGER.warning("Exception reading address %s: %s", address, e)
        return None

async def read_device_info(host, port, slave):
    """Liest Modell, Seriennummer und Hersteller-ID aus."""
    info = {"model": None, "serial": None, "manufacturer": None}
    try:
        async with AsyncModbusTcpClient(host=host, port=port) as client:
            if not client.connected:
                _LOGGER.warning("Keine Verbindung zu %s:%s", host, port)
                return info

            info["model"] = await read_ascii_registers(client, slave, 30000, 16)
            info["serial"] = await read_ascii_registers(client, slave, 30016, 16)
            info["manufacturer"] = await read_ascii_registers(client, slave, 30032, 16)

            _LOGGER.debug("Device info read: %s", info)

    except Exception as e:
        _LOGGER.warning("Geräteinfo konnte nicht gelesen werden: %s", e)
    return info

# ------------------ Config Flow ------------------

class AmpereStorageProE3ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle config flow."""
    VERSION = 1

    async def async_step_user(self, user_input=None):
        _LOGGER.debug("Starting async_step_user with input: %s", user_input)

        errors = {}

        if user_input is not None:
            info = await read_device_info(
                user_input["host"],
                user_input["port"],
                user_input["slave_id"],
            )

            _LOGGER.debug(
                "ConfigFlow read_device_info result: model=%s, serial=%s, manufacturer=%s",
                info["model"], info["serial"], info["manufacturer"]
            )

            # Konnte das Geraet nicht erreicht/identifiziert werden, abbrechen
            # statt einen unbrauchbaren Eintrag anzulegen.
            if not info["model"] and not info["serial"]:
                errors["base"] = "cannot_connect"
            else:
                # Eindeutige ID, damit dasselbe Geraet nicht doppelt
                # eingerichtet werden kann. Seriennummer bevorzugt,
                # sonst Host/Port/Slave als Fallback.
                unique_id = info["serial"] or (
                    f"{user_input['host']}_{user_input['port']}_{user_input['slave_id']}"
                )
                await self.async_set_unique_id(unique_id)
                self._abort_if_unique_id_configured()

                title = f"{info['model'] or 'Ampere StoragePro E3'} ({user_input['host']})"

                # Im Config-Entry speichern
                user_input["model_name"] = info["model"]
                user_input["serial_number"] = info["serial"]
                user_input["manufacturer"] = info["manufacturer"]

                return self.async_create_entry(
                    title=title,
                    data=user_input,
                    options={
                        "update_interval": DEFAULT_INTERVAL,
                        "enable_diagnostics": True,
                    },
                )

        schema = vol.Schema({
            vol.Required("host", default="127.0.0.1"): str,
            vol.Required("port", default=502): int,
            vol.Required("slave_id", default=247): int,
        })
        return self.async_show_form(
            step_id="user", data_schema=schema, errors=errors
        )

    async def async_step_reconfigure(self, user_input=None):
        """Host/Port/Slave-ID einer bestehenden Integration aendern."""
        entry = self._get_reconfigure_entry()
        errors = {}

        if user_input is not None:
            info = await read_device_info(
                user_input["host"],
                user_input["port"],
                user_input["slave_id"],
            )

            if not info["model"] and not info["serial"]:
                errors["base"] = "cannot_connect"
            else:
                return self.async_update_reload_and_abort(
                    entry,
                    data_updates={
                        "host": user_input["host"],
                        "port": user_input["port"],
                        "slave_id": user_input["slave_id"],
                        "model_name": info["model"],
                        "serial_number": info["serial"],
                        "manufacturer": info["manufacturer"],
                    },
                )

        schema = vol.Schema({
            vol.Required("host", default=entry.data["host"]): str,
            vol.Required("port", default=entry.data["port"]): int,
            vol.Required("slave_id", default=entry.data["slave_id"]): int,
        })
        return self.async_show_form(
            step_id="reconfigure", data_schema=schema, errors=errors
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return AmpereStorageProE3OptionsFlowHandler()


# ------------------ Options Flow ------------------

class AmpereStorageProE3OptionsFlowHandler(config_entries.OptionsFlow):
    """Handle options."""

    async def async_step_init(self, user_input=None):
        options = self.config_entry.options
        current_interval = options.get("update_interval", DEFAULT_INTERVAL)
        current_diag = options.get("enable_diagnostics", True)

        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        schema = vol.Schema({
            vol.Required("update_interval", default=current_interval): vol.In([10, 30, 60, 120]),
            vol.Optional("enable_diagnostics", default=current_diag): bool,
        })
        return self.async_show_form(step_id="init", data_schema=schema)