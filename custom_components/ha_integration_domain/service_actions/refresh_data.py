"""Handler for the refresh_data service action."""

from typing import TYPE_CHECKING

from custom_components.ha_integration_domain.const import DOMAIN
from homeassistant.config_entries import ConfigEntryState
from homeassistant.exceptions import ServiceValidationError
from homeassistant.util import dt as dt_util

if TYPE_CHECKING:
    from custom_components.ha_integration_domain.data import IntegrationBlueprintConfigEntry
    from homeassistant.core import HomeAssistant, ServiceCall, ServiceResponse

ATTR_CONFIG_ENTRY_ID = "config_entry_id"


async def async_handle_refresh_data(hass: HomeAssistant, call: ServiceCall) -> ServiceResponse:
    """
    Refresh the coordinator of the targeted config entry.

    Returns:
        When the refresh happened and whether it produced usable data.

    Raises:
        ServiceValidationError: If the targeted entry does not exist or is not loaded.

    """
    entry = _async_get_loaded_entry(hass, call.data[ATTR_CONFIG_ENTRY_ID])
    coordinator = entry.runtime_data.coordinator

    await coordinator.async_refresh()

    return {
        "refreshed_at": dt_util.utcnow().isoformat(),
        "success": coordinator.last_update_success,
        "value_count": len(coordinator.data),
    }


def _async_get_loaded_entry(hass: HomeAssistant, entry_id: str) -> IntegrationBlueprintConfigEntry:
    """
    Resolve a config entry id to a loaded entry.

    Returns:
        The loaded config entry.

    Raises:
        ServiceValidationError: If the entry is unknown or not loaded.

    """
    entry = hass.config_entries.async_get_entry(entry_id)
    if entry is None or entry.domain != DOMAIN:
        raise ServiceValidationError(
            translation_domain=DOMAIN,
            translation_key="entry_not_found",
            translation_placeholders={"target": entry_id},
        )
    if entry.state is not ConfigEntryState.LOADED:
        raise ServiceValidationError(
            translation_domain=DOMAIN,
            translation_key="entry_not_loaded",
            translation_placeholders={"target": entry.title},
        )
    return entry
