"""Number platform for ha_integration_domain."""

from typing import TYPE_CHECKING

from homeassistant.components.number import NumberEntityDescription

from .target_humidity import ENTITY_DESCRIPTIONS as HUMIDITY_DESCRIPTIONS, IntegrationBlueprintHumidityNumber

# Acts on the device: the coordinator does not limit outbound calls.
PARALLEL_UPDATES = 1

if TYPE_CHECKING:
    from custom_components.ha_integration_domain.data import IntegrationBlueprintConfigEntry
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

# Combine all entity descriptions from different modules
ENTITY_DESCRIPTIONS: tuple[NumberEntityDescription, ...] = (*HUMIDITY_DESCRIPTIONS,)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: IntegrationBlueprintConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the number platform."""
    async_add_entities(
        IntegrationBlueprintHumidityNumber(
            coordinator=entry.runtime_data.coordinator,
            entity_description=entity_description,
        )
        for entity_description in HUMIDITY_DESCRIPTIONS
    )
