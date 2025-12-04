"""Sample API Client."""
import logging
import asyncio
import random

_LOGGER = logging.getLogger(__name__)

class MaxxHacsTestingApiClient:
    """Sample API Client."""

    def __init__(self) -> None:
        """Sample API Client."""
        pass

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
