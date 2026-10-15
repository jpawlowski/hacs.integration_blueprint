"""Base entity class for ha_integration_domain."""

from typing import TYPE_CHECKING

from custom_components.ha_integration_domain.api import IntegrationBlueprintApiClientError
from custom_components.ha_integration_domain.const import ATTRIBUTION, DOMAIN
from custom_components.ha_integration_domain.coordinator import IntegrationBlueprintDataUpdateCoordinator
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable

    from custom_components.ha_integration_domain.api import IntegrationBlueprintApiClient
    from homeassistant.helpers.entity import EntityDescription


class IntegrationBlueprintEntity(CoordinatorEntity[IntegrationBlueprintDataUpdateCoordinator]):
    """
    Base entity providing device info, unique ID and attribution.

    The unique ID is `{entry_id}_{key}`, the documented identifier of last resort.
    A real integration switches to the device's serial, MAC or account ID before its
    first release, because changing it afterwards needs a registry migration.
    """

    _attr_attribution = ATTRIBUTION
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: IntegrationBlueprintDataUpdateCoordinator,
        entity_description: EntityDescription,
    ) -> None:
        """Initialize the entity."""
        super().__init__(coordinator)
        self.entity_description = entity_description
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}_{entity_description.key}"
        self._attr_device_info = DeviceInfo(
            identifiers={
                (
                    coordinator.config_entry.domain,
                    coordinator.config_entry.entry_id,
                ),
            },
            name=coordinator.config_entry.title,
            manufacturer="Integration Blueprint",
            model=coordinator.data["model"],
            serial_number=coordinator.data["serial_number"],
            sw_version=coordinator.data["sw_version"],
        )

    async def _async_write(
        self,
        call: Callable[[IntegrationBlueprintApiClient], Awaitable[None]],
        translation_key: str,
        **placeholders: str,
    ) -> None:
        """
        Run a write against the device, then refresh the coordinator.

        Args:
            call: Receives the API client and performs the write.
            translation_key: Key of the exception message used when the write fails.
            **placeholders: Values for that message's placeholders.

        Raises:
            HomeAssistantError: If the device cannot be reached or rejects the write.

        """
        try:
            await call(self.coordinator.config_entry.runtime_data.client)
        except IntegrationBlueprintApiClientError as exception:
            raise HomeAssistantError(
                translation_domain=DOMAIN,
                translation_key=translation_key,
                translation_placeholders=placeholders or None,
            ) from exception

        await self.coordinator.async_request_refresh()
