import voluptuous as vol
from homeassistant import config_entries
from .const import DOMAIN

class AmpereStorageProE3ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Config Flow für Ampere StoragePro E3."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(title="Ampere StoragePro E3", data=user_input)

        schema = vol.Schema({
            vol.Required("host"): str,
            vol.Required("port", default=502): int,
            vol.Required("slave_id", default=1): int,
        })

        return self.async_show_form(step_id="user", data_schema=schema)