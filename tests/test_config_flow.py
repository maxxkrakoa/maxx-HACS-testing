"""Test the config flow."""
import sys
import pytest
from unittest.mock import MagicMock, patch
from types import SimpleNamespace

# -- MOCK SETUP --

# 1. Plain constants
class MockConst:
    CONF_USERNAME = "username"
    CONF_PASSWORD = "password"
    class Platform:
        SENSOR = "sensor"
    DOMAIN = "maxx_hacs_testing"

# 2. Config Flow Parent
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

# 3. fake modules
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
    return key # Return just the string key to be used in dict

mock_voluptuous_module = SimpleNamespace()
mock_voluptuous_module.Schema = MockSchema
mock_voluptuous_module.Required = MockRequired

# Patch sys.modules
sys.modules["homeassistant"] = mock_hass_module
sys.modules["homeassistant.config_entries"] = mock_config_entries_module
sys.modules["homeassistant.core"] = mock_core_module
sys.modules["homeassistant.data_entry_flow"] = mock_data_entry_flow_module
sys.modules["homeassistant.const"] = mock_ha_const_module
sys.modules["voluptuous"] = mock_voluptuous_module
sys.modules["custom_components.maxx_hacs_testing.const"] = mock_local_const_module

# Link submodules to package
mock_hass_module.config_entries = mock_config_entries_module
mock_hass_module.const = mock_ha_const_module
mock_hass_module.core = mock_core_module
mock_hass_module.data_entry_flow = mock_data_entry_flow_module

# Import module
import os
import importlib
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

if "custom_components.maxx_hacs_testing.config_flow" in sys.modules:
    del sys.modules["custom_components.maxx_hacs_testing.config_flow"]

from custom_components.maxx_hacs_testing import config_flow
from custom_components.maxx_hacs_testing.const import DOMAIN, CONF_USERNAME, CONF_PASSWORD

@pytest.fixture(name="hass")
def mock_hass_fixture():
    m = MagicMock()
    m.config_entries.async_get_entry = MagicMock()
    return m

@pytest.mark.anyio
async def test_form(hass):
    flow = config_flow.ConfigFlow()
    flow.hass = hass
    result = await flow.async_step_user()
    assert result["type"] == "form"

@pytest.mark.anyio
async def test_form_valid_auth(hass):
    flow = config_flow.ConfigFlow()
    flow.hass = hass
    with patch("custom_components.maxx_hacs_testing.api.MaxxHacsTestingApiClient.async_authenticate", return_value=True):
        result = await flow.async_step_user({CONF_USERNAME: "u", CONF_PASSWORD: "p"})
    assert result["type"] == "create_entry"
    assert result["data"] == {CONF_USERNAME: "u", CONF_PASSWORD: "p"}

@pytest.mark.anyio
async def test_form_invalid_auth(hass):
    flow = config_flow.ConfigFlow()
    flow.hass = hass
    with patch("custom_components.maxx_hacs_testing.api.MaxxHacsTestingApiClient.async_authenticate", return_value=False):
        result = await flow.async_step_user({CONF_USERNAME: "u", CONF_PASSWORD: "p"})
    assert result["type"] == "form"
    assert result["errors"] == {"base": "invalid_auth"}

@pytest.mark.anyio
async def test_reconfigure(hass):
    flow = config_flow.ConfigFlow()
    flow.hass = hass
    flow.context = {"entry_id": "123"}
    mock_entry = MagicMock()
    mock_entry.data = {CONF_USERNAME: "old"}
    hass.config_entries.async_get_entry.return_value = mock_entry
    
    result = await flow.async_step_reconfigure()
    assert result["type"] == "form"
    
    with patch("custom_components.maxx_hacs_testing.api.MaxxHacsTestingApiClient.async_authenticate", return_value=True):
        result = await flow.async_step_reconfigure({CONF_USERNAME: "new", CONF_PASSWORD: "new"})
    assert result["type"] == "abort"
