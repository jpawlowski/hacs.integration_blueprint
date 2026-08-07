"""Tests for Home Assistant 2026.8 config-entry-scoped device ownership."""

from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.ha_integration_domain.const import DOMAIN
from custom_components.ha_integration_domain.entity_utils.device_info import create_device_info
from homeassistant.helpers import device_registry as dr


async def test_blueprint_device_info_creates_one_device_per_config_entry(hass) -> None:
    """Verify the blueprint creates a distinct device for every config entry."""
    first_entry = MockConfigEntry(domain=DOMAIN, entry_id="first-entry")
    second_entry = MockConfigEntry(domain=DOMAIN, entry_id="second-entry")
    first_entry.add_to_hass(hass)
    second_entry.add_to_hass(hass)

    device_registry = dr.async_get(hass)
    identifier = (DOMAIN, "shared-device-id")
    first_device_info = create_device_info(first_entry)
    first_device_info["identifiers"] = {identifier}
    second_device_info = create_device_info(second_entry)
    second_device_info["identifiers"] = {identifier}

    first_device = device_registry.async_get_or_create(
        config_entry_id=first_entry.entry_id,
        **first_device_info,
    )
    second_device = device_registry.async_get_or_create(
        config_entry_id=second_entry.entry_id,
        **second_device_info,
    )

    assert first_device.id != second_device.id
    assert first_device.config_entry_id == first_entry.entry_id
    assert second_device.config_entry_id == second_entry.entry_id
    assert device_registry.async_get_device_by_identifier(identifier, first_entry.entry_id) == first_device
    assert device_registry.async_get_device_by_identifier(identifier, second_entry.entry_id) == second_device
