"""
Diagnostics support for ha_integration_domain.

https://developers.home-assistant.io/docs/core/integration_diagnostics
"""

from typing import TYPE_CHECKING, Any

from homeassistant.const import CONF_PASSWORD, CONF_USERNAME
from homeassistant.helpers.redact import async_redact_data

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant

    from .data import IntegrationBlueprintConfigEntry

TO_REDACT = {
    CONF_PASSWORD,
    CONF_USERNAME,
    "api_key",
    "serial_number",
    "token",
}


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant,
    entry: IntegrationBlueprintConfigEntry,
) -> dict[str, Any]:
    """
    Return diagnostics for a config entry.

    Returns:
        The redacted entry configuration and the current coordinator state.

    """
    coordinator = entry.runtime_data.coordinator

    return {
        "entry": {
            "version": entry.version,
            "minor_version": entry.minor_version,
            "state": str(entry.state),
            "data": async_redact_data(entry.data, TO_REDACT),
            "options": async_redact_data(entry.options, TO_REDACT),
        },
        "coordinator": {
            "last_update_success": coordinator.last_update_success,
            "update_interval": str(coordinator.update_interval),
            "last_exception": str(coordinator.last_exception) if coordinator.last_exception else None,
            "data": async_redact_data(coordinator.data, TO_REDACT),
        },
    }
