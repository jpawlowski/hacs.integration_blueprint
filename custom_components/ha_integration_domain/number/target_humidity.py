"""Target humidity number for ha_integration_domain."""

from custom_components.ha_integration_domain.api import IntegrationBlueprintApiClientError
from custom_components.ha_integration_domain.const import DOMAIN
from custom_components.ha_integration_domain.entity import IntegrationBlueprintEntity
from homeassistant.components.number import NumberDeviceClass, NumberEntity, NumberEntityDescription, NumberMode
from homeassistant.const import PERCENTAGE
from homeassistant.exceptions import HomeAssistantError

ENTITY_DESCRIPTIONS: tuple[NumberEntityDescription, ...] = (
    NumberEntityDescription(
        key="target_humidity",
        translation_key="target_humidity",
        device_class=NumberDeviceClass.HUMIDITY,
        native_unit_of_measurement=PERCENTAGE,
        native_min_value=30,
        native_max_value=80,
        native_step=5,
        mode=NumberMode.SLIDER,
    ),
)


class IntegrationBlueprintHumidityNumber(NumberEntity, IntegrationBlueprintEntity):
    """Number entity for the device's target humidity."""

    @property
    def native_value(self) -> float | None:
        """Return the target humidity read from coordinator data."""
        return self.coordinator.data.get("target_humidity")

    async def async_set_native_value(self, value: float) -> None:
        """Write the target humidity to the device."""
        client = self.coordinator.config_entry.runtime_data.client
        try:
            await client.async_set_target_humidity(value)
        except IntegrationBlueprintApiClientError as exception:
            raise HomeAssistantError(
                translation_domain=DOMAIN,
                translation_key="number_set_failed",
            ) from exception

        await self.coordinator.async_request_refresh()
