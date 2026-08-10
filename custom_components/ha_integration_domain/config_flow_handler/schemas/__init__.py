"""
Data schemas for config flow forms.

This package contains all voluptuous schemas used in config flows, options flows,
and subentry flows. Schemas are organized into separate modules for better
maintainability as the integration grows.

Package structure:
-----------------
- config.py: Main config flow schemas (user, reauth, reconfigure)
- options.py: Options flow schemas

When schemas grow (>300 lines per file), split further:
- config/user.py, config/reauth.py, config/reconfigure.py
- options/basic.py, options/advanced.py
- subentries/device.py, subentries/location.py

All schemas are re-exported from this __init__.py for convenient imports.
"""

from custom_components.ha_integration_domain.config_flow_handler.schemas.config import (
    get_reauth_schema,
    get_reconfigure_schema,
    get_user_schema,
)
from custom_components.ha_integration_domain.config_flow_handler.schemas.options import get_options_schema

# Re-export all schemas for convenient imports
__all__ = [
    "get_options_schema",
    "get_reauth_schema",
    "get_reconfigure_schema",
    "get_user_schema",
]
