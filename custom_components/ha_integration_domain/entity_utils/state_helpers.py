"""State helper utilities for ha_integration_domain."""

from datetime import datetime
from typing import Any


def format_state_value(value: Any, unit: str | None = None) -> str:
    """
    Format a state value for display.

    Args:
        value: The value to format
        unit: Optional unit to append

    Returns:
        A formatted string representation of the value

    Example:
        >>> format_state_value(25.5, "°C")
        '25.5 °C'
        >>> format_state_value(True)
        'on'
    """
    if isinstance(value, bool):
        return "on" if value else "off"

    if isinstance(value, (int, float)):
        formatted = f"{value:.2f}" if isinstance(value, float) else str(value)
        return f"{formatted} {unit}" if unit else formatted

    if isinstance(value, datetime):
        return value.isoformat()

    return str(value) if value is not None else "unknown"


def parse_state_attributes(data: dict[str, Any]) -> dict[str, Any]:
    """
    Parse and extract state attributes from raw data.

    Args:
        data: Raw data from the API

    Returns:
        A dictionary of state attributes

    Example:
        >>> parse_state_attributes({"title": "foo", "body": "bar", "userId": 1})
        {'user_id': 1, 'has_content': True}
    """
    attributes = {}

    # Extract user ID if present
    if "userId" in data:
        attributes["user_id"] = data["userId"]

    # Extract title if present
    if "title" in data:
        attributes["title"] = data["title"]

    # Add computed attributes
    if "body" in data:
        attributes["has_content"] = bool(data["body"])
        attributes["content_length"] = len(data["body"]) if data["body"] else 0

    return attributes


def merge_state_attributes(
    base_attrs: dict[str, Any],
    new_attrs: dict[str, Any],
    preserve_keys: list[str] | None = None,
) -> dict[str, Any]:
    """
    Merge new state attributes with existing ones.

    Args:
        base_attrs: Base attributes
        new_attrs: New attributes to merge
        preserve_keys: Optional list of keys to preserve from base_attrs

    Returns:
        Merged attributes dictionary

    Example:
        >>> base = {"key1": "value1", "key2": "value2"}
        >>> new = {"key2": "new_value2", "key3": "value3"}
        >>> merge_state_attributes(base, new, preserve_keys=["key1"])
        {'key1': 'value1', 'key2': 'new_value2', 'key3': 'value3'}
    """
    merged = dict(base_attrs)

    # Update with new attributes
    merged.update(new_attrs)

    # Restore preserved keys if specified
    if preserve_keys:
        for key in preserve_keys:
            if key in base_attrs:
                merged[key] = base_attrs[key]

    return merged


def calculate_derived_state(data: dict[str, Any]) -> dict[str, Any]:
    """
    Calculate derived state values from raw data.

    Args:
        data: Raw data from the API

    Returns:
        A dictionary of derived state values

    Example:
        >>> calculate_derived_state({"title": "foo", "body": "bar"})
        {'is_active': True, 'data_quality': 'good'}
    """
    derived = {}

    # Example: Determine if the entity is "active" based on title
    derived["is_active"] = data.get("title") == "foo"

    # Example: Assess data quality
    if "title" in data and "body" in data:
        derived["data_quality"] = "good"
    elif "title" in data or "body" in data:
        derived["data_quality"] = "partial"
    else:
        derived["data_quality"] = "poor"

    return derived
