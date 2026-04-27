"""Config flow for WHOOP integration."""

from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import WhoopApiClient, WhoopApiError
from .const import CONF_API_TOKEN, CONF_USER_ID, DEFAULT_NAME, DOMAIN


class WhoopConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for WHOOP."""

    VERSION = 1

    async def _validate_input(self, data: dict[str, str]) -> None:
        client = WhoopApiClient(
            async_get_clientsession(self.hass),
            data[CONF_API_TOKEN],
            data[CONF_USER_ID],
        )
        await client.async_get_metrics()

    async def async_step_user(self, user_input: dict[str, Any] | None = None):
        errors: dict[str, str] = {}

        if user_input is not None:
            await self.async_set_unique_id(user_input[CONF_USER_ID])
            self._abort_if_unique_id_configured()

            try:
                await self._validate_input(user_input)
            except WhoopApiError:
                errors["base"] = "cannot_connect"
            except Exception:  # noqa: BLE001
                errors["base"] = "unknown"
            else:
                return self.async_create_entry(title=DEFAULT_NAME, data=user_input)

        data_schema = vol.Schema(
            {
                vol.Required(CONF_API_TOKEN): str,
                vol.Required(CONF_USER_ID): str,
            }
        )
        return self.async_show_form(step_id="user", data_schema=data_schema, errors=errors)

    async def async_step_reauth(self, entry_data: dict[str, Any]):
        return await self.async_step_user(user_input=entry_data)
