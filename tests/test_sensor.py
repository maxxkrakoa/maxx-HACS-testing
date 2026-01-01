"""Test the sensor."""
import sys
import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from types import SimpleNamespace
import os
import datetime

# Define simple mocks
class MockConst:
    DOMAIN = "maxx_hacs_testing"
    CONF_USERNAME = "username"
    CONF_PASSWORD = "password"
    UnitOfEnergy = SimpleNamespace(KILO_WATT_HOUR="kWh")
    UnitOfVolume = SimpleNamespace(LITERS="L")
    class Platform:
        SENSOR = "sensor"

class MockEntity:
    def __init__(self, *args, **kwargs):
        self._attr_extra_state_attributes = {}
    async def async_added_to_hass(self):
        pass
    @property
    def extra_state_attributes(self):
        return self._attr_extra_state_attributes

class MockCoordinatorEntity(MockEntity):
    def __init__(self, coordinator):
        super().__init__()
        self.coordinator = coordinator

class MockSensorEntity(MockEntity):
    pass

class MockCoordinator:
    def __init__(self, hass, logger, name, update_interval=None):
        self.data = {}
        self.async_add_listener = MagicMock()
        self.last_update_success = True

# Internal mocks
mock_brunata_client_instance = MagicMock()
mock_brunata_client_instance._get_tokens = AsyncMock(return_value=True)
mock_session_instance = MagicMock()

@pytest.fixture(name="mock_modules", autouse=True)
def mock_modules_fixture():
    # Create module mocks
    mock_hass_module = SimpleNamespace()
    mock_core_module = SimpleNamespace()
    mock_core_module.HomeAssistant = MagicMock
    mock_core_module.callback = lambda f: f
    
    mock_helpers_module = SimpleNamespace()
    mock_helpers_module.aiohttp_client = SimpleNamespace()
    mock_helpers_module.aiohttp_client.async_get_clientsession = MagicMock(return_value=mock_session_instance)

    # No restore_state needed anymore
    mock_helpers_module.restore_state = SimpleNamespace() 
    
    mock_helpers_module.entity = SimpleNamespace()
    mock_helpers_module.entity.Entity = MockEntity
    mock_helpers_module.entity_platform = SimpleNamespace()
    mock_helpers_module.entity_platform.AddEntitiesCallback = MagicMock()
    
    mock_update_coordinator_module = SimpleNamespace()
    mock_update_coordinator_module.DataUpdateCoordinator = MockCoordinator
    mock_update_coordinator_module.CoordinatorEntity = MockCoordinatorEntity
    mock_update_coordinator_module.UpdateFailed = Exception

    mock_sensor_module = SimpleNamespace()
    mock_sensor_module.SensorEntity = MockSensorEntity
    mock_sensor_module.SensorDeviceClass = SimpleNamespace()
    mock_sensor_module.SensorDeviceClass.ENERGY = "energy"
    mock_sensor_module.SensorStateClass = SimpleNamespace()
    mock_sensor_module.SensorStateClass.TOTAL_INCREASING = "total_increasing"
    
    mock_ha_const_module = MockConst()
    mock_local_const_module = MockConst()
    
    # External libs
    mock_aiohttp_module = SimpleNamespace()
    mock_aiohttp_module.ClientSession = MagicMock(return_value=mock_session_instance)
    
    mock_brunata_api_module = SimpleNamespace()
    mock_brunata_api_module.BrunataOnlineApiClient = MagicMock(return_value=mock_brunata_client_instance)

    # Patch sys.modules
    with patch.dict(sys.modules, {
        "homeassistant": mock_hass_module,
        "homeassistant.core": mock_core_module,
        "homeassistant.const": mock_ha_const_module,
        "homeassistant.helpers": mock_helpers_module,
        "homeassistant.helpers.restore_state": mock_helpers_module.restore_state,
        "homeassistant.helpers.entity": mock_helpers_module.entity,
        "homeassistant.helpers.entity_platform": mock_helpers_module.entity_platform,
        "homeassistant.helpers.update_coordinator": mock_update_coordinator_module,
        "homeassistant.helpers.aiohttp_client": mock_helpers_module.aiohttp_client,
        "homeassistant.components.sensor": mock_sensor_module,
        "custom_components.maxx_hacs_testing.const": mock_local_const_module,
        "aiohttp": mock_aiohttp_module,
        "brunata_api": mock_brunata_api_module,
        "libs.brunata.api": mock_brunata_api_module,
    }):
        # Ensure fresh import
        if "custom_components.maxx_hacs_testing.sensor" in sys.modules:
            del sys.modules["custom_components.maxx_hacs_testing.sensor"]
            
        sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        import custom_components.maxx_hacs_testing.sensor as sensor_module
        
        yield sensor_module

@pytest.fixture(name="coordinator")
def mock_coordinator():
    coord = MockCoordinator(None, None, "test")
    # timestamp still in data but unused by sensor
    coord.data = {"electricity_usage": 10.0, "timestamp": datetime.datetime.now().isoformat()}
    return coord

@pytest.mark.anyio
async def test_sensor_params(mock_modules, coordinator):
    sensor_module = mock_modules
    sensor = sensor_module.MaxxHacsTestingSensor(
        coordinator, "electricity_usage", "Electricity", "energy", "kWh"
    )
    assert sensor.native_value == 10.0
