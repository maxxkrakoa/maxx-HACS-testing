"""Config flow for Home Assistant Brunata Online integration."""
from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult

from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import BrunataOnlineApiClient
from .const import DOMAIN, LOGGER

_LOGGER = LOGGER

class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Home Assistant Brunata Online."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            # Validate credentials
            session = async_get_clientsession(self.hass)
            client = BrunataOnlineApiClient(
                username=user_input[CONF_USERNAME],
                password=user_input[CONF_PASSWORD],
                session=session,
            )
            
            _LOGGER.debug("Attempting to authenticate user: %s", user_input[CONF_USERNAME])
            valid = await client.async_authenticate()
            _LOGGER.debug("Authentication result: %s", valid)
            
            if valid:
                return self.async_create_entry(
                    title=user_input[CONF_USERNAME],
                    data=user_input,
                )
            else:
                errors["base"] = "invalid_auth"

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_USERNAME): str,
                    vol.Required(CONF_PASSWORD): str,
                }
            ),
            errors=errors,
        )

    async def async_step_reconfigure(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle reconfiguration."""
        errors: dict[str, str] = {}
        entry = self.hass.config_entries.async_get_entry(self.context["entry_id"])

        if user_input is not None:
            session = async_get_clientsession(self.hass)
            client = BrunataOnlineApiClient(
                username=user_input[CONF_USERNAME],
                password=user_input[CONF_PASSWORD],
                session=session,
            )
            
            _LOGGER.debug("Attempting to re-authenticate user: %s", user_input[CONF_USERNAME])
            valid = await client.async_authenticate()
            _LOGGER.debug("Re-authentication result: %s", valid)
            
            if valid:
                return self.async_update_reload_and_abort(
                    entry,
                    data={**entry.data, **user_input},
                )
            else:
                errors["base"] = "invalid_auth"

        return self.async_show_form(
            step_id="reconfigure",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_USERNAME, default=entry.data.get(CONF_USERNAME)): str,
                    vol.Required(CONF_PASSWORD): str,
                }
            ),
            errors=errors,
        )
