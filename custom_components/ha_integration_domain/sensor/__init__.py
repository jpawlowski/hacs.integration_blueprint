"""Sensor platform for ha_integration_domain."""

from typing import TYPE_CHECKING

from homeassistant.components.sensor import SensorEntityDescription

from .air_quality import ENTITY_DESCRIPTIONS as AIR_QUALITY_DESCRIPTIONS, IntegrationBlueprintAirQualitySensor
from .diagnostic import ENTITY_DESCRIPTIONS as DIAGNOSTIC_DESCRIPTIONS, IntegrationBlueprintDiagnosticSensor

# Read-only platform: the coordinator already serializes the fetch.
PARALLEL_UPDATES = 0

if TYPE_CHECKING:
    from custom_components.ha_integration_domain.data import IntegrationBlueprintConfigEntry
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

# Combine all entity descriptions from different modules
ENTITY_DESCRIPTIONS: tuple[SensorEntityDescription, ...] = (
    *AIR_QUALITY_DESCRIPTIONS,
    *DIAGNOSTIC_DESCRIPTIONS,
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: IntegrationBlueprintConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the sensor platform."""
    # Add air quality sensors
    async_add_entities(
        IntegrationBlueprintAirQualitySensor(
            coordinator=entry.runtime_data.coordinator,
            entity_description=entity_description,
        )
        for entity_description in AIR_QUALITY_DESCRIPTIONS
    )
    # Add diagnostic sensors
    async_add_entities(
        IntegrationBlueprintDiagnosticSensor(
            coordinator=entry.runtime_data.coordinator,
            entity_description=entity_description,
        )
        for entity_description in DIAGNOSTIC_DESCRIPTIONS
    )
