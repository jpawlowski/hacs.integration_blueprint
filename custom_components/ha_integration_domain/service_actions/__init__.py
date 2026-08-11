"""Service action registration for ha_integration_domain."""

from typing import TYPE_CHECKING

import voluptuous as vol

from custom_components.ha_integration_domain.const import DOMAIN
from homeassistant.core import SupportsResponse
from homeassistant.helpers import config_validation as cv

from .refresh_data import ATTR_CONFIG_ENTRY_ID, async_handle_refresh_data

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant, ServiceCall, ServiceResponse

SERVICE_REFRESH_DATA = "refresh_data"

REFRESH_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_CONFIG_ENTRY_ID): cv.string,
    },
)


async def async_setup_services(hass: HomeAssistant) -> None:
    """Register the integration's service actions once, at component level."""

    async def handle_refresh_data(call: ServiceCall) -> ServiceResponse:
        """
        Run the refresh_data action.

        Returns:
            The handler's response data.

        """
        return await async_handle_refresh_data(hass, call)

    if not hass.services.has_service(DOMAIN, SERVICE_REFRESH_DATA):
        hass.services.async_register(
            DOMAIN,
            SERVICE_REFRESH_DATA,
            handle_refresh_data,
            schema=REFRESH_DATA_SCHEMA,
            supports_response=SupportsResponse.OPTIONAL,
        )
