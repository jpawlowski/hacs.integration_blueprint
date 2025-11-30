"""Repairs platform for ha_integration_domain."""

from __future__ import annotations

from typing import TYPE_CHECKING, cast

from homeassistant.components.repairs import RepairsFlow
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import issue_registry as ir

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry


async def async_create_fix_flow(
    hass: HomeAssistant,
    issue_id: str,
    data: dict[str, str | int | float | None] | None,
) -> RepairsFlow:
    """Create a repair flow based on the issue_id."""
    # Map issue IDs to their corresponding repair flow classes
    if issue_id == "deprecated_api_endpoint":
        return DeprecatedApiEndpointRepairFlow()
    if issue_id == "missing_configuration":
        return MissingConfigurationRepairFlow()

    # Fallback for unknown issue IDs
    return UnknownIssueRepairFlow(issue_id)


class DeprecatedApiEndpointRepairFlow(RepairsFlow):
    """Handler for deprecated API endpoint repair."""

    async def async_step_init(self, user_input: dict[str, str] | None = None) -> FlowResult:
        """Handle the initial repair step."""
        if user_input is not None:
            # User confirmed the fix - update the config entry
            entry = cast(
                "ConfigEntry",
                self.hass.config_entries.async_get_entry(self.handler),
            )
            if entry:
                new_data = {**entry.data, "api_version": "v2"}
                self.hass.config_entries.async_update_entry(entry, data=new_data)

                # Remove the repair issue
                ir.async_delete_issue(self.hass, entry.domain, "deprecated_api_endpoint")

                # Reload the config entry to use the new API endpoint
                await self.hass.config_entries.async_reload(entry.entry_id)

            return self.async_create_entry(data={})

        return self.async_show_form(step_id="init")


class MissingConfigurationRepairFlow(RepairsFlow):
    """Handler for missing configuration repair."""

    async def async_step_init(self, user_input: dict[str, str] | None = None) -> FlowResult:
        """Handle the initial repair step."""
        if user_input is not None:
            # User acknowledged the issue - mark as resolved
            entry = cast(
                "ConfigEntry",
                self.hass.config_entries.async_get_entry(self.handler),
            )
            if entry:
                ir.async_delete_issue(self.hass, entry.domain, "missing_configuration")

            return self.async_create_entry(data={})

        return self.async_show_form(step_id="init")


class UnknownIssueRepairFlow(RepairsFlow):
    """Handler for unknown repair issues."""

    def __init__(self, issue_id: str) -> None:
        """Initialize the unknown issue repair flow."""
        super().__init__()
        self._issue_id = issue_id

    async def async_step_init(self, user_input: dict[str, str] | None = None) -> FlowResult:
        """Handle unknown issues."""
        if user_input is not None:
            # Just acknowledge and close
            return self.async_create_entry(data={})

        return self.async_show_form(step_id="init")
