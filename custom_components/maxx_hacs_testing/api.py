"""Sample API Client."""
import logging
import asyncio
import random

_LOGGER = logging.getLogger(__name__)

class MaxxHacsTestingApiClient:
    """Sample API Client."""

    def __init__(self, username: str, password: str) -> None:
        """Sample API Client."""
        self._username = username
        self._password = password

    async def async_authenticate(self) -> bool:
        """Authenticate with the API."""
        # Simulate network delay
        await asyncio.sleep(1)
        
        # Simple check: pass must not be empty
        if not self._username or not self._password:
            return False
            
        return True

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
