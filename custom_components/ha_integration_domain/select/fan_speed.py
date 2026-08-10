"""Fan speed select for ha_integration_domain."""

from enum import StrEnum
from typing import TYPE_CHECKING

from custom_components.ha_integration_domain.const import LOGGER
from custom_components.ha_integration_domain.entity import IntegrationBlueprintEntity
from homeassistant.components.select import SelectEntity, SelectEntityDescription

if TYPE_CHECKING:
    from custom_components.ha_integration_domain.coordinator import IntegrationBlueprintDataUpdateCoordinator


class FanSpeed(StrEnum):
    """Fan speed enum."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    AUTO = "auto"


ENTITY_DESCRIPTIONS = (
    SelectEntityDescription(
        key="fan_speed",
        translation_key="fan_speed",
        icon="mdi:fan",
        options=[speed.value for speed in FanSpeed],
        has_entity_name=True,
    ),
)


class IntegrationBlueprintFanSpeedSelect(SelectEntity, IntegrationBlueprintEntity):
    """Fan speed select class."""

    def __init__(
        self,
        coordinator: IntegrationBlueprintDataUpdateCoordinator,
        entity_description: SelectEntityDescription,
    ) -> None:
        """Initialize the select."""
        super().__init__(coordinator, entity_description)
        # Initialize with auto mode
        self._attr_current_option = FanSpeed.AUTO

    @property
    def current_option(self) -> str | None:
        """
        Return the current selected option.

        Demo: This is linked to the fan entity - if you change the fan speed
        slider there, this select will also update!
        """
        # Check if fan entity has set a speed
        demo_speed = self.coordinator.data.get("demo_fan_speed")
        if demo_speed and demo_speed in [speed.value for speed in FanSpeed]:
            return demo_speed
        return self._attr_current_option

    @property
    def icon(self) -> str:
        """Return dynamic icon based on fan speed."""
        current = self.current_option or FanSpeed.AUTO
        if current == FanSpeed.LOW:
            return "mdi:fan-speed-1"
        if current == FanSpeed.MEDIUM:
            return "mdi:fan-speed-2"
        if current == FanSpeed.HIGH:
            return "mdi:fan-speed-3"
        return "mdi:fan-auto"

    async def async_select_option(self, option: str) -> None:
        """
        Change the selected option.

        Demo: This also updates the fan entity - they're linked!
        """
        LOGGER.debug("Setting fan speed to: %s", option)

        if option not in [speed.value for speed in FanSpeed]:
            LOGGER.error("Invalid fan speed: %s", option)
            return

        # In production: Call API to set fan speed
        # await self.coordinator.config_entry.runtime_data.client.async_set_fan_speed(option)

        # Store in coordinator data so fan entity can read it
        self.coordinator.data["demo_fan_speed"] = option

        self._attr_current_option = option

        # Request coordinator refresh - simulates: API call → device updates → fetch new state
        await self.coordinator.async_request_refresh()
        LOGGER.info("Fan speed changed to: %s", option)
