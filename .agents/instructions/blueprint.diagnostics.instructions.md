---
name: "Diagnostics"
description: "Redacting credentials and personal data from diagnostics output"
applyTo: "custom_components/**/diagnostics.py"
paths:
  - "custom_components/**/diagnostics.py"
---

# Diagnostics Instructions

**Applies to:** Diagnostics implementation files

## Critical: Always Redact Sensitive Data

**Use `async_redact_data()` for all user data:**

```python
from homeassistant.helpers.redact import async_redact_data
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME

# Define what to redact
TO_REDACT = {
    CONF_PASSWORD,
    CONF_USERNAME,
    "api_key",
    "token",
    "refresh_token",
}

async def async_get_config_entry_diagnostics(
    hass: HomeAssistant,
    entry: ConfigEntry,
) -> dict[str, Any]:
    """Return diagnostics for a config entry."""
    coordinator = entry.runtime_data.coordinator

    return {
        "entry_data": async_redact_data(entry.data, TO_REDACT),
        "entry_options": async_redact_data(entry.options, TO_REDACT),
        "coordinator_data": coordinator.data,
    }
```

## Device-Level Diagnostics

A second, optional entry point. Implement it when a single device's data is worth downloading on its own; without it,
the device page offers the config entry diagnostics instead.

```python
async def async_get_device_diagnostics(
    hass: HomeAssistant,
    entry: ConfigEntry,
    device: DeviceEntry,
) -> dict[str, Any]:
    """Return diagnostics for a device."""
```

Either function may exist on its own, or both together. Redaction rules are identical.

## Never Expose

The following must ALWAYS be redacted:

- Passwords
- API keys / tokens (access_token, refresh_token, api_key, etc.)
- OAuth credentials
- Location data (latitude/longitude)
- Personal information (email, phone, name)
- Device serial numbers (if considered sensitive)
- MAC addresses (use `format_mac` if needed for identification)

## When in Doubt

If you're unsure whether data is sensitive, **redact it**. Better to redact too much than expose credentials.
