"""
Event listeners and callbacks for coordinator state changes.

This module provides utilities for managing entity callbacks and event
listeners that respond to coordinator state changes.

Use cases:
- Entity-specific update callbacks
- State change notifications
- Performance monitoring and metrics
- Custom event handling for specific data changes
"""

from collections.abc import Awaitable, Callable

from custom_components.ha_integration_domain.const import LOGGER


def create_entity_callback(entity_id: str, callback: Callable[[], Awaitable[None]]) -> Callable[[], Awaitable[None]]:
    """
    Create a wrapped callback for an entity with logging.

    Args:
        entity_id: The ID of the entity this callback is for.
        callback: The async callback function to wrap.

    Returns:
        A wrapped callback that includes logging.

    Example:
        >>> async def update():
        ...     print("updating")
        >>> wrapped = create_entity_callback("sensor.test", update)
    """

    async def wrapped_callback() -> None:
        """Execute callback with error handling and logging."""
        try:
            await callback()
        except Exception:  # noqa: BLE001 - Must catch all callback errors to prevent coordinator crashes
            LOGGER.exception("Error in callback for %s", entity_id)

    return wrapped_callback


def should_notify_entity(old_data: dict, new_data: dict, entity_key: str) -> bool:
    """
    Determine if an entity should be notified about a data change.

    This can be used to reduce unnecessary updates when data hasn't
    meaningfully changed for a specific entity.

    Args:
        old_data: The previous coordinator data.
        new_data: The new coordinator data.
        entity_key: The key in the data dict this entity cares about.

    Returns:
        True if the entity should be notified, False otherwise.

    Example:
        >>> old = {"temperature": 20.0, "humidity": 50}
        >>> new = {"temperature": 20.1, "humidity": 50}
        >>> should_notify_entity(old, new, "humidity")
        False
    """
    # Check if the relevant data has changed
    if entity_key not in old_data and entity_key not in new_data:
        return False

    if entity_key not in old_data:
        return True  # New data available

    if entity_key not in new_data:
        return True  # Data removed

    # Compare values (could be made more sophisticated with thresholds)
    return old_data[entity_key] != new_data[entity_key]


def track_update_performance(update_duration: float) -> None:
    """
    Track and log coordinator update performance metrics.

    Args:
        update_duration: The time taken for the update in seconds.

    Example:
        >>> track_update_performance(0.5)  # 500ms update
    """
    threshold_slow = 5.0  # seconds
    threshold_warning = 10.0  # seconds

    if update_duration > threshold_warning:
        LOGGER.warning("Coordinator update took %.2f seconds (very slow)", update_duration)
    elif update_duration > threshold_slow:
        LOGGER.info("Coordinator update took %.2f seconds (slow)", update_duration)
    else:
        LOGGER.debug("Coordinator update took %.2f seconds", update_duration)
