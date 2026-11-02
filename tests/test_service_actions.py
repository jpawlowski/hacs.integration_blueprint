"""Tests for the refresh_data service action."""

import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.ha_integration_domain.const import DOMAIN
from custom_components.ha_integration_domain.service_actions import SERVICE_REFRESH_DATA
from homeassistant.const import ATTR_CONFIG_ENTRY_ID
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ServiceValidationError


async def test_refresh_data_returns_the_refresh_result(init_integration: MockConfigEntry, hass: HomeAssistant) -> None:
    """A loaded entry is refreshed and the result reported back."""
    response = await hass.services.async_call(
        DOMAIN,
        SERVICE_REFRESH_DATA,
        {ATTR_CONFIG_ENTRY_ID: init_integration.entry_id},
        blocking=True,
        return_response=True,
    )

    assert response is not None
    assert response["success"] is True


@pytest.mark.usefixtures("init_integration")
async def test_refresh_data_rejects_an_unknown_entry(hass: HomeAssistant) -> None:
    """An entry id nobody knows fails validation with Home Assistant's own message."""
    with pytest.raises(ServiceValidationError) as exc_info:
        await hass.services.async_call(DOMAIN, SERVICE_REFRESH_DATA, {ATTR_CONFIG_ENTRY_ID: "missing"}, blocking=True)

    assert exc_info.value.translation_domain == "homeassistant"
    assert exc_info.value.translation_key == "service_config_entry_not_found"


async def test_refresh_data_rejects_an_unloaded_entry(init_integration: MockConfigEntry, hass: HomeAssistant) -> None:
    """An entry that is set up but not loaded cannot be refreshed."""
    await hass.config_entries.async_unload(init_integration.entry_id)
    await hass.async_block_till_done()

    with pytest.raises(ServiceValidationError) as exc_info:
        await hass.services.async_call(
            DOMAIN, SERVICE_REFRESH_DATA, {ATTR_CONFIG_ENTRY_ID: init_integration.entry_id}, blocking=True
        )

    assert exc_info.value.translation_domain == "homeassistant"
    assert exc_info.value.translation_key == "service_config_entry_not_loaded"
