"""
API package for ha_integration_domain.

Exception hierarchy:
    IntegrationBlueprintApiClientError (base)
    ├── IntegrationBlueprintApiClientCommunicationError (network/timeout)
    └── IntegrationBlueprintApiClientAuthenticationError (401/403)

The coordinator maps them onto ConfigEntryAuthFailed and UpdateFailed; nothing else
in the integration imports this package.
"""

from .client import (
    FAN_SPEEDS,
    IntegrationBlueprintApiClient,
    IntegrationBlueprintApiClientAuthenticationError,
    IntegrationBlueprintApiClientCommunicationError,
    IntegrationBlueprintApiClientError,
)

__all__ = [
    "FAN_SPEEDS",
    "IntegrationBlueprintApiClient",
    "IntegrationBlueprintApiClientAuthenticationError",
    "IntegrationBlueprintApiClientCommunicationError",
    "IntegrationBlueprintApiClientError",
]
