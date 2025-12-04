"""Tests for MaxxHacsTestingApiClient."""
import asyncio
from unittest.mock import patch
import pytest
from custom_components.maxx_hacs_testing.api import MaxxHacsTestingApiClient

@pytest.mark.anyio
async def test_async_get_data():
    """Test async_get_data."""
    api = MaxxHacsTestingApiClient()
    
    with patch("asyncio.sleep", return_value=None) as mock_sleep:
        data = await api.async_get_data()
        
        # Verify sleep was called
        mock_sleep.assert_called_once()
        
        # Verify data structure
        assert "electricity_usage" in data
        assert "water_usage" in data
        
        # Verify data types
        assert isinstance(data["electricity_usage"], float)
        assert isinstance(data["water_usage"], (int, float))
