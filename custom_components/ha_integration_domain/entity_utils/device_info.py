"""Device info utilities for ha_integration_domain."""

from typing import TYPE_CHECKING, Any

from homeassistant.helpers.device_registry import DeviceInfo

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry


def create_device_info(
    config_entry: ConfigEntry,
    name: str | None = None,
    manufacturer: str | None = None,
    model: str | None = None,
    sw_version: str | None = None,
) -> DeviceInfo:
    """
    Create a DeviceInfo object for an entity.

    Args:
        config_entry: The config entry for the integration
        name: Optional device name
        manufacturer: Optional manufacturer name
        model: Optional model name
        sw_version: Optional software version

    Returns:
        A DeviceInfo object with the specified information

    Example:
        >>> device_info = create_device_info(
        ...     config_entry,
        ...     name="My Device",
        ...     manufacturer="Example Corp",
        ...     model="Model X",
        ... )
    """
    return DeviceInfo(
        identifiers={(config_entry.domain, config_entry.entry_id)},
        name=name or "Integration Blueprint",
        manufacturer=manufacturer or "Integration Blueprint",
        model=model or "Unknown",
        sw_version=sw_version,
    )


def update_device_info(
    base_info: DeviceInfo,
    **kwargs: Any,
) -> DeviceInfo:
    """
    Update a DeviceInfo object with new information.

    Args:
        base_info: The base DeviceInfo to update
        **kwargs: Key-value pairs to update in the DeviceInfo

    Returns:
        An updated DeviceInfo object

    Example:
        >>> updated_info = update_device_info(
        ...     base_info,
        ...     model="New Model",
        ...     sw_version="2.0.0",
        ... )
    """
    # Create a new DeviceInfo with updated values
    updated = dict(base_info)
    updated.update(kwargs)
    return DeviceInfo(**updated)  # type: ignore[arg-type]


def get_device_identifiers(config_entry: ConfigEntry) -> set[tuple[str, str]]:
    """
    Get device identifiers for a config entry.

    Args:
        config_entry: The config entry

    Returns:
        A set of device identifier tuples

    Example:
        >>> identifiers = get_device_identifiers(config_entry)
        >>> # Returns: {('ha_integration_domain', 'entry_id_value')}
    """
    return {(config_entry.domain, config_entry.entry_id)}
