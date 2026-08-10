"""Example service action handlers for ha_integration_domain."""

from typing import TYPE_CHECKING

from custom_components.ha_integration_domain.const import LOGGER
from homeassistant.exceptions import ConfigEntryAuthFailed, ConfigEntryNotReady
from homeassistant.helpers.update_coordinator import UpdateFailed
from homeassistant.util import dt as dt_util

if TYPE_CHECKING:
    from custom_components.ha_integration_domain.data import IntegrationBlueprintConfigEntry
    from homeassistant.core import HomeAssistant, ServiceCall, ServiceResponse


async def async_handle_example_action(
    hass: HomeAssistant,
    entry: IntegrationBlueprintConfigEntry,
    call: ServiceCall,
) -> None:
    """
    Handle the example_action service action call.

    This is a dummy service action that demonstrates how to implement custom service actions.

    Args:
        hass: Home Assistant instance
        entry: Config entry for the integration
        call: Service call data
    """
    LOGGER.info("Example action service called with data: %s", call.data)

    # Example: Access the coordinator
    # coordinator = entry.runtime_data.coordinator

    # Example: Access the API client
    # client = entry.runtime_data.client

    # Example: Do something with the service call data
    action_type = call.data.get("action_type", "default")
    target_value = call.data.get("target_value")

    LOGGER.debug(
        "Processing action type: %s with target value: %s",
        action_type,
        target_value,
    )

    # In a real implementation, you would:
    # - Validate the input
    # - Call API methods via client
    # - Update coordinator data if needed
    # - Handle errors appropriately

    # For now, this is just a dummy that logs the action
    LOGGER.info("Example action completed successfully")


async def async_handle_reload_data(
    hass: HomeAssistant,
    entry: IntegrationBlueprintConfigEntry,
    call: ServiceCall,
) -> ServiceResponse:
    """
    Handle the reload_data service call with response data.

    This service forces a refresh of the integration data and returns
    diagnostic information about the refresh operation.

    Args:
        hass: Home Assistant instance
        entry: Config entry for the integration
        call: Service call data

    Returns:
        ServiceResponse: Dictionary with refresh status, timestamp, and data summary
    """
    LOGGER.info("Reload data service called")

    # Access the coordinator and trigger a refresh
    coordinator = entry.runtime_data.coordinator
    start_time = dt_util.now()

    try:
        await coordinator.async_request_refresh()
    except (UpdateFailed, ConfigEntryAuthFailed, ConfigEntryNotReady) as exception:
        LOGGER.exception("Failed to reload data: %s", exception)
        # Return error response instead of raising
        return {
            "status": "error",
            "timestamp": dt_util.now().isoformat(),
            "error": str(exception),
            "error_type": type(exception).__name__,
        }
    else:
        end_time = dt_util.now()
        duration_ms = (end_time - start_time).total_seconds() * 1000

        # Count records in coordinator data
        data_size = len(str(coordinator.data)) if coordinator.data else 0
        record_count = len(coordinator.data) if isinstance(coordinator.data, dict) else 0

        response_data: ServiceResponse = {
            "status": "success",
            "timestamp": end_time.isoformat(),
            "duration_ms": round(duration_ms, 2),
            "record_count": record_count,
            "data_size_bytes": data_size,
            "last_update_success": coordinator.last_update_success,
        }

        LOGGER.info(
            "Data reload completed successfully in %.2fms with %d records",
            duration_ms,
            record_count,
        )
        return response_data
