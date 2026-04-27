"""Data coordinator for WHOOP."""

from __future__ import annotations

from datetime import timedelta
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed, ConfigEntryError
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import WhoopApiClient, WhoopApiError
from .const import CONF_API_TOKEN, CONF_USER_ID, DOMAIN, UPDATE_INTERVAL_SECONDS

_LOGGER = logging.getLogger(__name__)


class WhoopDataUpdateCoordinator(DataUpdateCoordinator[dict]):
    """Class to manage fetching WHOOP data."""

    config_entry: ConfigEntry

    def __init__(self, hass: HomeAssistant, config_entry: ConfigEntry) -> None:
        self.config_entry = config_entry
        self.client = WhoopApiClient(
            async_get_clientsession(hass),
            config_entry.data[CONF_API_TOKEN],
            config_entry.data[CONF_USER_ID],
        )

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=UPDATE_INTERVAL_SECONDS),
        )

    async def _async_update_data(self) -> dict:
        try:
            return await self.client.async_get_metrics()
        except WhoopApiError as err:
            if "401" in str(err):
                raise ConfigEntryAuthFailed("Invalid WHOOP token") from err
            raise UpdateFailed(str(err)) from err
        except Exception as err:
            raise ConfigEntryError(f"Unexpected WHOOP error: {err}") from err
