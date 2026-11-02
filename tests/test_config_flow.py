"""Tests that a changed config entry is set up again exactly once."""

from unittest.mock import patch

import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.ha_integration_domain import async_setup_entry
from custom_components.ha_integration_domain.const import CONF_FILTER_REPLACEMENT_THRESHOLD
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType

SETUP_ENTRY = "custom_components.ha_integration_domain.async_setup_entry"


async def test_options_change_reloads_once(
    init_integration: MockConfigEntry,
    hass: HomeAssistant,
) -> None:
    """New options take effect through one reload."""
    with patch(SETUP_ENTRY, wraps=async_setup_entry) as setup_entry:
        result = await hass.config_entries.options.async_init(init_integration.entry_id)
        result = await hass.config_entries.options.async_configure(
            result["flow_id"],
            {CONF_FILTER_REPLACEMENT_THRESHOLD: 25},
        )
        await hass.async_block_till_done()

    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert init_integration.options[CONF_FILTER_REPLACEMENT_THRESHOLD] == 25
    assert setup_entry.call_count == 1


@pytest.mark.parametrize(
    ("start_flow", "reason"),
    [
        ("start_reauth_flow", "reauth_successful"),
        ("start_reconfigure_flow", "reconfigure_successful"),
    ],
)
async def test_new_credentials_reload_once(
    init_integration: MockConfigEntry,
    hass: HomeAssistant,
    start_flow: str,
    reason: str,
) -> None:
    """New credentials take effect through the flow's own reload, not a second one from an update listener."""
    with patch(SETUP_ENTRY, wraps=async_setup_entry) as setup_entry:
        result = await getattr(init_integration, start_flow)(hass)
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {CONF_USERNAME: "demo", CONF_PASSWORD: "new-secret"},
        )
        await hass.async_block_till_done()

    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == reason
    assert init_integration.data[CONF_PASSWORD] == "new-secret"
    assert setup_entry.call_count == 1
