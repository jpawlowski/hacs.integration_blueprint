"""Repairs platform for ha_integration_domain."""

from typing import TYPE_CHECKING

from homeassistant.components.repairs import ConfirmRepairFlow, RepairsFlow

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant


async def async_create_fix_flow(
    hass: HomeAssistant,
    issue_id: str,
    data: dict[str, str | int | float | None] | None,
) -> RepairsFlow:
    """
    Create the repair flow for an issue this integration raised.

    Branch on issue_id here once an issue needs more than an acknowledgement.

    Returns:
        The flow that fixes the issue.

    """
    return ConfirmRepairFlow()
