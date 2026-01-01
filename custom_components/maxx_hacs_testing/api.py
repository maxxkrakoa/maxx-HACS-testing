"""Sample API Client."""
import logging
import asyncio
import random
import aiohttp
from .brunata import api as brunata_api

_LOGGER = logging.getLogger(__name__)

class MaxxHacsTestingApiClient:
    """Sample API Client."""

    def __init__(
        self, username: str, password: str, session: aiohttp.ClientSession
    ) -> None:
        """Sample API Client."""
        self._username = username
        self._password = password
        self._session = session

        # initialize Brunata API client
        self._brunata_client = brunata_api.BrunataOnlineApiClient(self._username, self._password, self._session)

    async def _async_validate_credentials(self) -> bool:
        """Validate credentials."""
        # check if tokens are valid - ie. username/password is valid
        tokens_valid = await self._brunata_client._get_tokens()

        return tokens_valid

    # Helper to find latest value in Meter category
    def _get_latest_value(self, json_data: dict, category_name: str) -> float | None:
        category_data = json_data.get(category_name, {})
        meters = category_data.get("Meters", {}).get("Day", {})
        
        for meter_id, meter_info in meters.items():
            values = meter_info.get("Values", {})
            if values:
                # keys are dates, sort them to find max
                latest_date = max(values.keys())
                return float(values[latest_date])
        return None

    async def async_authenticate(self) -> bool:
        """Authenticate with the API."""
        return await self._async_validate_credentials()

    async def async_get_data(self) -> dict:
        """Get data from the API."""
        # try to fetch all available data at the DAY granularity
        await self._brunata_client.fetch_meters()
        await self._brunata_client.fetch_consumption(brunata_api.Consumption.WATER, brunata_api.Interval.DAY)
        await self._brunata_client.fetch_consumption(brunata_api.Consumption.ELECTRICITY, brunata_api.Interval.DAY)
        await self._brunata_client.fetch_consumption(brunata_api.Consumption.HEATING, brunata_api.Interval.DAY)
        await self._brunata_client.fetch_consumption(brunata_api.Consumption.OTHER, brunata_api.Interval.DAY)

        # now that the data has been loaded, we extract the data we need
        json_data = await self._brunata_client.get_consumption()

        # Current mapping: Water -> water_usage, Other -> electricity_usage 
        # (works for my setup, will have to be changed to be more generic)        
        data = {}
        data["water_usage"] = self._get_latest_value(json_data, "Water")
        data["electricity_usage"] = self._get_latest_value(json_data, "Other")
        return data
