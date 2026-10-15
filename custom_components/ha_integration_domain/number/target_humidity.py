"""Target humidity number for ha_integration_domain."""

from custom_components.ha_integration_domain.entity import IntegrationBlueprintEntity
from homeassistant.components.number import NumberDeviceClass, NumberEntity, NumberEntityDescription, NumberMode
from homeassistant.const import PERCENTAGE

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
        await self._async_write(lambda client: client.async_set_target_humidity(value), "number_set_failed")
