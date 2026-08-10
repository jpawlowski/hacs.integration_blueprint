---
name: "Python Code"
description: "Module layout, type hints, async patterns, imports, logging, and validation"
applyTo: "**/*.py"
paths:
  - "**/*.py"
---

# Python Code Instructions

**Applies to:** All Python files in the integration

## File Structure

### Module Organization

**Integration modules:**

- `__init__.py` - Platform setup with `async_setup_entry()`
- Individual files - One class per file when practical
- `const.py` - Module constants only (no logic)

**File size guidelines:**

- **Target:** 200-400 lines per file
- **Maximum:** ~500 lines before refactoring
- **Reason:** AI models have context limits - keep files manageable

**When a file grows too large:**

1. Extract helper functions to separate files
2. Move entity classes to individual files
3. Create subpackages for related functionality
4. Split constants into logical groups

**Example structure:**

```text
sensor/
  __init__.py          # Setup and entity list (50 lines)
  air_quality.py       # Air quality sensor class (200 lines)
  temperature.py       # Temperature sensor class (150 lines)
  diagnostic.py        # Diagnostic sensors (180 lines)
  const.py             # Sensor-specific constants (30 lines)
```

**Naming:**

- Files: `snake_case.py`
- Classes: `PascalCase` prefixed with the integration's class prefix (defined in project identity)
- Functions/methods: `snake_case`
- Constants: `UPPER_SNAKE_CASE`

## Type Annotations

**Required for:**

- All function parameters and return values
- Class attributes (when not obvious)

**Import rules:**

- Never `from __future__ import annotations` — Home Assistant requires Python 3.14, where annotations are already
  lazily evaluated; Ruff's `banned-api` rejects it
- `collections.abc` for abstract base classes (prefer over `typing`)
- `typing` for complex types (Any, TYPE_CHECKING, etc.)

**Avoiding circular imports:**

Use `if TYPE_CHECKING:` block for type-only imports that would cause circular dependencies.

## Async Patterns

**All I/O operations must be async** - Network, file, database, blocking operations

**Core patterns:**

- `async def` for coroutines, `await` for async calls
- `asyncio.gather()` for concurrent operations
- `asyncio.timeout()` for timeouts (not `async_timeout`)
- Never: `time.sleep()`, synchronous HTTP libraries, blocking operations

**Running blocking code:**

- `await hass.async_add_executor_job(sync_function, arg1, arg2)` - Run blocking I/O in executor thread
- Avoid if sync function also uses executor internally (deadlock risk)

**Background tasks:** inside an integration, create tasks on the **config entry**, not on `hass` — the entry cancels
them on unload, which `hass.async_create_task` does not.

- `entry.async_create_task(hass, coroutine)` - Work that must finish before the entry unloads
- `entry.async_create_background_task(hass, coroutine, name)` - Long-lived loops (a listener, a reconnect loop)
- `hass.async_create_task(coroutine)` - Only in `async_setup()` scope, where there is no entry
- `asyncio.run_coroutine_threadsafe(coro, hass.loop).result()` - From sync thread (rare)

**Callback decorator:**

- `@callback` from `homeassistant.core` - For event loop functions without blocking
- Required for event listeners, state change callbacks
- Cannot do I/O, cannot call coroutines (only schedule them)

**Calling Home Assistant from a non-event-loop thread:** the `async_*` APIs are **not** thread-safe and Home Assistant
raises when they are called from the wrong thread. Most have a sync twin that does the hand-off for you — a library
callback running on its own thread is the usual reason to need one:

