"""Options flow schemas."""

from collections.abc import Mapping
from typing import Any

import probatio

from custom_components.ha_integration_domain.const import (
    CONF_FILTER_REPLACEMENT_THRESHOLD,
    DEFAULT_FILTER_REPLACEMENT_THRESHOLD,
)
from homeassistant.helpers import selector


def get_options_schema(defaults: Mapping[str, Any] | None = None) -> probatio.Schema:
    """
    Build the options form schema.

    Args:
        defaults: The entry's current options, used to pre-fill the form.

    Returns:
        The probatio schema for the options form.

    """
    defaults = defaults or {}
    return probatio.Schema(
        {
            probatio.Optional(
                CONF_FILTER_REPLACEMENT_THRESHOLD,
                default=defaults.get(CONF_FILTER_REPLACEMENT_THRESHOLD, DEFAULT_FILTER_REPLACEMENT_THRESHOLD),
            ): selector.NumberSelector(
                selector.NumberSelectorConfig(
                    min=1,
                    max=50,
                    step=1,
                    unit_of_measurement="%",
                    mode=selector.NumberSelectorMode.SLIDER,
                ),
            ),
        },
    )


__all__ = ["get_options_schema"]
