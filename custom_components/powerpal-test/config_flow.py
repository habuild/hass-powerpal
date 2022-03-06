"""Adds config flow for Blueprint."""
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers.aiohttp_client import async_create_clientsession
import voluptuous as vol

from mindmelting.powerpal import Powerpal

from .const import (
    CONF_DEVICE_ID,
    CONF_AUTH_KEY,
    DOMAIN,
    PLATFORMS,
)


class BlueprintFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for Blueprint."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_CLOUD_POLL

    def __init__(self):
        """Initialize."""
        self._errors = {}

    async def async_step_user(self, user_input=None):
        """Handle a flow initialized by the user."""
        self._errors = {}

        # Uncomment the next 2 lines if only a single instance of the integration is allowed:
        # if self._async_current_entries():
        #     return self.async_abort(reason="single_instance_allowed")

        if user_input is not None:
            valid = await self._test_credentials(
                user_input[CONF_AUTH_KEY], user_input[CONF_DEVICE_ID]
            )
            if valid:
                return self.async_create_entry(
                    title=f"Powerpal {user_input[CONF_DEVICE_ID]}", data=user_input
                )
            else:
                self._errors["base"] = "auth"

            return await self._show_config_form(user_input)

        user_input = {}
        # Provide defaults for form
        user_input[CONF_AUTH_KEY] = ""
        user_input[CONF_DEVICE_ID] = ""

        return await self._show_config_form(user_input)

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return BlueprintOptionsFlowHandler(config_entry)

    async def _show_config_form(self, user_input):  # pylint: disable=unused-argument
        """Show the configuration form to edit auth data."""
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_AUTH_KEY, default=user_input[CONF_AUTH_KEY]): str,
                    vol.Required(
                        CONF_DEVICE_ID, default=user_input[CONF_DEVICE_ID]
                    ): str,
                }
            ),
            errors=self._errors,
        )

    async def _test_credentials(self, authKey, deviceId):
        """Return true if credentials is valid."""
        try:
            session = async_create_clientsession(self.hass)
            client = Powerpal(session, authKey, deviceId)
            await client.get_data()
            return True
        except Exception:  # pylint: disable=broad-except
            pass
        return False


class BlueprintOptionsFlowHandler(config_entries.OptionsFlow):
    """Blueprint config flow options handler."""

    def __init__(self, config_entry):
        """Initialize HACS options flow."""
        self.config_entry = config_entry
        self.options = dict(config_entry.options)

    async def async_step_init(self, user_input=None):  # pylint: disable=unused-argument
        """Manage the options."""
        return await self.async_step_user()

    async def async_step_user(self, user_input=None):
        """Handle a flow initialized by the user."""
        if user_input is not None:
            self.options.update(user_input)
            return await self._update_options()

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(x, default=self.options.get(x, True)): bool
                    for x in sorted(PLATFORMS)
                }
            ),
        )

    async def _update_options(self):
        """Update config entry options."""
        return self.async_create_entry(
            title=f"Powerpal {self.config_entry.data.get(CONF_DEVICE_ID)}",
            data=self.options,
        )
