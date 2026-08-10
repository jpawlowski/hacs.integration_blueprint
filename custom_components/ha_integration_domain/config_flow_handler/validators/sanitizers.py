"""
Input sanitizers and normalizers.

Functions for cleaning and normalizing user inputs.

When adding many sanitizers, consider organizing by type:
- text.py: Text input sanitizers
- network.py: URL, host, port sanitizers
- identifiers.py: Device ID, serial number normalizers
"""


def sanitize_username(username: str) -> str:
    """
    Sanitize username input.

    This function can be extended to normalize usernames (e.g., lowercase,
    trim whitespace) depending on API requirements.

    Args:
        username: Raw username input.

    Returns:
        Sanitized username.

    """
    return username.strip()


__all__ = [
    "sanitize_username",
]
