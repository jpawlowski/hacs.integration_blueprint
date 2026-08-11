"""Options flow for ha_integration_domain."""

from typing import Any

from homeassistant import config_entries

from .schemas import get_options_schema


class IntegrationBlueprintOptionsFlow(config_entries.OptionsFlow):
    """Let the user change the poll interval after setup."""

    async def async_step_init(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> config_entries.ConfigFlowResult:
        """
        Show and process the options form.

        Returns:
            The form, or the stored options.

        """
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=get_options_schema(self.config_entry.options),
        )


__all__ = ["IntegrationBlueprintOptionsFlow"]
