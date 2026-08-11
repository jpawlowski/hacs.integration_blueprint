"""Config flow for ha_integration_domain — user setup, reconfigure and reauth."""

from typing import Any

from custom_components.ha_integration_domain.api import (
    IntegrationBlueprintApiClientAuthenticationError,
    IntegrationBlueprintApiClientCommunicationError,
)
from custom_components.ha_integration_domain.const import DOMAIN, LOGGER
from homeassistant import config_entries
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME
from homeassistant.loader import async_get_loaded_integration
from homeassistant.util import slugify

from .options_flow import IntegrationBlueprintOptionsFlow
from .schemas import get_reauth_schema, get_reconfigure_schema, get_user_schema
from .validators import validate_credentials


class IntegrationBlueprintConfigFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle the config flow for ha_integration_domain."""

    VERSION = 1

    @staticmethod
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> IntegrationBlueprintOptionsFlow:
        """
        Return the options flow for this handler.

        Returns:
            The options flow instance.

        """
        return IntegrationBlueprintOptionsFlow()

    async def async_step_user(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> config_entries.ConfigFlowResult:
        """
        Handle a flow started by the user.

        Returns:
            The form, or the created config entry.

        """
        errors: dict[str, str] = {}

        if user_input is not None:
            errors = await self._async_validate(user_input)
            if not errors:
                # The username is the unique ID of last resort. A real integration
                # uses a serial number, MAC or account ID instead.
                await self.async_set_unique_id(slugify(user_input[CONF_USERNAME]))
                self._abort_if_unique_id_configured()

                return self.async_create_entry(
                    title=user_input[CONF_USERNAME],
                    data=user_input,
                )

        integration = async_get_loaded_integration(self.hass, DOMAIN)

        return self.async_show_form(
            step_id="user",
            data_schema=get_user_schema(user_input),
            errors=errors,
            description_placeholders={
                "documentation_url": integration.documentation or "",
            },
        )

    async def async_step_reconfigure(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> config_entries.ConfigFlowResult:
        """
        Handle reconfiguration of an existing entry.

        Returns:
            The form, or the abort that follows the entry update.

        """
        entry = self._get_reconfigure_entry()
        errors: dict[str, str] = {}

        if user_input is not None:
            errors = await self._async_validate(user_input)
            if not errors:
                return self.async_update_reload_and_abort(entry, data_updates=user_input)

        return self.async_show_form(
            step_id="reconfigure",
            data_schema=self.add_suggested_values_to_schema(
                get_reconfigure_schema(entry.data.get(CONF_USERNAME, "")),
                entry.data,
            ),
            errors=errors,
        )

    async def async_step_reauth(
        self,
        entry_data: dict[str, Any],
    ) -> config_entries.ConfigFlowResult:
        """
        Start reauthentication after the coordinator reported invalid credentials.

        Returns:
            The result of the reauth_confirm step.

        """
        return await self.async_step_reauth_confirm()

    async def async_step_reauth_confirm(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> config_entries.ConfigFlowResult:
        """
        Collect and verify replacement credentials.

        Returns:
            The form, or the abort that follows the entry update.

        """
        entry = self._get_reauth_entry()
        errors: dict[str, str] = {}

        if user_input is not None:
            errors = await self._async_validate(user_input)
            if not errors:
                return self.async_update_reload_and_abort(entry, data_updates=user_input)

        return self.async_show_form(
            step_id="reauth_confirm",
            data_schema=get_reauth_schema(entry.data.get(CONF_USERNAME, "")),
            errors=errors,
            description_placeholders={
                "username": entry.data.get(CONF_USERNAME, ""),
            },
        )

    async def _async_validate(self, user_input: dict[str, Any]) -> dict[str, str]:
        """
        Test the submitted credentials.

        Returns:
            An empty dict when they work, otherwise the errors for the form.

        """
        try:
            await validate_credentials(
                self.hass,
                username=user_input[CONF_USERNAME],
                password=user_input[CONF_PASSWORD],
            )
        except IntegrationBlueprintApiClientAuthenticationError:
            return {"base": "invalid_auth"}
        except IntegrationBlueprintApiClientCommunicationError:
            return {"base": "cannot_connect"}
        except Exception:  # noqa: BLE001 - Anything unexpected still has to reach the form.
            LOGGER.exception("Unexpected exception")
            return {"base": "unknown"}

        return {}


__all__ = ["IntegrationBlueprintConfigFlowHandler"]
