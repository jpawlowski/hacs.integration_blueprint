"""
Options flow for ha_integration_domain.

This module implements the options flow that allows users to modify settings
after the initial configuration, such as update intervals and debug settings.

For more information:
https://developers.home-assistant.io/docs/config_entries_options_flow_handler
"""

from typing import Any

from custom_components.ha_integration_domain.config_flow_handler.schemas import get_options_schema
from homeassistant import config_entries


class IntegrationBlueprintOptionsFlow(config_entries.OptionsFlow):
    """
    Handle options flow for the integration.

    This class manages the options that users can modify after initial setup,
    such as update intervals and debug settings.

    The options flow always starts with async_step_init and provides a single
    form for all configurable options.

    For more information:
    https://developers.home-assistant.io/docs/config_entries_options_flow_handler
    """

    async def async_step_init(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> config_entries.ConfigFlowResult:
        """
        Manage the options for the integration.

        This is the entry point for the options flow, allowing users to
        configure advanced settings like update interval and debugging.

        Args:
            user_input: The user input from the options form, or None for initial display.

        Returns:
            The config flow result, either showing a form or creating an options entry.

        """
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=get_options_schema(self.config_entry.options),
        )


__all__ = ["IntegrationBlueprintOptionsFlow"]
