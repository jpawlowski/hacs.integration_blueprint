"""Air quality sensor descriptions for ha_integration_domain."""

from homeassistant.components.sensor import SensorDeviceClass, SensorStateClass
from homeassistant.const import UnitOfDensity

from .entity import IntegrationBlueprintSensorEntityDescription

# SensorDeviceClass.AQI and .PM25 already name these entities, so they carry no
# translation_key — adding one would only create a redundant key for translators.
ENTITY_DESCRIPTIONS: tuple[IntegrationBlueprintSensorEntityDescription, ...] = (
    IntegrationBlueprintSensorEntityDescription(
        key="air_quality_index",
        device_class=SensorDeviceClass.AQI,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=0,
        value_fn=lambda data: data.get("air_quality_index"),
    ),
    IntegrationBlueprintSensorEntityDescription(
        key="pm25",
        device_class=SensorDeviceClass.PM25,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfDensity.MICROGRAMS_PER_CUBIC_METER,
        suggested_display_precision=1,
        value_fn=lambda data: data.get("pm25"),
    ),
)
