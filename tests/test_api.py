"""Tests for MaxxHacsTestingApiClient."""
import sys
import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from types import SimpleNamespace
import os

# Internal mocks
mock_brunata_client_instance = MagicMock()
mock_brunata_client_instance._get_tokens = AsyncMock(return_value=True)
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

    # Patch sys.modules
    with patch.dict(sys.modules, {
        "aiohttp": mock_aiohttp_module,
        "homeassistant.helpers.aiohttp_client": mock_helpers_module.aiohttp_client,
        "brunata_api": mock_brunata_api_module,
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
    """Test async_get_data."""
    api_class = mock_modules
    api = api_class("user", "pass", mock_session_instance)
    
    with patch("asyncio.sleep", return_value=None):
        data = await api.async_get_data()
        
        # Verify data structure
        assert "electricity_usage" in data
        assert "water_usage" in data
        
        # Verify data types
        assert isinstance(data["electricity_usage"], float)
        assert isinstance(data["water_usage"], (int, float))

@pytest.mark.anyio
async def test_async_authenticate(mock_modules):
    """Test async_authenticate."""
    api_class = mock_modules
    api = api_class("user", "pass", mock_session_instance)
    
    mock_brunata_client_instance._get_tokens.return_value = True
    assert await api.async_authenticate() is True
    
    mock_brunata_client_instance._get_tokens.return_value = False
    assert await api.async_authenticate() is False
