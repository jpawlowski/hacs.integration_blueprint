"""
Subentry flow template for ha_integration_domain.

This module provides a template for implementing subentry flows when needed.
Subentry flows allow users to add multiple "sub-configurations" under a single
config entry.

Example use case:
- Weather integration: Main entry for API credentials, subentries for locations
- Multi-device integration: Main entry for hub/account, subentries for devices

Device registry ownership rules (Home Assistant Core 2026.8+):
- A device belongs to exactly one config entry and at most one config subentry.
- Create a separate device for every subentry; never share a device across subentries.
- Keep the hub/account as a separate parent-entry device and link subentry devices
  with via_device_id when a parent relationship is needed.
- Scope identifier/connection lookups to the owning config entry. Do not use the
  deprecated async_get_device() or via_device APIs.

This file is currently a template/example. Uncomment and adapt when implementing
subentry support.

For more information:
https://developers.home-assistant.io/docs/config_entries_config_flow_handler#subentry-flows
"""

from __future__ import annotations

# Uncomment when implementing subentry flows:
#
# from typing import Any
#
# from homeassistant import config_entries
# from homeassistant.config_entries import ConfigSubentryFlow, SubentryFlowResult
#
# class ExampleLocationSubentryFlowHandler(ConfigSubentryFlow):
#     """
#     Handle subentry flow for adding and modifying locations.
#
#     This is an example implementation. Adapt to your integration's needs.
#     """
#
#     async def async_step_user(
#         self,
#         user_input: dict[str, Any] | None = None
#     ) -> SubentryFlowResult:
#         """User flow to add a new location."""
#         if user_input is not None:
#             # Validate and create subentry
#             return self.async_create_subentry(
#                 title=user_input["location_name"],
#                 data=user_input,
#             )
#
#         # Show form to collect location data
#         return self.async_show_form(
#             step_id="user",
#             data_schema=vol.Schema({
#                 vol.Required("location_name"): str,
#                 vol.Required("latitude"): float,
#                 vol.Required("longitude"): float,
#             })
#         )
#
#     async def async_step_reconfigure(
#         self,
#         user_input: dict[str, Any] | None = None
#     ) -> SubentryFlowResult:
#         """User flow to modify an existing location."""
#         config_entry = self._get_entry()
#         config_subentry = self._get_reconfigure_subentry()
#
#         if user_input is not None:
#             # Validate and update subentry
#             return self.async_update_subentry(
#                 config_subentry,
#                 data=user_input,
#             )
#
#         # Show form pre-filled with current values
#         return self.async_show_form(
#             step_id="reconfigure",
#             data_schema=vol.Schema({
#                 vol.Required(
#                     "location_name",
#                     default=config_subentry.data.get("location_name")
#                 ): str,
#                 vol.Required(
#                     "latitude",
#                     default=config_subentry.data.get("latitude")
#                 ): float,
#                 vol.Required(
#                     "longitude",
#                     default=config_subentry.data.get("longitude")
#                 ): float,
#             })
#         )
#
#
# # Add to main ConfigFlow class:
# #
# # @classmethod
# # @callback
# # def async_get_supported_subentry_types(
# #     cls,
# #     config_entry: ConfigEntry
# # ) -> dict[str, type[ConfigSubentryFlow]]:
# #     """Return subentries supported by this integration."""
# #     return {
# #         "location": ExampleLocationSubentryFlowHandler
# #     }


__all__: list[str] = []  # Empty until subentry flows are implemented
