"""Button platform for ha_integration_domain."""

from typing import TYPE_CHECKING

from .reset_filter import ENTITY_DESCRIPTIONS, IntegrationBlueprintButton

# Acts on the device: the coordinator does not limit outbound calls.
PARALLEL_UPDATES = 1

if TYPE_CHECKING:
    from custom_components.ha_integration_domain.data import IntegrationBlueprintConfigEntry
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback


async def async_setup_entry(
    hass: HomeAssistant,
    entry: IntegrationBlueprintConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the button platform."""
    async_add_entities(
        IntegrationBlueprintButton(entry.runtime_data.coordinator, description) for description in ENTITY_DESCRIPTIONS
    )
