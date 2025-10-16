import voluptuous as vol
from homeassistant import config_entries
from .const import DOMAIN

class AmpereStorageProConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """UI Config Flow für Modbus TCP."""
    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_LOCAL_POLL

    async def async_step_user(self, user_input=None):
        errors = {}

        if user_input is not None:
            host = user_input.get("host")
            port = user_input.get("port")
            slave_id = user_input.get("slave_id")

            if not host:
                errors["host"] = "Host erforderlich"
            if not port:
                errors["port"] = "Port erforderlich"
            if not slave_id:
                errors["slave_id"] = "Slave-ID erforderlich"

            if not errors:
                return self.async_create_entry(title=f"Modbus {host}", data=user_input)

        data_schema = vol.Schema(
            {
                vol.Required("host", default="192.168.1.100"): str,
                vol.Required("port", default=502): int,
                vol.Required("slave_id", default=1): int,
            }
        )
        return self.async_show_form(step_id="user", data_schema=data_schema, errors=errors)