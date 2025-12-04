"""Global fixtures for Maxx HACS Testing integration."""
import sys
from unittest.mock import MagicMock
import pytest

# Mock homeassistant module
module_mock = MagicMock()
sys.modules["homeassistant"] = module_mock
sys.modules["homeassistant.config_entries"] = module_mock
sys.modules["homeassistant.const"] = module_mock
sys.modules["homeassistant.core"] = module_mock
sys.modules["homeassistant.helpers"] = module_mock
sys.modules["homeassistant.helpers.update_coordinator"] = module_mock

@pytest.fixture
def anyio_backend():
    return "asyncio"
