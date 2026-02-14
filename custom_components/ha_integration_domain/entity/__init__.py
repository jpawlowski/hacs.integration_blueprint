"""
Entity package for ha_integration_domain.

Architecture:
    All platform entities inherit from (PlatformEntity, IntegrationBlueprintEntity).
    MRO order matters — platform-specific class first, then the integration base.
    Entities read data from coordinator.data and NEVER call the API client directly.
    Unique IDs follow the pattern: {entry_id}_{description.key}

See entity/base.py for the IntegrationBlueprintEntity base class.
"""

from .base import IntegrationBlueprintEntity

__all__ = ["IntegrationBlueprintEntity"]
