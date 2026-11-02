"""
API package for ha_integration_domain.

Exception hierarchy:
    IntegrationBlueprintApiClientError (base)
    ├── IntegrationBlueprintApiClientCommunicationError (network/timeout)
    │   └── IntegrationBlueprintApiClientRateLimitError (429, carries retry_after)
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
    IntegrationBlueprintApiClientRateLimitError,
)

__all__ = [
    "FAN_SPEEDS",
    "IntegrationBlueprintApiClient",
    "IntegrationBlueprintApiClientAuthenticationError",
    "IntegrationBlueprintApiClientCommunicationError",
    "IntegrationBlueprintApiClientError",
    "IntegrationBlueprintApiClientRateLimitError",
]
