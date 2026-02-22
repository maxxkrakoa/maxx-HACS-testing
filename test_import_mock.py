import sys
import os
import unittest.mock as mock

from types import SimpleNamespace
mock_hass = SimpleNamespace()
mock_hass.helpers = SimpleNamespace()
mock_hass.helpers.aiohttp_client = SimpleNamespace()

with mock.patch.dict(sys.modules, {
    "homeassistant": mock_hass,
    "homeassistant.helpers": mock_hass.helpers,
    "homeassistant.helpers.aiohttp_client": mock_hass.helpers.aiohttp_client,
}):
    sys.path.append(os.path.abspath("."))
    from custom_components.maxx_hacs_testing.brunata.api import BrunataOnlineApiClient
    import custom_components.maxx_hacs_testing.brunata.api as test_api
    
    print("Does ClientSession exist?", hasattr(test_api, "ClientSession"))
    print("What is it?", getattr(test_api, "ClientSession", None))
