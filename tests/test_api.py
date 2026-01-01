"""Tests for MaxxHacsTestingApiClient."""
import sys
import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from types import SimpleNamespace
import os

# Internal mocks
mock_brunata_client_instance = MagicMock()
mock_brunata_client_instance._get_tokens = AsyncMock(return_value=True)
mock_brunata_client_instance.fetch_meters = AsyncMock()
mock_brunata_client_instance.fetch_consumption = AsyncMock()
mock_brunata_client_instance.get_consumption = AsyncMock() # Will set return value in test

mock_session_instance = MagicMock()

@pytest.fixture(name="mock_modules", autouse=True)
def mock_modules_fixture():
    # External libs
    mock_aiohttp_module = SimpleNamespace()
    mock_aiohttp_module.ClientSession = MagicMock(return_value=mock_session_instance)
    
    mock_helpers_module = SimpleNamespace()
    mock_helpers_module.aiohttp_client = SimpleNamespace()
    mock_helpers_module.aiohttp_client.async_get_clientsession = MagicMock(return_value=mock_session_instance)

    mock_brunata_api_module = SimpleNamespace()
    mock_brunata_api_module.BrunataOnlineApiClient = MagicMock(return_value=mock_brunata_client_instance)
    # Mock enums
    mock_brunata_api_module.Consumption = SimpleNamespace(WATER="Water", ELECTRICITY="Electricity", HEATING="Heating", OTHER="Other")
    mock_brunata_api_module.Interval = SimpleNamespace(DAY="Day")

    # Patch sys.modules
    with patch.dict(sys.modules, {
        "aiohttp": mock_aiohttp_module,
        "homeassistant.helpers.aiohttp_client": mock_helpers_module.aiohttp_client,
        "custom_components.maxx_hacs_testing.brunata.api": mock_brunata_api_module,
        "libs.brunata.api": mock_brunata_api_module,
    }):
        # Ensure fresh import of api
        if "custom_components.maxx_hacs_testing.api" in sys.modules:
            del sys.modules["custom_components.maxx_hacs_testing.api"]
            
        sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from custom_components.maxx_hacs_testing.api import MaxxHacsTestingApiClient
        
        yield MaxxHacsTestingApiClient

@pytest.mark.anyio
async def test_async_get_data(mock_modules):
    """Test async_get_data with sample JSON."""
    api_class = mock_modules
    api = api_class("user", "pass", mock_session_instance)
    
    # Sample JSON from user request
    sample_json = {
        "Heating": {},
        "Water": {
            "Meters": {
                "Day": {
                    "12709726": {
                        "Name": "Teknikrum",
                        "Values": {
                            "2026-01-01": 0.0,
                            "2026-01-02": 1.0
                        }
                    }
                },
                "Month": {}
            },
            "Units": ["K"]
        },
        "Electricity": {},
        "Other": {
            "Meters": {
                "Day": {
                    "12709720": {
                        "Name": "Teknikrum",
                        "Values": {
                            "2026-01-01": 0,
                            "2026-01-02": 7
                        }
                    }
                },
                "Month": {}
            },
            "Units": ["M"]
        }
    }
    
    mock_brunata_client_instance.get_consumption.return_value = sample_json
    
    data = await api.async_get_data()
    
    # Verify calls
    assert mock_brunata_client_instance.fetch_meters.await_count == 1
    assert mock_brunata_client_instance.fetch_consumption.await_count == 4
    
    # Verify data extraction
    assert "electricity_usage" in data
    assert "water_usage" in data
    
    # Map Other -> electricity_usage (latest value is 7)
    assert data["electricity_usage"] == 7
    
    # Map Water -> water_usage (latest value is 1.0)
    assert data["water_usage"] == 1.0

@pytest.mark.anyio
async def test_async_authenticate(mock_modules):
    """Test async_authenticate."""
    api_class = mock_modules
    api = api_class("user", "pass", mock_session_instance)
    
    mock_brunata_client_instance._get_tokens.return_value = True
    assert await api.async_authenticate() is True
    
    mock_brunata_client_instance._get_tokens.return_value = False
    assert await api.async_authenticate() is False
