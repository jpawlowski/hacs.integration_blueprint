"""Control switches for ha_integration_domain."""

from typing import TYPE_CHECKING, Any

from custom_components.ha_integration_domain.api import IntegrationBlueprintApiClientError
from custom_components.ha_integration_domain.const import LOGGER
from custom_components.ha_integration_domain.entity import IntegrationBlueprintEntity
from homeassistant.components.switch import SwitchDeviceClass, SwitchEntity, SwitchEntityDescription
from homeassistant.const import EntityCategory
from homeassistant.exceptions import HomeAssistantError

if TYPE_CHECKING:
    from custom_components.ha_integration_domain.coordinator import IntegrationBlueprintDataUpdateCoordinator

ENTITY_DESCRIPTIONS = (
    SwitchEntityDescription(
        key="child_lock",
        translation_key="child_lock",
        icon="mdi:lock",
        device_class=SwitchDeviceClass.SWITCH,
        entity_category=EntityCategory.CONFIG,
        has_entity_name=True,
    ),
    SwitchEntityDescription(
        key="led_display",
        translation_key="led_display",
        icon="mdi:led-on",
        device_class=SwitchDeviceClass.SWITCH,
        entity_category=EntityCategory.CONFIG,
        has_entity_name=True,
        entity_registry_enabled_default=False,
    ),
)


class IntegrationBlueprintSwitch(SwitchEntity, IntegrationBlueprintEntity):
    """Control switch class."""

    def __init__(
        self,
        coordinator: IntegrationBlueprintDataUpdateCoordinator,
        entity_description: SwitchEntityDescription,
    ) -> None:
        """Initialize the switch."""
        super().__init__(coordinator, entity_description)
        # Track state locally (in production, get from API)
        self._is_on = False

    @property
    def is_on(self) -> bool:
        """Return true if the switch is on."""
        return self._is_on

    @property
    def icon(self) -> str:
        """Return dynamic icon based on state."""
        if self.entity_description.key == "child_lock":
            return "mdi:lock" if self._is_on else "mdi:lock-open"
        if self.entity_description.key == "led_display":
            return "mdi:led-on" if self._is_on else "mdi:led-off"
        return self.entity_description.icon or "mdi:toggle-switch"

    async def async_turn_on(self, **_: Any) -> None:
        """Turn on the switch."""
        try:
            # In production: Call API to enable feature
            # await self.coordinator.config_entry.runtime_data.client.async_set_switch(
            #     self.entity_description.key, True
            # )
            self._is_on = True
            self.async_write_ha_state()
            LOGGER.debug("%s turned on", self.entity_description.key)
        except IntegrationBlueprintApiClientError as exception:
            LOGGER.exception("Failed to turn on %s", self.entity_description.key)
            raise HomeAssistantError(
                translation_domain="ha_integration_domain",
                translation_key="switch_turn_on_failed",
            ) from exception

    async def async_turn_off(self, **_: Any) -> None:
        """Turn off the switch."""
        try:
            # In production: Call API to disable feature
            # await self.coordinator.config_entry.runtime_data.client.async_set_switch(
            #     self.entity_description.key, False
            # )
            self._is_on = False
            self.async_write_ha_state()
            LOGGER.debug("%s turned off", self.entity_description.key)
        except IntegrationBlueprintApiClientError as exception:
            LOGGER.exception("Failed to turn off %s", self.entity_description.key)
            raise HomeAssistantError(
                translation_domain="ha_integration_domain",
                translation_key="switch_turn_off_failed",
            ) from exception
