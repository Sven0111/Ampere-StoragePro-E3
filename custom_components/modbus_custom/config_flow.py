import voluptuous as vol
from homeassistant import config_entries
from .const import DOMAIN

class ModbusCustomConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_LOCAL_POLL

    async def async_step_user(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(title="Modbus Gerät", data=user_input)

        data_schema = vol.Schema({
            vol.Required("host"): str,
            vol.Required("port", default=502): int,
            vol.Required("slave_id", default=1): int
        })
        return self.async_show_form(step_id="user", data_schema=data_schema)