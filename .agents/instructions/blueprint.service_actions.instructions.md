---
name: "Service Action Implementation"
description: "Registration in async_setup(), schemas, exceptions, and response data"
applyTo: "custom_components/**/service_actions/**/*.py"
paths:
  - "custom_components/**/service_actions/**/*.py"
---

# Service Actions Instructions

**Procedure:** [`ha-service-action`](../skills/ha-service-action/SKILL.md) — load it before adding, changing or
removing an action. This file is the rule set; the skill is the order of operations and the design decisions, and it
covers the `services.yaml` half of the change too.

**Applies to:** Service action implementation files

**Reference:** [Home Assistant Service Actions Documentation](https://developers.home-assistant.io/docs/dev_101_services/)

## Critical Rules

**Registration location (Bronze Quality Scale requirement `action-setup`):**

- ✅ Register service actions in `async_setup()` (component level)
- ❌ Never register in `async_setup_entry()` (per config entry)
- Check `hass.services.has_service(DOMAIN, "action_name")` before registering
  **Service naming:**

- Format: `<integration_domain>.<action_name>`
- Always use integration DOMAIN, never platform domain (e.g., `sensor`, `switch`)

**Implementation structure:**

- Call `await async_setup_services(hass)` from `async_setup()` in `__init__.py`
- Register the actions in `service_actions/__init__.py`; put the handler bodies in a module per logical group
- Resolve entries with `hass.config_entries.async_entries(DOMAIN)`, then reach state through `entry.runtime_data`.
  **NEVER** use `hass.data[DOMAIN]` — this integration stores runtime state on the config entry.
- When no entry is loaded, raise `ServiceValidationError` with a translation key rather than logging and returning —
  the caller's automation must see the failure

## Service Schema

Use voluptuous with `homeassistant.helpers.config_validation` for parameter validation:

```python
import voluptuous as vol
from homeassistant.helpers import config_validation as cv

SERVICE_SCHEMA = vol.Schema({
    vol.Required("device_id"): cv.string,
    vol.Optional("force", default=False): cv.boolean,
})
```

## Exception Handling

**Use appropriate exceptions:**

- `ServiceValidationError` - User provided invalid data (no stack trace in logs except at debug level)
- `HomeAssistantError` - Device/communication errors (full stack trace in logs)

Both exceptions support translation keys for localization.

**Authentication failures need `entry.async_start_reauth(hass)`.** `ConfigEntryAuthFailed` only triggers the reauth
flow when it is raised from `async_setup_entry` in `__init__.py` or from the coordinator. Raised in an action handler
it does nothing but log, so start the flow explicitly and raise a translated `HomeAssistantError` for the caller.

## Target Field

Use modern `target` field in `services.yaml` instead of deprecated `entity_id`:

```yaml
reset_filter:
  target:
    entity:
      domain: sensor
```

## Response Data

Services can return JSON-serializable data (`homeassistant.util.json.JsonObjectType`) for use in automations:

**Critical requirements:**

- Response MUST be a `dict`
- **datetime objects MUST use `.isoformat()`** - Template engine cannot handle raw datetime
- Raise exceptions for errors, never return error codes in response data

**SupportsResponse modes:**

- `SupportsResponse.OPTIONAL` - Returns data only if `call.return_response` is True
- `SupportsResponse.ONLY` - Always returns data, performs no action

Example with datetime conversion:

```python
from homeassistant.core import SupportsResponse

async def search_items(call: ServiceCall) -> ServiceResponse:
    items = await client.search(call.data["start"], call.data["end"])
    return {
        "items": [
            {
                "summary": item["summary"],
                "timestamp": item["timestamp"].isoformat(),  # ✅ Convert datetime!
            }
            for item in items
        ],
    }

hass.services.async_register(
    DOMAIN, "search", search_items,
    supports_response=SupportsResponse.ONLY,
)
```

## Entity Service Actions

For services targeting entities, use `async_register_platform_entity_service`:

```python
from homeassistant.helpers import service

service.async_register_platform_entity_service(
    hass,
    DOMAIN,  # Integration domain, NOT platform domain!
    "set_timer",
    entity_domain="media_player",
    schema={vol.Required("sleep_time"): cv.time_period},
    func="set_sleep_timer",  # Method name on entity class
)
```

`func` takes either the name of a method on the entity class, as above, or a callable `(entity, service_call)`.

## Service Icons

Define in `icons.json`:

```json
{
  "services": {
    "turn_on": { "service": "mdi:lightbulb-on" },
    "start_brewing": {
      "service": "mdi:flask",
      "sections": { "advanced_options": "mdi:test-tube" }
    }
  }
}
```

## Permissions

Verify authentication when required:

```python
async def handle_service(call: ServiceCall) -> None:
    if not call.context.user_id:
        raise Unauthorized("Service requires authentication")
```
