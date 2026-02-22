import sys
import os
import unittest.mock as mock

from types import SimpleNamespace
mock_hass = SimpleNamespace()
mock_hass.helpers = SimpleNamespace()
mock_hass.helpers.aiohttp_client = SimpleNamespace()
mock_hass.config_entries = SimpleNamespace()
mock_hass.config_entries.ConfigFlow = object
mock_hass.core = SimpleNamespace()
mock_hass.data_entry_flow = SimpleNamespace()
mock_hass.const = SimpleNamespace()
mock_hass.const.CONF_PASSWORD = "password"
mock_hass.const.CONF_USERNAME = "username"

with mock.patch.dict(sys.modules, {
    "homeassistant": mock_hass,
    "homeassistant.helpers": mock_hass.helpers,
    "homeassistant.helpers.aiohttp_client": mock_hass.helpers.aiohttp_client,
    "homeassistant.config_entries": mock_hass.config_entries,
    "homeassistant.core": mock_hass.core,
    "homeassistant.data_entry_flow": mock_hass.data_entry_flow,
    "homeassistant.const": mock_hass.const,
    "voluptuous": SimpleNamespace(),
}):
    sys.path.append(os.path.abspath("."))
    try:
        import custom_components.maxx_hacs_testing.config_flow
        print("Import successful!")
    except Exception as e:
        import traceback
        traceback.print_exc()
