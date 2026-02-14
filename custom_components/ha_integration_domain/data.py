"""
Custom types for ha_integration_domain.

This module defines the runtime data structure attached to each config entry.
Access pattern: entry.runtime_data.client / entry.runtime_data.coordinator

The IntegrationBlueprintConfigEntry type alias is used throughout the integration
for type-safe access to the config entry's runtime data.
"""

from __future__ import annotations

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
    """Runtime data for ha_integration_domain config entries.

    Stored as entry.runtime_data after successful setup.
    Provides typed access to the API client and coordinator instances.
    """

    client: IntegrationBlueprintApiClient
    coordinator: IntegrationBlueprintDataUpdateCoordinator
    integration: Integration
