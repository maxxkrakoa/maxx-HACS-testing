"""Sensor platform for Maxx HACS Testing."""
from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfEnergy, UnitOfVolume
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import MaxxHacsTestingDataUpdateCoordinator

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the sensor platform."""
    coordinator: MaxxHacsTestingDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    
    entities = [
        MaxxHacsTestingSensor(
            coordinator=coordinator,
            key="electricity_usage",
            name="Electricity Usage",
            device_class=SensorDeviceClass.ENERGY,
            native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        ),
        MaxxHacsTestingSensor(
            coordinator=coordinator,
            key="water_usage",
            name="Water Usage",
            device_class=SensorDeviceClass.WATER,
            native_unit_of_measurement=UnitOfVolume.LITERS,
        ),
    ]
    
    async_add_entities(entities)

class MaxxHacsTestingSensor(CoordinatorEntity, SensorEntity):
    """Maxx HACS Testing Sensor class."""

    def __init__(
        self,
        coordinator: MaxxHacsTestingDataUpdateCoordinator,
        key: str,
        name: str,
        device_class: SensorDeviceClass,
        native_unit_of_measurement: str,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._key = key
        self._attr_name = f"Maxx HACS Testing {name}"
        self._attr_unique_id = f"{DOMAIN}_{key}"
        self._attr_device_class = device_class
        self._attr_native_unit_of_measurement = native_unit_of_measurement
        self._attr_state_class = SensorStateClass.TOTAL_INCREASING

    @property
    def native_value(self):
        """Return the native value of the sensor."""
        return self.coordinator.data.get(self._key)
