"""
Config flow for ha_integration_domain.

This module provides backwards compatibility for hassfest.
The actual implementation is in the config_flow_handler package.
"""

from .config_flow_handler import IntegrationBlueprintConfigFlowHandler

__all__ = ["IntegrationBlueprintConfigFlowHandler"]
