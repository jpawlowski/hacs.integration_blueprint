"""Air quality sensors for ha_integration_domain."""

from __future__ import annotations

from typing import TYPE_CHECKING

from custom_components.ha_integration_domain.entity import IntegrationBlueprintEntity
from homeassistant.components.sensor import SensorDeviceClass, SensorEntity, SensorEntityDescription, SensorStateClass
from homeassistant.const import UnitOfDensity

if TYPE_CHECKING:
    from custom_components.ha_integration_domain.coordinator import IntegrationBlueprintDataUpdateCoordinator


ENTITY_DESCRIPTIONS = (
    SensorEntityDescription(
        key="air_quality_index",
        translation_key="air_quality_index",
        icon="mdi:gauge",
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.AQI,
        suggested_display_precision=0,
        has_entity_name=True,
    ),
    SensorEntityDescription(
        key="pm25",
        translation_key="pm25",
        icon="mdi:molecule",
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.PM25,
        native_unit_of_measurement=UnitOfDensity.MICROGRAMS_PER_CUBIC_METER,
        suggested_unit_of_measurement=UnitOfDensity.MICROGRAMS_PER_CUBIC_METER,
        suggested_display_precision=1,
        has_entity_name=True,
    ),
)


class IntegrationBlueprintAirQualitySensor(SensorEntity, IntegrationBlueprintEntity):
    """Air quality sensor class."""

    def __init__(
        self,
        coordinator: IntegrationBlueprintDataUpdateCoordinator,
        entity_description: SensorEntityDescription,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, entity_description)

    @property
    def native_value(self) -> int | float | None:
        """Return the native value of the sensor."""
        if not self.coordinator.last_update_success:
            return None

        # Get data from API response
        # In production: API would return actual air quality data
        # Example: {"userId": 1, "id": 1, "title": "...", "body": "..."}
        user_id = self.coordinator.data.get("userId", 0)
        api_id = self.coordinator.data.get("id", 0)

        # AQI (0-500 scale)
        if self.entity_description.key == "air_quality_index":
            # Simulate AQI based on API data (in production: use actual AQI from API)
            # Using both userId and id to create varied data
            return ((user_id * 47) + (api_id * 13)) % 501

        # PM2.5 concentration
        if self.entity_description.key == "pm25":
            # Simulate PM2.5 based on API data (in production: use actual PM2.5 from API)
            return round(((user_id * 23.7) + (api_id * 5.3)) % 300, 1)

        return None

    @property
    def extra_state_attributes(self) -> dict[str, str | int | float]:
        """Return additional state attributes."""
        # Base attributes from API
        attributes: dict[str, str | int | float] = {
            "api_source": "JSONPlaceholder",
            "data_id": self.coordinator.data.get("id", "unknown"),
        }

        if self.entity_description.key == "air_quality_index":
            aqi = self.native_value or 0
            # Determine air quality category
            if aqi <= 50:
                category = "Good"
            elif aqi <= 100:
                category = "Moderate"
            elif aqi <= 150:
                category = "Unhealthy for Sensitive Groups"
            elif aqi <= 200:
                category = "Unhealthy"
            elif aqi <= 300:
                category = "Very Unhealthy"
            else:
                category = "Hazardous"

            attributes.update(
                {
                    "air_quality_category": category,
                    "health_recommendation": "Keep windows closed" if aqi > 100 else "Safe to open windows",
                }
            )

        return attributes

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return self.coordinator.last_update_success
