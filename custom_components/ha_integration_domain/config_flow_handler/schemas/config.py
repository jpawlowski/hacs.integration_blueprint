"""Config flow schemas for the user, reconfigure and reauth steps."""

from collections.abc import Mapping
from typing import Any

import voluptuous as vol

from homeassistant.const import CONF_PASSWORD, CONF_USERNAME
from homeassistant.helpers import selector

_USERNAME_SELECTOR = selector.TextSelector(
    selector.TextSelectorConfig(
        type=selector.TextSelectorType.TEXT,
        autocomplete="username",
    ),
)
_PASSWORD_SELECTOR = selector.TextSelector(
    selector.TextSelectorConfig(
        type=selector.TextSelectorType.PASSWORD,
        autocomplete="current-password",
    ),
)


def get_user_schema(defaults: Mapping[str, Any] | None = None) -> vol.Schema:
    """
    Build the schema for the user step.

    Args:
        defaults: Previously submitted values, used to pre-fill the form.

    Returns:
        The voluptuous schema for the credentials form.

    """
    defaults = defaults or {}
    return vol.Schema(
        {
            vol.Required(
                CONF_USERNAME,
                default=defaults.get(CONF_USERNAME, vol.UNDEFINED),
            ): _USERNAME_SELECTOR,
            vol.Required(CONF_PASSWORD): _PASSWORD_SELECTOR,
        },
    )


def get_reconfigure_schema(username: str) -> vol.Schema:
    """
    Build the schema for the reconfigure step.

    Args:
        username: The entry's current username, used to pre-fill the form.

    Returns:
        The voluptuous schema for the reconfigure form.

    """
    return vol.Schema(
        {
            vol.Required(CONF_USERNAME, default=username): _USERNAME_SELECTOR,
            vol.Required(CONF_PASSWORD): _PASSWORD_SELECTOR,
        },
    )


def get_reauth_schema(username: str) -> vol.Schema:
    """
    Build the schema for the reauth step.

    Args:
        username: The entry's current username, used to pre-fill the form.

    Returns:
        The voluptuous schema for the reauth form.

    """
    return vol.Schema(
        {
            vol.Required(CONF_USERNAME, default=username): _USERNAME_SELECTOR,
            vol.Required(CONF_PASSWORD): _PASSWORD_SELECTOR,
        },
    )


__all__ = [
    "get_reauth_schema",
    "get_reconfigure_schema",
    "get_user_schema",
]
