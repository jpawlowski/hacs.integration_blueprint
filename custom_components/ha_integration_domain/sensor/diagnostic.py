"""Diagnostic sensors for ha_integration_domain."""

from typing import TYPE_CHECKING

from custom_components.ha_integration_domain.entity import IntegrationBlueprintEntity
from homeassistant.components.sensor import SensorDeviceClass, SensorEntity, SensorEntityDescription, SensorStateClass
from homeassistant.const import PERCENTAGE, EntityCategory, UnitOfTime

if TYPE_CHECKING:
    from datetime import datetime

    from custom_components.ha_integration_domain.coordinator import IntegrationBlueprintDataUpdateCoordinator

ENTITY_DESCRIPTIONS = (
    SensorEntityDescription(
        key="filter_life",
        translation_key="filter_life",
        icon="mdi:percent",
        entity_category=EntityCategory.DIAGNOSTIC,
        device_class=SensorDeviceClass.POWER_FACTOR,
        native_unit_of_measurement=PERCENTAGE,
        suggested_display_precision=0,
        state_class=SensorStateClass.MEASUREMENT,
        has_entity_name=True,
    ),
    SensorEntityDescription(
        key="runtime",
        translation_key="runtime",
        icon="mdi:timer-outline",
        entity_category=EntityCategory.DIAGNOSTIC,
        device_class=SensorDeviceClass.DURATION,
        native_unit_of_measurement=UnitOfTime.HOURS,
        state_class=SensorStateClass.TOTAL_INCREASING,
        suggested_display_precision=0,
        has_entity_name=True,
    ),
)


class IntegrationBlueprintDiagnosticSensor(SensorEntity, IntegrationBlueprintEntity):
    """Diagnostic sensor class for filter and runtime."""

    def __init__(
        self,
        coordinator: IntegrationBlueprintDataUpdateCoordinator,
        entity_description: SensorEntityDescription,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, entity_description)

    @property
    def native_value(self) -> int | float | datetime | None:
        """Return the native value of the sensor."""
        if not self.coordinator.last_update_success:
            return None

        user_id = self.coordinator.data.get("userId", 0)

        # Filter life remaining (0-100%)
        if self.entity_description.key == "filter_life":
            # Demo: If reset button was pressed, show 100%!
            if self.coordinator.data.get("demo_filter_reset"):
                return 100
            return 100 - (user_id % 100)

        # Total runtime in hours
        if self.entity_description.key == "runtime":
            return (user_id * 12) % 10000

        return None

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        # Diagnostic entities should always be available to show status
        return True
