"""Config flow schemas for the user, reconfigure and reauth steps."""

from collections.abc import Mapping
from typing import Any

import probatio

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


def get_user_schema(defaults: Mapping[str, Any] | None = None) -> probatio.Schema:
    """
    Build the schema for the user step.

    Args:
        defaults: Previously submitted values, used to pre-fill the form.

    Returns:
        The voluptuous schema for the credentials form.

    """
    defaults = defaults or {}
    return probatio.Schema(
        {
            probatio.Required(
                CONF_USERNAME,
                default=defaults.get(CONF_USERNAME, probatio.UNDEFINED),
            ): _USERNAME_SELECTOR,
            probatio.Required(CONF_PASSWORD): _PASSWORD_SELECTOR,
        },
    )


def get_credentials_schema(username: str) -> probatio.Schema:
    """
    Build the schema for the reconfigure and reauth steps.

    Args:
        username: The entry's current username, used to pre-fill the form.

    Returns:
        The voluptuous schema for the credentials form.

    """
    return probatio.Schema(
        {
            probatio.Required(CONF_USERNAME, default=username): _USERNAME_SELECTOR,
            probatio.Required(CONF_PASSWORD): _PASSWORD_SELECTOR,
        },
    )


__all__ = [
    "get_credentials_schema",
    "get_user_schema",
]
