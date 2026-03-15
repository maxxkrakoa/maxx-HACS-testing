"""The Home Assistant Brunata Online integration."""
from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .api import BrunataOnlineApiClient
from .const import DOMAIN, CONF_USERNAME, CONF_PASSWORD
from .coordinator import BrunataOnlineDataUpdateCoordinator

PLATFORMS: list[Platform] = [Platform.SENSOR]

from homeassistant.helpers.aiohttp_client import async_get_clientsession

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Home Assistant Brunata Online from a config entry."""
    hass.data.setdefault(DOMAIN, {})

    session = async_get_clientsession(hass)
    client = BrunataOnlineApiClient(
        username=entry.data[CONF_USERNAME],
        password=entry.data[CONF_PASSWORD],
        session=session,
    )
    coordinator = BrunataOnlineDataUpdateCoordinator(hass, client)
    
    await coordinator.async_config_entry_first_refresh()

    hass.data[DOMAIN][entry.entry_id] = coordinator

    async def handle_update_data(call):
        """Handle the service call."""
        await coordinator.async_request_refresh()

    hass.services.async_register(DOMAIN, "update_data", handle_update_data)

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
