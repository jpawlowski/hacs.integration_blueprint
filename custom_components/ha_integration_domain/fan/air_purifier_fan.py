"""Air purifier fan entity for ha_integration_domain."""

import math
from typing import TYPE_CHECKING, Any

from custom_components.ha_integration_domain.api import IntegrationBlueprintApiClientError
from custom_components.ha_integration_domain.const import LOGGER
from custom_components.ha_integration_domain.entity import IntegrationBlueprintEntity
from homeassistant.components.fan import FanEntity, FanEntityDescription, FanEntityFeature
from homeassistant.exceptions import HomeAssistantError
from homeassistant.util.percentage import percentage_to_ranged_value

if TYPE_CHECKING:
    from custom_components.ha_integration_domain.coordinator import IntegrationBlueprintDataUpdateCoordinator

# Speed range for percentage calculations (Low=1, Medium=2, High=3)
SPEED_RANGE = (1, 3)

ENTITY_DESCRIPTIONS = (
    FanEntityDescription(
        key="air_purifier",
        translation_key="air_purifier",
        icon="mdi:air-purifier",
        has_entity_name=True,
    ),
)


class IntegrationBlueprintFan(FanEntity, IntegrationBlueprintEntity):
    """
    Air purifier fan entity.

    This entity is linked to the fan_speed select entity - they control the same thing.
    When you change one, the other updates automatically.
    """

    _attr_supported_features = FanEntityFeature.SET_SPEED | FanEntityFeature.TURN_ON | FanEntityFeature.TURN_OFF
    _attr_speed_count = 3  # Low, Medium, High (Auto is handled separately)

    def __init__(
        self,
        coordinator: IntegrationBlueprintDataUpdateCoordinator,
        entity_description: FanEntityDescription,
    ) -> None:
        """Initialize the fan."""
        super().__init__(coordinator, entity_description)
        # Track state locally (in production, get from API)
        self._is_on = True
        self._percentage = 66  # Default to Medium (66%)

    @property
    def is_on(self) -> bool:
        """Return true if fan is on."""
        # Check if the select entity has "auto" selected
        # In that case, we're always "on"
        return self._is_on

    @property
    def percentage(self) -> int | None:
        """Return the current speed percentage."""
        if not self.is_on:
            return 0
        return self._percentage

    async def async_set_percentage(self, percentage: int) -> None:
        """
        Set the speed percentage of the fan.

        This also updates the fan_speed select entity to match.
        """
        try:
            if percentage == 0:
                await self.async_turn_off()
                return

            # Convert percentage to speed value (1-3)
            speed_value = math.ceil(percentage_to_ranged_value(SPEED_RANGE, percentage))

            # Map to speed name for API call
            speed_map = {1: "low", 2: "medium", 3: "high"}
            speed_name = speed_map.get(speed_value, "medium")

            # In production: Send to API
            # await self.coordinator.config_entry.runtime_data.client.async_set_fan_speed(speed_name)

            self._percentage = percentage
            self._is_on = True

            # Store in coordinator data for select entity to read
            # This creates a link: when you change the fan speed here,
            # the fan_speed select entity will also update
            self.coordinator.data["demo_fan_speed"] = speed_name

            # Request coordinator refresh - simulates: API call → device updates → fetch new state
            await self.coordinator.async_request_refresh()

            LOGGER.debug("Fan speed set to %s (%d%%)", speed_name, percentage)

        except IntegrationBlueprintApiClientError as exception:
            msg = f"Failed to set fan speed: {exception}"
            raise HomeAssistantError(msg) from exception

    async def async_turn_on(
        self,
        percentage: int | None = None,
        preset_mode: str | None = None,
        **kwargs: Any,
    ) -> None:
        """Turn on the fan."""
        if percentage is not None:
            await self.async_set_percentage(percentage)
        else:
            self._is_on = True
            self.async_write_ha_state()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn off the fan."""
        self._is_on = False
        self._percentage = 0
        self.async_write_ha_state()
