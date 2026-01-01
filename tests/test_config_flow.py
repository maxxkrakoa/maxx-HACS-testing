"""Test the config flow."""
import sys
import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from types import SimpleNamespace
import os
import importlib

# Define simple mocks for libraries
class MockConst:
    CONF_USERNAME = "username"
    CONF_PASSWORD = "password"
    class Platform:
        SENSOR = "sensor"
    DOMAIN = "maxx_hacs_testing"

class MockConfigFlowParent:
    def __init__(self):
        self.hass = None
        self.context = {}
    
    def __init_subclass__(cls, **kwargs):
        pass

    def async_show_form(self, step_id, data_schema=None, errors=None):
        return {"type": "form", "step_id": step_id, "errors": errors}
    
    def async_create_entry(self, title, data):
        return {"type": "create_entry", "title": title, "data": data}
        
    def async_update_reload_and_abort(self, entry, data):
        return {"type": "abort", "reason": "reconfigure_successful"}

# Internal mocks we want to assert on
# We create them globally but inject them via fixture
mock_brunata_client_instance = MagicMock()
mock_brunata_client_instance._get_tokens = AsyncMock()
mock_session_instance = MagicMock()

@pytest.fixture(name="mock_modules", autouse=True)
def mock_modules_fixture():
    # Create module mocks
    mock_hass_module = SimpleNamespace()
    mock_config_entries_module = SimpleNamespace()
    mock_config_entries_module.ConfigFlow = MockConfigFlowParent
    mock_config_entries_module.ConfigEntry = MagicMock
    mock_core_module = SimpleNamespace()
    mock_core_module.HomeAssistant = MagicMock
    mock_data_entry_flow_module = SimpleNamespace()
    mock_data_entry_flow_module.FlowResult = dict
    mock_ha_const_module = MockConst()
    mock_local_const_module = MockConst()
    
    # Voluptuous
    class MockSchema:
        def __init__(self, schema):
            self.schema = schema
        def __call__(self, data):
            return data
    def MockRequired(key, default=None):
        return key

    mock_voluptuous_module = SimpleNamespace()
    mock_voluptuous_module.Schema = MockSchema
    mock_voluptuous_module.Required = MockRequired
    
    # Link package submodules
    mock_hass_module.config_entries = mock_config_entries_module
    mock_hass_module.const = mock_ha_const_module
    mock_hass_module.core = mock_core_module
    mock_hass_module.data_entry_flow = mock_data_entry_flow_module
    
    mock_helpers_module = SimpleNamespace()
    mock_helpers_module.aiohttp_client = SimpleNamespace()
    mock_helpers_module.aiohttp_client.async_get_clientsession = MagicMock(return_value=mock_session_instance)

    # External libs
    mock_aiohttp_module = SimpleNamespace()
    mock_aiohttp_module.ClientSession = MagicMock(return_value=mock_session_instance)
    
    mock_brunata_api_module = SimpleNamespace()
    mock_brunata_api_module.BrunataOnlineApiClient = MagicMock(return_value=mock_brunata_client_instance)

    # Patch sys.modules
    with patch.dict(sys.modules, {
        "homeassistant": mock_hass_module,
        "homeassistant.config_entries": mock_config_entries_module,
        "homeassistant.core": mock_core_module,
        "homeassistant.data_entry_flow": mock_data_entry_flow_module,
        "homeassistant.const": mock_ha_const_module,
        "homeassistant.helpers.aiohttp_client": mock_helpers_module.aiohttp_client,
        "voluptuous": mock_voluptuous_module,
        "custom_components.maxx_hacs_testing.const": mock_local_const_module,
        "aiohttp": mock_aiohttp_module,
        "brunata_api": mock_brunata_api_module,
        "libs.brunata.api": mock_brunata_api_module,
    }):
        # Ensure fresh import of modules under test
        if "custom_components.maxx_hacs_testing.config_flow" in sys.modules:
            del sys.modules["custom_components.maxx_hacs_testing.config_flow"]
        if "custom_components.maxx_hacs_testing.api" in sys.modules:
            del sys.modules["custom_components.maxx_hacs_testing.api"]
            
        sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        import custom_components.maxx_hacs_testing.config_flow as config_flow
        from custom_components.maxx_hacs_testing.const import DOMAIN, CONF_USERNAME, CONF_PASSWORD
        
        yield config_flow, DOMAIN, CONF_USERNAME, CONF_PASSWORD

@pytest.fixture(name="hass")
def mock_hass_fixture():
    m = MagicMock()
    m.config_entries.async_get_entry = MagicMock()
    return m

@pytest.mark.anyio
async def test_form(hass, mock_modules):
    config_flow, DOMAIN, CONF_USERNAME, CONF_PASSWORD = mock_modules
    flow = config_flow.ConfigFlow()
    flow.hass = hass
    result = await flow.async_step_user()
    assert result["type"] == "form"

@pytest.mark.anyio
async def test_form_valid_auth(hass, mock_modules):
    config_flow, DOMAIN, CONF_USERNAME, CONF_PASSWORD = mock_modules
    flow = config_flow.ConfigFlow()
    flow.hass = hass
    
    # Configure mock client
    mock_brunata_client_instance._get_tokens.return_value = True
    
    result = await flow.async_step_user({CONF_USERNAME: "u", CONF_PASSWORD: "p"})
    assert result["type"] == "create_entry"
    assert result["data"] == {CONF_USERNAME: "u", CONF_PASSWORD: "p"}
    
    # Verify interaction
    import brunata_api
    brunata_api.BrunataOnlineApiClient.assert_called_with("u", "p", mock_session_instance)
    mock_brunata_client_instance._get_tokens.assert_called() # loose check

@pytest.mark.anyio
async def test_form_invalid_auth(hass, mock_modules):
    config_flow, DOMAIN, CONF_USERNAME, CONF_PASSWORD = mock_modules
    flow = config_flow.ConfigFlow()
    flow.hass = hass
    
    mock_brunata_client_instance._get_tokens.return_value = False
    
    result = await flow.async_step_user({CONF_USERNAME: "u", CONF_PASSWORD: "p"})
    assert result["type"] == "form"
    assert result["errors"] == {"base": "invalid_auth"}

@pytest.mark.anyio
async def test_reconfigure(hass, mock_modules):
    config_flow, DOMAIN, CONF_USERNAME, CONF_PASSWORD = mock_modules
    flow = config_flow.ConfigFlow()
    flow.hass = hass
    flow.context = {"entry_id": "123"}
    
    mock_entry = MagicMock()
    mock_entry.data = {CONF_USERNAME: "old"}
    hass.config_entries.async_get_entry.return_value = mock_entry
    
    result = await flow.async_step_reconfigure()
    assert result["type"] == "form"
    
    mock_brunata_client_instance._get_tokens.return_value = True
    result = await flow.async_step_reconfigure({CONF_USERNAME: "new", CONF_PASSWORD: "new"})
    assert result["type"] == "abort"
