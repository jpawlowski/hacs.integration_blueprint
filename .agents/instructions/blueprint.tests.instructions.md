---
name: "Tests"
description: "Test layout, fixtures, mocking, registry assertions, and snapshots"
applyTo: "tests/**/*.py"
paths:
  - "tests/**/*.py"
---

# Test Instructions

**Procedure:** [`ha-testing`](../skills/ha-testing/SKILL.md) — load it before writing or repairing a test. This file is
the rule set; the skill is the scaffolding and the judgement calls — what a behavioural change is worth testing for,
and how to diagnose a failure rather than silence it.

**Applies to:** `tests/` directory

**Official documentation:** [Home Assistant Testing](https://developers.home-assistant.io/docs/development_testing)

## Test Structure

**Mirror integration structure:**

```text
tests/
  conftest.py          # Shared fixtures
  test_init.py         # Integration setup
  test_config_flow.py  # Config flow
  sensor/test_air_quality.py
  binary_sensor/test_filter.py
```

**File organization:**

- One test file per module/feature
- Named `test_*.py`
- Use fixtures from `conftest.py`

## Pytest Markers

**Categorize tests:**

- `@pytest.mark.unit` - Fast, isolated (no external dependencies)
- `@pytest.mark.integration` - With coordinator, time service, etc.

## Fixtures

**Standard fixtures (define in `conftest.py`):**

- `hass` - Mock Home Assistant instance
- `config_entry` - `MockConfigEntry` from `pytest-homeassistant-custom-component`
- `coordinator` - The project's `DataUpdateCoordinator` instance
- `mock_api_client` - Mocked API client
- `hass_client` - From `pytest_homeassistant_custom_component.typing`; an authenticated aiohttp client against the
  HTTP API. Needed for anything served over HTTP, diagnostics above all.
- `freezer` - `pytest-freezegun`; advance with `freezer.tick()` plus `async_fire_time_changed`, never `time.sleep`

**Define fixtures in `conftest.py`:** Use `MockConfigEntry` from `pytest-homeassistant-custom-component`

**Use [Syrupy](https://github.com/tophat/syrupy) for large outputs:**

- Snapshots for: Entity states, registry entries, diagnostics, config flow results
- Update: `script/test --snapshot-update`, commit `.ambr` files
- The file is named after the test file and lives in `snapshots/` beside it — `test_sensor.py` →
  `snapshots/test_sensor.ambr`. Renaming a test file orphans its snapshot.
- Complement functional tests, don't replace them. A snapshot asserts "unchanged since I recorded it", which assumes
  the recording was right. To check that an entity goes unavailable on an API error, assert that specific state —
  do not snapshot the whole entity and hope.
- Pattern: `assert hass.states.get("sensor.x") == snapshot`

## Core Interface Testing

**Rule: Test through core interfaces, not integration internals.** The point is not purity — it is that a test which
reaches into the integration has to be rewritten every time the integration is refactored, so it stops being a safety
net exactly when one is needed.

✅ **Correct:** `async_setup_component` or `hass.config_entries.async_setup`, `MockConfigEntry`, `hass.states`,
`hass.services`, `entry.state`, and the device and entity registries

❌ **Wrong:** Direct entity instantiation, reading entity properties, reaching into `entry.runtime_data`

## Registry Testing

**Registry Testing:**

- Device: `dr.async_get(hass).async_get_device_by_identifier((DOMAIN, id), config_entry.entry_id)` - Verify
  manufacturer, model, identifiers, and ownership by `config_entry_id`
- Entity: `er.async_get(hass).async_get("sensor.x")` - Verify unique_id, disabled state
- Lifecycle: Test `async_setup()` → `LOADED`, `async_unload()` → `NOT_LOADED`
- Multiple entries: When two entries expose the same identifier or connection, verify that each entry owns a separate
  device and that entry-scoped lookups return the correct one
- Subentries: Verify that each subentry owns a separate device; never assert or depend on a device shared by subentries

**Never use in new tests:** The deprecated unscoped `async_get_device()` lookup or the plural
`DeviceEntry.config_entries` / `DeviceEntry.config_entries_subentries` compatibility properties.

## Mocking

**Mocking:**

✅ **Mock:** External APIs, network calls, time-dependent operations

- Use `patch.object()` for success cases, `side_effect` for errors
- Pattern: `with patch.object(client, "method", return_value=data):`

❌ **Don't mock:** Home Assistant internals, your own integration code

## Entity Testing

**Entity Testing:**

Pattern: Setup entry → `async_block_till_done()` → `hass.states.get("entity_id")` → assert state/attributes

## Config Flow Testing

**Config Flow Testing:**

Pattern: `hass.config_entries.flow.async_init(DOMAIN, context={"source": "user"}, data={...})`

Verify: `result["type"]` (form/create_entry/abort), `result["step_id"]`, `result["errors"]`

## Test Commands

```bash
script/test                    # All tests
script/test -v                 # Verbose
script/test --cov-html         # Coverage report (htmlcov/index.html)
script/test tests/sensor/      # Specific directory
script/test -k test_sensor     # Pattern matching
script/test -m unit            # Marker filtering
script/test --snapshot-update  # Update snapshots
script/test -x                 # Stop at the first failure — the one to use while iterating
script/test --cov-report term-missing   # Coverage with the uncovered lines listed in the terminal
```

`development_testing.md` upstream is mostly the **Core** workflow — `prek`, `script/gen_requirements_all.py` and its
`pytest ./tests/components/...` paths do not exist here. Take its patterns, not its commands.

## Coverage targets

Coordinator logic, config flow validation, error handling, entity state calculations. Check with
`script/test --cov-html`.

[Home Assistant Core's own tests](https://github.com/home-assistant/core/tree/dev/tests/components) are the reference
for a pattern this file does not cover.
