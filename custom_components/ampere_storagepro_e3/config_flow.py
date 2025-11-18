import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from pymodbus.client import AsyncModbusTcpClient
from .const import DOMAIN, DEFAULT_INTERVAL
import asyncio
import logging

_LOGGER = logging.getLogger(__name__)

# ------------------ Hilfsfunktionen ------------------

async def read_ascii_registers(client, slave, address, count):
    """Liest eine Reihe Modbus-Register und dekodiert ASCII."""
    try:
        rr = await asyncio.wait_for(
            client.read_input_registers(address=address, count=count, slave=slave),
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
            info["manufacturer"] = await read_ascii_registers(client, slave, 30032, 8)

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
        return self.async_show_form(step_id="user", data_schema=schema)

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return AmpereStorageProE3OptionsFlowHandler(config_entry)


# ------------------ Options Flow ------------------

class AmpereStorageProE3OptionsFlowHandler(config_entries.OptionsFlow):
    """Handle options."""

    def __init__(self, config_entry: config_entries.ConfigEntry):
        self.config_entry = config_entry

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