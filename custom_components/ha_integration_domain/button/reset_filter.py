"""Reset filter button for ha_integration_domain."""

from typing import TYPE_CHECKING

from custom_components.ha_integration_domain.api import IntegrationBlueprintApiClientError
from custom_components.ha_integration_domain.const import LOGGER
from custom_components.ha_integration_domain.entity import IntegrationBlueprintEntity
from homeassistant.components.button import ButtonDeviceClass, ButtonEntity, ButtonEntityDescription
from homeassistant.const import EntityCategory
from homeassistant.exceptions import HomeAssistantError

if TYPE_CHECKING:
    from custom_components.ha_integration_domain.coordinator import IntegrationBlueprintDataUpdateCoordinator

ENTITY_DESCRIPTIONS = (
    ButtonEntityDescription(
        key="reset_filter",
        translation_key="reset_filter",
        icon="mdi:restart",
        device_class=ButtonDeviceClass.RESTART,
        entity_category=EntityCategory.CONFIG,
        has_entity_name=True,
    ),
)


class IntegrationBlueprintButton(ButtonEntity, IntegrationBlueprintEntity):
    """Reset filter button class."""

    def __init__(
        self,
        coordinator: IntegrationBlueprintDataUpdateCoordinator,
        entity_description: ButtonEntityDescription,
    ) -> None:
        """Initialize the button."""
        super().__init__(coordinator, entity_description)

    async def async_press(self) -> None:
        """
        Handle the button press.

        This simulates resetting the filter timer. In a real integration,
        this would send an API command to reset the device's filter counter.

        Demo: This also affects the filter_life sensor - watch it jump to 100%!
        """
        try:
            # In production: Send reset command to device
            # await self.coordinator.config_entry.runtime_data.client.async_reset_filter()

            # For demo: Store reset flag in coordinator data
            # The filter_life sensor will read this and show 100%
            self.coordinator.data["demo_filter_reset"] = True

            # Request a coordinator refresh - this simulates the real flow:
            # 1. API call to device (commented out above)
            # 2. Coordinator fetches updated data from device
            # 3. All entities get updated with fresh data
            await self.coordinator.async_request_refresh()

            LOGGER.info("Filter timer reset successfully")

        except IntegrationBlueprintApiClientError as exception:
            msg = f"Failed to reset filter: {exception}"
            raise HomeAssistantError(msg) from exception
