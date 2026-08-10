"""Validation utilities for ha_integration_domain."""

from typing import Any


def validate_api_response(response: dict[str, Any]) -> bool:
    """
    Validate that an API response has the expected structure.

    Args:
        response: The API response to validate

    Returns:
        True if valid, False otherwise

    Example:
        >>> validate_api_response({"title": "foo", "body": "bar"})
        True
    """
    if not isinstance(response, dict):
        return False

    # Check for expected fields
    required_fields = ["title", "body"]
    return all(field in response for field in required_fields)


def validate_config_value(value: Any, value_type: type, min_val: Any = None, max_val: Any = None) -> bool:
    """
    Validate a configuration value.

    Args:
        value: The value to validate
        value_type: Expected type of the value
        min_val: Optional minimum value (for numeric types)
        max_val: Optional maximum value (for numeric types)

    Returns:
        True if valid, False otherwise

    Example:
        >>> validate_config_value(5, int, min_val=1, max_val=10)
        True
        >>> validate_config_value(15, int, min_val=1, max_val=10)
        False
    """
    if not isinstance(value, value_type):
        return False

    if min_val is not None and value < min_val:
        return False

    if max_val is not None and value > max_val:
        return False

    return True


def is_valid_url(url: str) -> bool:
    """
    Check if a string is a valid URL.

    Args:
        url: The URL string to validate

    Returns:
        True if valid URL, False otherwise

    Example:
        >>> is_valid_url("https://example.com")
        True
        >>> is_valid_url("not a url")
        False
    """
    if not isinstance(url, str):
        return False

    # Simple URL validation
    return url.startswith(("http://", "https://")) and len(url) > 8
