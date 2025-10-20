import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from .const import DOMAIN

DEFAULT_INTERVAL = 30

# ConfigFlow
class AmpereStorageProE3ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Ampere StoragePro E3."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(
                title=f"Ampere StoragePro E3 ({user_input['host']})",
                data=user_input,
                options={"update_interval": DEFAULT_INTERVAL},
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

# OptionsFlow
class AmpereStorageProE3OptionsFlowHandler(config_entries.OptionsFlow):
    """Handle options for Ampere StoragePro E3."""

    def __init__(self, config_entry: config_entries.ConfigEntry):
        """HA übergibt den ConfigEntry, muss aber NICHT gespeichert werden."""
        super().__init__()

    async def async_step_init(self, user_input=None):
        """Manage the options."""
        # Hier HA-internes self.config_entry verwenden, das automatisch gesetzt wird
        options = self.config_entry.options
        current_interval = options.get("update_interval", DEFAULT_INTERVAL)

        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        schema = vol.Schema({
            vol.Required(
                "update_interval",
                default=current_interval
            ): vol.In([10, 30, 60, 120])
        })

        return self.async_show_form(step_id="init", data_schema=schema)