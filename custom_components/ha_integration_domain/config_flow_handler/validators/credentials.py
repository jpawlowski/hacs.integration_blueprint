"""
Credential validators.

Validation functions for user credentials and authentication.

When this file grows, consider splitting into:
- credentials.py: Basic credential validation
- oauth.py: OAuth-specific validation
- api_auth.py: API authentication methods
"""

from typing import TYPE_CHECKING

from custom_components.ha_integration_domain.api import IntegrationBlueprintApiClient
from homeassistant.helpers.aiohttp_client import async_create_clientsession

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant


async def validate_credentials(hass: HomeAssistant, username: str, password: str) -> None:
    """
    Validate user credentials by testing API connection.

    Args:
        hass: Home Assistant instance.
        username: The username to validate.
        password: The password to validate.

    Raises:
        IntegrationBlueprintApiClientAuthenticationError: If credentials are invalid.
        IntegrationBlueprintApiClientCommunicationError: If communication fails.
        IntegrationBlueprintApiClientError: For other API errors.

    """
    client = IntegrationBlueprintApiClient(
        username=username,
        password=password,
        session=async_create_clientsession(hass),
    )
    await client.async_get_data()  # May raise authentication/communication errors


__all__ = [
    "validate_credentials",
]
