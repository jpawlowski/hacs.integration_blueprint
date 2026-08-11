"""Options flow schemas."""

from collections.abc import Mapping
from typing import Any

import voluptuous as vol

from custom_components.ha_integration_domain.const import CONF_UPDATE_INTERVAL_HOURS, DEFAULT_UPDATE_INTERVAL_HOURS
from homeassistant.helpers import selector


def get_options_schema(defaults: Mapping[str, Any] | None = None) -> vol.Schema:
    """
    Build the options form schema.

    Args:
        defaults: The entry's current options, used to pre-fill the form.

    Returns:
        The voluptuous schema for the options form.

    """
    defaults = defaults or {}
    return vol.Schema(
        {
            vol.Optional(
                CONF_UPDATE_INTERVAL_HOURS,
                default=defaults.get(CONF_UPDATE_INTERVAL_HOURS, DEFAULT_UPDATE_INTERVAL_HOURS),
            ): selector.NumberSelector(
                selector.NumberSelectorConfig(
                    min=0.25,
                    max=24,
                    step=0.25,
                    unit_of_measurement="h",
                    mode=selector.NumberSelectorMode.BOX,
                ),
            ),
        },
    )


__all__ = ["get_options_schema"]
