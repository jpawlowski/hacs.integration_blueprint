"""Air purifier fan entity for ha_integration_domain."""

from typing import Any

from custom_components.ha_integration_domain.api import IntegrationBlueprintApiClientError
from custom_components.ha_integration_domain.const import DOMAIN
from custom_components.ha_integration_domain.entity import IntegrationBlueprintEntity
from homeassistant.components.fan import FanEntity, FanEntityDescription, FanEntityFeature
from homeassistant.exceptions import HomeAssistantError
from homeassistant.util.percentage import percentage_to_ordered_list_item

ORDERED_SPEEDS = ["low", "medium", "high"]

# The fan is the device's main feature, so name=None makes its friendly name the
# device name alone — otherwise the UI reads "Air Purifier Air Purifier".
ENTITY_DESCRIPTIONS: tuple[FanEntityDescription, ...] = (
    FanEntityDescription(
        key="air_purifier",
        name=None,
    ),
)


class IntegrationBlueprintFan(FanEntity, IntegrationBlueprintEntity):
    """The air purifier's fan."""

    _attr_supported_features = FanEntityFeature.SET_SPEED | FanEntityFeature.TURN_ON | FanEntityFeature.TURN_OFF
    _attr_speed_count = len(ORDERED_SPEEDS)

    @property
    def is_on(self) -> bool | None:
        """Return whether the fan is running."""
        return self.coordinator.data.get("fan_on")

    @property
    def percentage(self) -> int | None:
        """Return the current speed as a percentage."""
        return self.coordinator.data.get("fan_percentage")

    async def async_set_percentage(self, percentage: int) -> None:
        """Set the fan speed."""
        if percentage == 0:
            await self.async_turn_off()
            return

        speed = percentage_to_ordered_list_item(ORDERED_SPEEDS, percentage)
        client = self.coordinator.config_entry.runtime_data.client
        try:
            await client.async_set_fan_speed(speed)
        except IntegrationBlueprintApiClientError as exception:
            raise HomeAssistantError(
                translation_domain=DOMAIN,
                translation_key="fan_speed_set_failed",
            ) from exception

        await self.coordinator.async_request_refresh()

    async def async_turn_on(
        self,
        percentage: int | None = None,
        preset_mode: str | None = None,
        **kwargs: Any,
    ) -> None:
        """Turn the fan on, optionally at a given speed."""
        if percentage is not None:
            await self.async_set_percentage(percentage)
            return

        await self._async_set_state(is_on=True)

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the fan off."""
        await self._async_set_state(is_on=False)

    async def _async_set_state(self, *, is_on: bool) -> None:
        """Write the on/off state to the device and refresh."""
        client = self.coordinator.config_entry.runtime_data.client
        try:
            await client.async_set_fan_state(is_on=is_on)
        except IntegrationBlueprintApiClientError as exception:
            raise HomeAssistantError(
                translation_domain=DOMAIN,
                translation_key="fan_state_set_failed",
            ) from exception

        await self.coordinator.async_request_refresh()
