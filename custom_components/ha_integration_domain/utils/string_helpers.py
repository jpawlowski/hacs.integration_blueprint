"""String helper utilities for ha_integration_domain."""

import re


def slugify_name(name: str) -> str:
    """
    Convert a name to a slug.

    Example:
        >>> slugify_name("My Device Name")
        'my_device_name'
    """
    # Convert to lowercase and replace spaces/special chars with underscores
    slug = re.sub(r"[^\w\s-]", "", name.lower())
    slug = re.sub(r"[-\s]+", "_", slug)
    return slug.strip("_")


def truncate_string(text: str, max_length: int = 255, suffix: str = "...") -> str:
    """
    Truncate a string to a maximum length.

    Args:
        text: The string to truncate
        max_length: Maximum length of the resulting string
        suffix: Suffix to append if truncated

    Returns:
        The truncated string with suffix if needed

    Example:
        >>> truncate_string("This is a very long text", 10)
        'This is...'
    """
    if len(text) <= max_length:
        return text

    truncate_at = max_length - len(suffix)
    return text[:truncate_at].rstrip() + suffix


def sanitize_string(text: str) -> str:
    """
    Remove potentially dangerous characters from a string.

    Args:
        text: The string to sanitize

    Returns:
        A sanitized string safe for use in filenames, IDs, etc.

    Example:
        >>> sanitize_string("My<>Device/Name")
        'MyDeviceName'
    """
    # Remove characters that might be problematic in filenames or IDs
    return re.sub(r'[<>:"/\\|?*\x00-\x1f]', "", text)
