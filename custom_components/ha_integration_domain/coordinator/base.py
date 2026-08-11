"""Data update coordinator for ha_integration_domain."""

from typing import TYPE_CHECKING, Any

from custom_components.ha_integration_domain.api import (
    IntegrationBlueprintApiClientAuthenticationError,
    IntegrationBlueprintApiClientError,
)
from custom_components.ha_integration_domain.const import DOMAIN, ISSUE_DEPRECATED_API
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers import issue_registry as ir
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

if TYPE_CHECKING:
    from custom_components.ha_integration_domain.data import IntegrationBlueprintConfigEntry


class IntegrationBlueprintDataUpdateCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Fetch the device state once per interval and hand it to every entity."""

    config_entry: IntegrationBlueprintConfigEntry

    async def _async_update_data(self) -> dict[str, Any]:
        """
        Fetch the current device state.

        Returns:
            The payload entities read by key.

        Raises:
            ConfigEntryAuthFailed: If the credentials were rejected; triggers reauth.
            UpdateFailed: If the fetch failed for any other reason.

        """
        try:
            data = await self.config_entry.runtime_data.client.async_get_data()
        except IntegrationBlueprintApiClientAuthenticationError as exception:
            raise ConfigEntryAuthFailed(
                translation_domain=DOMAIN,
                translation_key="authentication_failed",
            ) from exception
        except IntegrationBlueprintApiClientError as exception:
            raise UpdateFailed(
                translation_domain=DOMAIN,
                translation_key="update_failed",
            ) from exception

        self._async_check_api_version(deprecated=bool(data["api_deprecated"]))
        return data

    def _async_check_api_version(self, *, deprecated: bool) -> None:
        """Raise or clear the repair issue for the deprecated API version."""
        if deprecated:
            ir.async_create_issue(
                self.hass,
                DOMAIN,
                ISSUE_DEPRECATED_API,
                is_fixable=True,
                severity=ir.IssueSeverity.WARNING,
                translation_key=ISSUE_DEPRECATED_API,
                breaks_in_ha_version="2027.1",
                data={"entry_id": self.config_entry.entry_id},
            )
        else:
            ir.async_delete_issue(self.hass, DOMAIN, ISSUE_DEPRECATED_API)
