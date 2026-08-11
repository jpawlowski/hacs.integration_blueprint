"""Tests for Home Assistant 2026.8 config-entry-scoped device ownership."""

from unittest.mock import AsyncMock

from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.ha_integration_domain.const import DOMAIN
from homeassistant.config_entries import ConfigEntryState
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME
from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr


async def test_entry_owns_its_own_device(init_integration: MockConfigEntry, hass: HomeAssistant) -> None:
    """A loaded entry registers exactly one device, owned by that entry."""
    assert init_integration.state is ConfigEntryState.LOADED

    devices = dr.async_entries_for_config_entry(dr.async_get(hass), init_integration.entry_id)

    assert len(devices) == 1
    assert devices[0].config_entry_id == init_integration.entry_id
    assert devices[0].model == "Blueprint Air Purifier"


async def test_two_entries_get_separate_devices(
    hass: HomeAssistant,
    mock_api: AsyncMock,
    init_integration: MockConfigEntry,
) -> None:
    """Two entries never share a device, and entry-scoped lookups keep them apart."""
    second_entry = MockConfigEntry(
        domain=DOMAIN,
        title="second",
        unique_id="second",
        data={CONF_USERNAME: "second", CONF_PASSWORD: "secret"},
    )
    second_entry.add_to_hass(hass)
    await hass.config_entries.async_setup(second_entry.entry_id)
    await hass.async_block_till_done()

    device_registry = dr.async_get(hass)
    first_device = device_registry.async_get_device_by_identifier(
        (DOMAIN, init_integration.entry_id),
        init_integration.entry_id,
    )
    second_device = device_registry.async_get_device_by_identifier(
        (DOMAIN, second_entry.entry_id),
        second_entry.entry_id,
    )

    assert first_device is not None
    assert second_device is not None
    assert first_device.id != second_device.id
