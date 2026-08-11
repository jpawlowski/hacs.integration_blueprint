"""Repairs platform for ha_integration_domain."""

from typing import TYPE_CHECKING

from homeassistant.components.repairs import ConfirmRepairFlow, RepairsFlow
from homeassistant.components.repairs.models import RepairsFlowResult
from homeassistant.helpers import issue_registry as ir

from .api import CURRENT_API_VERSION
from .const import CONF_API_VERSION, ISSUE_DEPRECATED_API

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant


async def async_create_fix_flow(
    hass: HomeAssistant,
    issue_id: str,
    data: dict[str, str | int | float | None] | None,
) -> RepairsFlow:
    """
    Create the repair flow for an issue this integration raised.

    Returns:
        The flow that fixes the issue, or a plain confirmation for anything else.

    """
    if issue_id == ISSUE_DEPRECATED_API and data is not None:
        return DeprecatedApiEndpointRepairFlow(str(data["entry_id"]))

    return ConfirmRepairFlow()


class DeprecatedApiEndpointRepairFlow(RepairsFlow):
    """Move a config entry onto the current API version."""

    def __init__(self, entry_id: str) -> None:
        """Initialize the flow for the entry that raised the issue."""
        super().__init__()
        self._entry_id = entry_id

    async def async_step_init(
        self,
        user_input: dict[str, str] | None = None,
    ) -> RepairsFlowResult:
        """
        Confirm the switch, then write the new API version and reload.

        Returns:
            The confirmation form, or the finished flow.

        """
        if user_input is None:
            return self.async_show_form(step_id="init")

        entry = self.hass.config_entries.async_get_entry(self._entry_id)
        if entry is not None:
            self.hass.config_entries.async_update_entry(
                entry,
                data={**entry.data, CONF_API_VERSION: CURRENT_API_VERSION},
            )
            ir.async_delete_issue(self.hass, entry.domain, ISSUE_DEPRECATED_API)
            await self.hass.config_entries.async_reload(entry.entry_id)

        return self.async_create_entry(data={})
