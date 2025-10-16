import voluptuous as vol
from homeassistant import config_entries
from .const import DOMAIN

# Minimaler, funktionierender Config Flow
class ModbusCustomConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow für Modbus Custom Integration."""
    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_LOCAL_POLL

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            # Prüfen, dass alle Werte gesetzt sind
            host = user_input.get("host")
            port = user_input.get("port")
            slave_id = user_input.get("slave_id")

            if not host:
                errors["host"] = "Host muss gesetzt sein"
            if not port:
                errors["port"] = "Port muss gesetzt sein"
            if not slave_id:
                errors["slave_id"] = "Slave-ID muss gesetzt sein"

            if not errors:
                # Alle Werte vorhanden → Config Entry erstellen
                return self.async_create_entry(title=f"Modbus {host}", data=user_input)

        # Formular anzeigen
        data_schema = vol.Schema(
            {
                vol.Required("host", default="192.168.1.100"): str,
                vol.Required("port", default=502): int,
                vol.Required("slave_id", default=1): int,
            }
        )
        return self.async_show_form(step_id="user", data_schema=data_schema, errors=errors)