| From a worker thread, instead of                                                               | call                                                |
| ---------------------------------------------------------------------------------------------- | --------------------------------------------------- |
| `hass.async_create_task`                                                                       | `hass.create_task`                                  |
| `hass.bus.async_fire`                                                                          | `hass.bus.fire`                                     |
| `hass.services.async_register` / `async_remove`                                                | `hass.services.register` / `remove`                 |
| `entity.async_write_ha_state`                                                                  | `entity.schedule_update_ha_state`                   |
| `async_dispatcher_send`                                                                        | `dispatcher_send`                                   |
| `issue_registry.async_get_or_create` / `async_delete`                                          | `issue_registry.create_issue` / `delete_issue`      |
| `event.async_track_state_change_event`                                                         | `event.track_state_change_event`                    |
| The registries (`device_`, `entity_`, `area_`, …) and `hass.config_entries.async_update_entry` | no sync twin — wrap the call in `hass.add_job(...)` |

`hass.add_job` is the sync entry point and is not deprecated; `hass.async_add_job` is.

- Missing decorator causes execution in executor thread (wrong context)

**Blocking operations (NEVER in event loop):**

- File: `open()`, `pathlib.Path.read_text()`, `pathlib.Path.write_bytes()`
- Directory: `os.listdir()`, `os.walk()`, `glob.glob()`
- Network: `urllib` (use `aiohttp`)
- Other: `time.sleep()`, `SSLContext.load_default_certs()`
- **All must run in executor:** `await hass.async_add_executor_job(blocking_func)`

**Late imports:**

- Module-level imports are safe
- Late async imports: `await async_import_module(hass, "module.path")`
- `if TYPE_CHECKING:` for type-only imports

## Code Style

**Conventions not enforced by Ruff:**

- Alphabetical sorting of constants/lists when order doesn't matter
- Comments: see `blueprint.comments.instructions.md` for when one is warranted at all — the default is none, and
  those that survive are complete sentences with capitalization and an ending period

**Note:** Ruff enforces `__all__`/`__slots__` sorting, import ordering, f-string usage in logs.

## Home Assistant Requirements

**Setup Failure Handling:**

