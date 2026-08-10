"""Diagnostics support for ha_integration_domain.

Learn more about diagnostics:
https://developers.home-assistant.io/docs/core/integration_diagnostics
"""

from typing import TYPE_CHECKING, Any

from homeassistant.const import CONF_PASSWORD, CONF_USERNAME
from homeassistant.helpers import device_registry as dr, entity_registry as er
from homeassistant.helpers.redact import async_redact_data

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant

    from .data import IntegrationBlueprintConfigEntry

# Fields to redact from diagnostics - CRITICAL for security!
TO_REDACT = {
    CONF_PASSWORD,
    CONF_USERNAME,
    "username",
    "password",
    "api_key",
    "token",
}


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant,
    entry: IntegrationBlueprintConfigEntry,
) -> dict[str, Any]:
    """Return diagnostics for a config entry."""
    coordinator = entry.runtime_data.coordinator
    client = entry.runtime_data.client
    integration = entry.runtime_data.integration

    # Get device and entity information
    device_reg = dr.async_get(hass)
    entity_reg = er.async_get(hass)

    # Find all devices for this integration
    devices = dr.async_entries_for_config_entry(device_reg, entry.entry_id)
    device_info = []
    for device in devices:
        entities = er.async_entries_for_device(entity_reg, device.id)
        device_info.append(
            {
                "id": device.id,
                "name": device.name,
                "manufacturer": device.manufacturer,
                "model": device.model,
                "sw_version": device.sw_version,
                "entity_count": len(entities),
                "entities": [
                    {
                        "entity_id": entity.entity_id,
                        "platform": entity.platform,
                        "original_name": entity.original_name,
                        "disabled": entity.disabled,
                        "disabled_by": entity.disabled_by.value if entity.disabled_by else None,
                    }
                    for entity in entities
                ],
            }
        )

    # Coordinator statistics
    coordinator_info = {
        "last_update_success": coordinator.last_update_success,
        "update_interval": str(coordinator.update_interval),
        "data_keys": list(coordinator.data.keys()) if isinstance(coordinator.data, dict) else None,
    }

    # API client information (no sensitive data)
    api_info = {
        "base_endpoint": "https://jsonplaceholder.typicode.com",
        "has_credentials": bool(client._username),  # noqa: SLF001
    }

    # Integration information
    integration_info = {
        "name": integration.name,
        "version": integration.version,
        "domain": integration.domain,
        "documentation": integration.documentation,
        "issue_tracker": integration.issue_tracker,
    }

    # Config entry details (with redacted sensitive data)
    entry_info = {
        "entry_id": entry.entry_id,
        "version": entry.version,
        "minor_version": entry.minor_version,
        "domain": entry.domain,
        "title": entry.title,
        "state": str(entry.state),
        "unique_id": entry.unique_id,
        "disabled_by": entry.disabled_by.value if entry.disabled_by else None,
        "data": async_redact_data(entry.data, TO_REDACT),
        "options": async_redact_data(entry.options, TO_REDACT),
    }

    # Error information
    error_info = {
        "last_exception": str(coordinator.last_exception) if coordinator.last_exception else None,
        "last_exception_type": (type(coordinator.last_exception).__name__ if coordinator.last_exception else None),
    }

    # Current data sample (sanitized)
    data_sample = {}
    if coordinator.data:
        if isinstance(coordinator.data, dict):
            # Include sample data but sanitize sensitive info
            data_sample = {
                "title": coordinator.data.get("title"),
                "body_length": len(coordinator.data.get("body", "")) if coordinator.data.get("body") else 0,
                "has_user_id": "userId" in coordinator.data,
            }

    return {
        "entry": entry_info,
        "integration": integration_info,
        "coordinator": coordinator_info,
        "api": api_info,
        "devices": device_info,
        "data_sample": data_sample,
        "error": error_info,
    }
