"""
Config flow for ha_integration_domain.

This module implements the main configuration flow including:
- Initial user setup
- Reconfiguration of existing entries
- Reauthentication flow

For more information:
https://developers.home-assistant.io/docs/config_entries_config_flow_handler
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from slugify import slugify

from custom_components.ha_integration_domain.config_flow_handler.schemas import (
    get_reauth_schema,
    get_reconfigure_schema,
    get_user_schema,
)
from custom_components.ha_integration_domain.config_flow_handler.validators import validate_credentials
from custom_components.ha_integration_domain.const import DOMAIN, LOGGER
from homeassistant import config_entries
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME

if TYPE_CHECKING:
    from custom_components.ha_integration_domain.config_flow_handler.options_flow import IntegrationBlueprintOptionsFlow

# Map exception types to error keys for user-facing messages
ERROR_MAP = {
    "IntegrationBlueprintApiClientAuthenticationError": "auth",
    "IntegrationBlueprintApiClientCommunicationError": "connection",
}


class IntegrationBlueprintConfigFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """
    Handle a config flow for ha_integration_domain.

    This class manages the configuration flow for the integration, including
    initial setup, reconfiguration, and reauthentication.

    Supported flows:
    - user: Initial setup via UI
    - reconfigure: Update existing configuration
    - reauth: Handle expired credentials

    For more details:
    https://developers.home-assistant.io/docs/config_entries_config_flow_handler
    """

    VERSION = 1

    @staticmethod
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> IntegrationBlueprintOptionsFlow:
        """
        Get the options flow for this handler.

        Returns:
            The options flow instance for modifying integration options.

        """
        from custom_components.ha_integration_domain.config_flow_handler.options_flow import (  # noqa: PLC0415
            IntegrationBlueprintOptionsFlow,
        )

        return IntegrationBlueprintOptionsFlow()

    async def async_step_user(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> config_entries.ConfigFlowResult:
        """
        Handle a flow initialized by the user.

        This is the entry point when a user adds the integration from the UI.

        Args:
            user_input: The user input from the config flow form, or None for initial display.

        Returns:
            The config flow result, either showing a form or creating an entry.

        """
        errors: dict[str, str] = {}

        if user_input is not None:
            try:
                await validate_credentials(
                    self.hass,
                    username=user_input[CONF_USERNAME],
                    password=user_input[CONF_PASSWORD],
                )
            except Exception as exception:  # noqa: BLE001
                errors["base"] = self._map_exception_to_error(exception)
            else:
                # Set unique ID based on username
                # NOTE: This is just an example - use a proper unique ID in production
                # See: https://developers.home-assistant.io/docs/config_entries_config_flow_handler#unique-ids
                await self.async_set_unique_id(slugify(user_input[CONF_USERNAME]))
                self._abort_if_unique_id_configured()

                return self.async_create_entry(
                    title=user_input[CONF_USERNAME],
                    data=user_input,
                )

        return self.async_show_form(
            step_id="user",
            data_schema=get_user_schema(user_input),
            errors=errors,
            description_placeholders={
                "documentation_url": "https://github.com/jpawlowski/hacs.integration_blueprint",
            },
        )

    async def async_step_reconfigure(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> config_entries.ConfigFlowResult:
        """
        Handle reconfiguration of the integration.

        Allows users to update their credentials without removing and re-adding
        the integration.

        Args:
            user_input: The user input from the reconfigure form, or None for initial display.

        Returns:
            The config flow result, either showing a form or updating the entry.

        """
        entry = self._get_reconfigure_entry()
        errors: dict[str, str] = {}

        if user_input is not None:
            try:
                await validate_credentials(
                    self.hass,
                    username=user_input[CONF_USERNAME],
                    password=user_input[CONF_PASSWORD],
                )
            except Exception as exception:  # noqa: BLE001
                errors["base"] = self._map_exception_to_error(exception)
            else:
                return self.async_update_reload_and_abort(
                    entry,
                    data=user_input,
                )

        return self.async_show_form(
            step_id="reconfigure",
            data_schema=get_reconfigure_schema(entry.data.get(CONF_USERNAME, "")),
            errors=errors,
        )

    async def async_step_reauth(
        self,
        entry_data: dict[str, Any] | None = None,
    ) -> config_entries.ConfigFlowResult:
        """
        Handle reauthentication when credentials are invalid.

        This flow is automatically triggered when the coordinator catches
        an authentication error (ConfigEntryAuthFailed).

        Args:
            entry_data: The existing entry data (unused, per convention).

        Returns:
            The result of the reauth_confirm step.

        """
        return await self.async_step_reauth_confirm()

    async def async_step_reauth_confirm(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> config_entries.ConfigFlowResult:
        """
        Handle reauthentication confirmation.

        Shows the reauthentication form and processes updated credentials.

        Args:
            user_input: The user input with updated credentials, or None for initial display.

        Returns:
            The config flow result, either showing a form or updating the entry.

        """
        entry = self._get_reauth_entry()
        errors: dict[str, str] = {}

        if user_input is not None:
            try:
                await validate_credentials(
                    self.hass,
                    username=user_input[CONF_USERNAME],
                    password=user_input[CONF_PASSWORD],
                )
            except Exception as exception:  # noqa: BLE001
                errors["base"] = self._map_exception_to_error(exception)
            else:
                return self.async_update_reload_and_abort(
                    entry,
                    data={**entry.data, **user_input},
                )

        return self.async_show_form(
            step_id="reauth_confirm",
            data_schema=get_reauth_schema(entry.data.get(CONF_USERNAME, "")),
            errors=errors,
            description_placeholders={
                "username": entry.data.get(CONF_USERNAME, ""),
            },
        )

    def _map_exception_to_error(self, exception: Exception) -> str:
        """
        Map API exceptions to user-facing error keys.

        Args:
            exception: The exception that was raised.

        Returns:
            The error key for display in the config flow form.

        """
        LOGGER.warning("Error in config flow: %s", exception)
        exception_name = type(exception).__name__
        return ERROR_MAP.get(exception_name, "unknown")


__all__ = ["IntegrationBlueprintConfigFlowHandler"]
