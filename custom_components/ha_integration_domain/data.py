"""
Runtime data types for ha_integration_domain.

Access pattern: entry.runtime_data.client / entry.runtime_data.coordinator
"""

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.loader import Integration

    from .api import IntegrationBlueprintApiClient
    from .coordinator import IntegrationBlueprintDataUpdateCoordinator


type IntegrationBlueprintConfigEntry = ConfigEntry[IntegrationBlueprintData]


@dataclass
class IntegrationBlueprintData:
    """Runtime data stored on the config entry after a successful setup."""

    client: IntegrationBlueprintApiClient
    coordinator: IntegrationBlueprintDataUpdateCoordinator
    integration: Integration
