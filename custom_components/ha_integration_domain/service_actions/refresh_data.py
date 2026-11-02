"""Handler for the refresh_data service action."""

from typing import TYPE_CHECKING

from custom_components.ha_integration_domain.const import DOMAIN
from homeassistant.const import ATTR_CONFIG_ENTRY_ID
from homeassistant.helpers.service import async_get_config_entry
from homeassistant.util import dt as dt_util

if TYPE_CHECKING:
    from custom_components.ha_integration_domain.data import IntegrationBlueprintConfigEntry
    from homeassistant.core import HomeAssistant, ServiceCall, ServiceResponse


async def async_handle_refresh_data(hass: HomeAssistant, call: ServiceCall) -> ServiceResponse:
    """
    Refresh the coordinator of the targeted config entry.

    Returns:
        When the refresh happened and whether it produced usable data.

    Raises:
        ServiceValidationError: If the targeted entry does not exist or is not loaded.

    """
    entry: IntegrationBlueprintConfigEntry = async_get_config_entry(hass, DOMAIN, call.data[ATTR_CONFIG_ENTRY_ID])
    coordinator = entry.runtime_data.coordinator

    await coordinator.async_refresh()

    return {
        "refreshed_at": dt_util.utcnow().isoformat(),
        "success": coordinator.last_update_success,
        "value_count": len(coordinator.data),
    }
