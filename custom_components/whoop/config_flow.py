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

    async def _prepare_user_id(self, data: dict[str, str]) -> str:
        """Validate or resolve WHOOP user id."""
        client = WhoopApiClient(
            async_get_clientsession(self.hass),
            data[CONF_API_TOKEN],
            str(data.get(CONF_USER_ID, "")).strip(),
        )

        user_id = str(data.get(CONF_USER_ID, "")).strip()
        if user_id:
            if not user_id.isdigit():
                raise ValueError("invalid_user_id")
            return user_id

        return await client.async_get_user_id()

    async def _validate_input(self, api_token: str, user_id: str) -> None:
        client = WhoopApiClient(async_get_clientsession(self.hass), api_token, user_id)
        await client.async_get_metrics()

    async def async_step_user(self, user_input: dict[str, Any] | None = None):
        errors: dict[str, str] = {}

        if user_input is not None:
            try:
                resolved_user_id = await self._prepare_user_id(user_input)
            except ValueError:
                errors["base"] = "invalid_user_id"
            except WhoopApiError:
                errors["base"] = "cannot_resolve_user"
            else:
                await self.async_set_unique_id(resolved_user_id)
                self._abort_if_unique_id_configured()

                try:
                    await self._validate_input(user_input[CONF_API_TOKEN], resolved_user_id)
                except WhoopApiError:
                    errors["base"] = "cannot_connect"
                except Exception:  # noqa: BLE001
                    errors["base"] = "unknown"
                else:
                    return self.async_create_entry(
                        title=DEFAULT_NAME,
                        data={
                            CONF_API_TOKEN: user_input[CONF_API_TOKEN],
                            CONF_USER_ID: resolved_user_id,
                        },
                    )

        data_schema = vol.Schema(
            {
                vol.Required(CONF_API_TOKEN): str,
                vol.Optional(CONF_USER_ID, default=""): str,
            }
        )
        return self.async_show_form(step_id="user", data_schema=data_schema, errors=errors)

    async def async_step_reauth(self, entry_data: dict[str, Any]):
        return await self.async_step_user(user_input=entry_data)
