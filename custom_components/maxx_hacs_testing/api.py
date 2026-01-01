"""Sample API Client."""
import logging
import asyncio
import random
import aiohttp
import brunata_api

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

    async def async_authenticate(self) -> bool:
        """Authenticate with the API."""
        return await self._async_validate_credentials()

    async def async_get_data(self) -> dict:
        """Get data from the API."""
        # Simulate network delay
        await asyncio.sleep(1)
        
        # Return mock data
        # In a real implementation, this would call a REST API
        return {
            "electricity_usage": round(random.uniform(0.5, 5.0), 2), # kWh
            "water_usage": round(random.uniform(10, 100), 1), # Liters
        }
