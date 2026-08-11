"""Tests for the deprecated-API repair issue and its fix flow."""

from unittest.mock import AsyncMock

from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.ha_integration_domain.const import CONF_API_VERSION, DOMAIN, ISSUE_DEPRECATED_API
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME
from homeassistant.core import HomeAssistant
from homeassistant.helpers import issue_registry as ir


async def test_no_issue_while_the_entry_is_current(
    init_integration: MockConfigEntry,
    hass: HomeAssistant,
) -> None:
    """An entry already on the current API version raises nothing."""
    assert ir.async_get(hass).async_get_issue(DOMAIN, ISSUE_DEPRECATED_API) is None


async def test_old_api_version_raises_a_fixable_issue(
    hass: HomeAssistant,
    mock_api: AsyncMock,
) -> None:
    """An entry left on the old API version gets a repair the user can act on."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title="legacy",
        unique_id="legacy",
        data={CONF_USERNAME: "legacy", CONF_PASSWORD: "secret"},
    )
    entry.add_to_hass(hass)
    await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    issue = ir.async_get(hass).async_get_issue(DOMAIN, ISSUE_DEPRECATED_API)

    assert issue is not None
    assert issue.is_fixable
    assert issue.severity is ir.IssueSeverity.WARNING
    assert entry.data.get(CONF_API_VERSION) is None
