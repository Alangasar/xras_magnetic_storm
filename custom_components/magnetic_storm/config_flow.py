import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from .const import DOMAIN, CITIES

class MagneticStormConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_CLOUD_POLL

    async def async_step_user(self, user_input=None):
        errors = {}
        if user_input is not None:
            # Проверка, что город выбран
            if user_input["city"] in CITIES:
                return self.async_create_entry(title=CITIES[user_input["city"]], data=user_input)
            else:
                errors["base"] = "invalid_city"

        # Форма для выбора города
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required("city"): vol.In(CITIES)
            }),
            errors=errors
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return MagneticStormOptionsFlow(config_entry)

class MagneticStormOptionsFlow(config_entries.OptionsFlow):
    def __init__(self, config_entry):
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema({
                vol.Required("city", default=self.config_entry.data.get("city")): vol.In(CITIES)
            })
        )