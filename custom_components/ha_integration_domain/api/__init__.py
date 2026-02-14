"""
API package for ha_integration_domain.

Architecture:
    Three-layer data flow: Entities → Coordinator → API Client.
    Only the coordinator should call the API client. Entities must never
    import or call the API client directly.

Exception hierarchy:
    IntegrationBlueprintApiClientError (base)
    ├── IntegrationBlueprintApiClientCommunicationError (network/timeout)
    └── IntegrationBlueprintApiClientAuthenticationError (401/403)

Coordinator exception mapping:
    ApiClientAuthenticationError → ConfigEntryAuthFailed (triggers reauth)
    ApiClientCommunicationError → UpdateFailed (auto-retry)
    ApiClientError             → UpdateFailed (auto-retry)
"""

from .client import (
    IntegrationBlueprintApiClient,
    IntegrationBlueprintApiClientAuthenticationError,
    IntegrationBlueprintApiClientCommunicationError,
    IntegrationBlueprintApiClientError,
)

__all__ = [
    "IntegrationBlueprintApiClient",
    "IntegrationBlueprintApiClientAuthenticationError",
    "IntegrationBlueprintApiClientCommunicationError",
    "IntegrationBlueprintApiClientError",
]