See [Integration Setup Failures](https://developers.home-assistant.io/docs/integration_setup_failures) for details.

- `ConfigEntryNotReady` - Device offline/unavailable, retry later (raise in `async_setup_entry()`)
- `ConfigEntryAuthFailed` - Expired credentials (triggers reauth flow)
- `ConfigEntryError` - Will not resolve on its own (closed account, unsupported device); stops the retry loop
- Pass error message to exception (HA logs at debug level automatically)
- **Do NOT log setup failures manually** - Avoid log spam
- Raising any of the three still runs the `entry.async_on_unload` callbacks, but does **not** replace
  `async_unload_entry` — that always has to exist
- Raising `ConfigEntryNotReady` in a **platform's** `async_setup_entry` does nothing; by then the config entry setup
  has already completed and cannot catch it

**Constants:**

- Prefer `homeassistant.const` over defining new ones (e.g., `CONF_USERNAME`, `CONF_PASSWORD`)
- Only add to integration's `const.py` if widely used internally

**Units of Measurement:**

- Always use constants from `homeassistant.const` - Never hardcode strings
- Examples: `UnitOfDensity.MICROGRAMS_PER_CUBIC_METER`, `PERCENTAGE`, `UnitOfTime.HOURS`
- Construct compound units if no combined constant exists: `f"{UnitOfLength.METERS}/{UnitOfTime.SECONDS}"`

**Time and Timestamps:**

- Always use UTC timestamps (ISO 8601 or Unix)
- Use `dt_util.utcnow().isoformat()` from `homeassistant.util`
- Never use relative time ("2 hours ago") in state/attributes

**Service Actions:**

- Format: `<integration_domain>.<action_name>`
- Register under integration domain (not platform domain)
- Example: `hass.services.async_register(DOMAIN, "reset_filter", handler)`

**Event Names:**

- Prefix with integration domain: `<domain>_<event_name>`
- Example: `hass.bus.async_fire(f"{DOMAIN}_device_paired", data)`

**PARALLEL_UPDATES:**

- Required in **every** platform `__init__.py`, not optional — a missing one fails the `parallel-updates` rule
- A module-level literal, never imported from `const.py`; `0` or `1` is decided per platform in
  [`blueprint.entities`](blueprint.entities.instructions.md)
- Left undefined, Home Assistant derives it: `0` when the entity defines `async_update`, otherwise `1`

## Imports

**Order (separated by blank lines):**

1. Standard library
2. Third-party packages
3. Home Assistant core
4. Local integration imports

**Standard HA aliases:** `vol`, `cv`, `dr`, `er`, `dt_util`

## Entity Classes

**Structure requirements:**

- Inherit from both platform entity and the base entity class from `..entity` (order matters)
- Set `_attr_unique_id` in `__init__` (format: `{entry_id}_{key}`)
- Use coordinator data only - Never call API directly
- Handle unavailability via `_attr_available`

## Error Handling

**Use specific exceptions from integration's exception module**

**Errors that reach the user** — from a service action handler _and_ from an entity method
(`async_set_native_value`, `async_set_hvac_mode`, …):

- `ServiceValidationError` — the user got something wrong (bad value, unsupported option). The stack trace is only
  logged at debug level, so they see a message rather than a wall of text.
- `HomeAssistantError` — the device or service failed. The full stack trace **is** logged.
- **Never `ValueError`.** It is what these two exist to replace, and it reaches the user as an unhandled crash.

Both take `translation_domain`, `translation_key` and `translation_placeholders` — never a plain English string.

**Logging levels:**

- `_LOGGER.critical()` - System-critical failures
- `_LOGGER.exception()` - Errors with full traceback (in exception handlers)
- `_LOGGER.error()` - Errors affecting functionality
- `_LOGGER.warning()` - Recoverable issues
- `_LOGGER.info()` - Sparingly, user-facing only
- `_LOGGER.debug()` - Detailed troubleshooting

**Log message style:**

- No periods at end (syslog style)
- Never log credentials/tokens/API keys
- Use `%` formatting (enforced by Ruff G004)

## Testing Considerations

**Note: Only write tests when explicitly requested by the developer.**

If you are asked to write tests for entities:

**Example test structure:**

```python
"""Test sensor platform."""

import pytest

from custom_components.{domain}.sensor import async_setup_entry

@pytest.mark.unit
async def test_sensor_setup(hass, config_entry, coordinator):
    """Test sensor platform setup."""
    # Test implementation
```

## Common Patterns

**Config entry data:** `entry.runtime_data.coordinator` / `entry.runtime_data.client` — runtime objects stored during `async_setup_entry()` in `data.py`

**Device info:** Provided via base entity class (manufacturer, model, serial, config URL, firmware)

## Validation

**Recommended workflow — run fix scripts first, they report what they couldn't fix:**

```bash
script/python       # Ruff format + ruff check --fix — output shows remaining errors
script/type-check   # Pyright — no auto-fix, always manual
```

Repeat until both exit 0. Only manually edit files for errors that remain in the output.

**When validation fails:**

- Look up error codes: [Ruff rules](https://docs.astral.sh/ruff/rules/), [Pyright docs](https://microsoft.github.io/pyright/)
- Search [HA docs](https://developers.home-assistant.io/) for patterns
- Fix root cause — don't bypass checks

**Suppressing checks (use sparingly for false positives/library issues):**

- Specific suppression: `# noqa: F401 - Reason` or `# type: ignore[attr-defined] - Reason`
- **Never use blanket:** `# noqa`, `# type: ignore`, `# ruff: noqa`
- Always include error codes and explanatory comments

## Verify Current Patterns

Home Assistant APIs evolve fast enough that a remembered pattern is unreliable. **The installed source in the
devcontainer is the authority** — grep it before trusting recall, a blog post, or an older integration:

```bash
rg -n "deprecated|breaks_in_ha_version" .venv/lib/python*/site-packages/homeassistant/helpers/<module>.py
```

For the procedure and the full deprecation table, see the `ha-modern-apis` agent skill
(`.agents/skills/ha-modern-apis/SKILL.md`). Secondary sources:

- [Home Assistant Developer Docs](https://developers.home-assistant.io/)
- [Developer Blog](https://developers.home-assistant.io/blog/) for deprecations/changes
