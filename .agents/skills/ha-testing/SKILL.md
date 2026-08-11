---
name: ha-testing
description: >-
  Write, fix, or extend automated tests for this Home Assistant custom integration using pytest and
  pytest-homeassistant-custom-component. Use when asked to "add tests", "write a test", "the tests fail", "improve
  coverage", "add a regression test", "test the config flow", "update snapshots", or when a behavioural change
  needs verification before it can be called done. Covers the tests/ layout, the conftest.py fixtures this project
  needs, mocking the API client, config flow and entity test patterns, registry assertions, syrupy snapshots,
  freezing time, and the script/test commands. SYMPTOMS — load this if you are about to: instantiate an entity
  class directly instead of asserting on `hass.states`; write a test without `enable_custom_integrations`; use
  `time.sleep` instead of `async_fire_time_changed`; silence a DeprecationWarning to make the suite pass; or
  commit a snapshot you have not read.
---

# Testing

Home Assistant tests are integration tests by nature: you load a real config entry into a real `hass` instance and
assert on `hass.states` — not on Python objects.

**Read [`blueprint.tests.instructions.md`](../../instructions/blueprint.tests.instructions.md) first** — it
holds the rules: directory mirroring, pytest markers, which fixtures to define, the core-interface rule, registry
assertions, what to mock and what never to mock, the full command list, and the do/don't list. This skill is the
scaffolding and the judgement calls.

## When a test is required

- Behavioural change, bug fix, or regression → add a proportionate test.
- Documentation-only, formatting-only, or anything that cannot affect runtime → no test needed.
- If a test is impractical (needs real hardware, non-deterministic timing), say so explicitly and describe the residual
  risk. Do not silently skip it, and never claim coverage that does not exist.

## Bootstrap: `tests/conftest.py`

The suite currently has no `conftest.py`. Custom integrations are **not** loaded by default in tests, so the first thing
any new test file needs is this — create it once:

```python
"""Shared fixtures for <domain> tests."""

from collections.abc import Generator
from unittest.mock import AsyncMock, patch

import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.<domain>.const import DOMAIN
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME
from homeassistant.core import HomeAssistant


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations: None) -> None:
    """Load the custom integration in every test."""


@pytest.fixture
def mock_config_entry() -> MockConfigEntry:
    """Return a config entry for the integration."""
    return MockConfigEntry(
        domain=DOMAIN,
        title="Example Device",
        data={CONF_USERNAME: "test-user", CONF_PASSWORD: "test-password"},
        unique_id="test-unique-id",
    )


@pytest.fixture
def mock_api_client() -> Generator[AsyncMock]:
    """Patch the API client with a mock that returns fixture data."""
    with patch(
        "custom_components.<domain>.{ClassPrefix}ApiClient",
        autospec=True,
    ) as client_class:
        client = client_class.return_value
        client.async_get_data.return_value = {"model": "Blueprint", "title": "ok"}
        yield client


@pytest.fixture
async def init_integration(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry,
    mock_api_client: AsyncMock,
) -> MockConfigEntry:
    """Set up the integration and return the loaded entry."""
    mock_config_entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()
    return mock_config_entry
```

Patch the client where it is **imported**, not where it is defined. `autospec=True` makes the mock fail when the real
signature changes, which is the whole point.

## Layout

`tests/` mirrors `custom_components/<domain>/`:

```text
tests/
├── conftest.py
├── test_init.py               # setup, unload, reload, migration
├── test_config_flow.py        # user, reauth, reconfigure, options, discovery
├── test_diagnostics.py        # snapshot + redaction
├── sensor/test_air_quality.py
└── snapshots/                 # syrupy .ambr files, committed
```

## Patterns

### Setup and unload lifecycle

```python
async def test_setup_and_unload(hass: HomeAssistant, init_integration: MockConfigEntry) -> None:
    """The entry loads and unloads cleanly."""
    assert init_integration.state is ConfigEntryState.LOADED

    assert await hass.config_entries.async_unload(init_integration.entry_id)
    await hass.async_block_till_done()
    assert init_integration.state is ConfigEntryState.NOT_LOADED
```

### Setup failure

```python
@pytest.mark.parametrize(
    ("error", "expected_state"),
    [
        ({ClassPrefix}ApiClientCommunicationError, ConfigEntryState.SETUP_RETRY),
        ({ClassPrefix}ApiClientAuthenticationError, ConfigEntryState.SETUP_ERROR),
    ],
)
async def test_setup_failures(hass, mock_config_entry, mock_api_client, error, expected_state) -> None:
    """Client failures map onto the right entry state."""
    mock_api_client.async_get_data.side_effect = error
    mock_config_entry.add_to_hass(hass)
    await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()
    assert mock_config_entry.state is expected_state
```

### Entity state

```python
async def test_sensor_state(hass: HomeAssistant, init_integration: MockConfigEntry) -> None:
    """The sensor exposes the coordinator value."""
    state = hass.states.get("sensor.example_device_pm25")
    assert state is not None
    assert state.state == "12.3"
    assert state.attributes[ATTR_UNIT_OF_MEASUREMENT] == "µg/m³"
```

Never instantiate an entity class directly — go through `hass.states`.

### Config flow

```python
async def test_user_flow(hass: HomeAssistant, mock_api_client: AsyncMock) -> None:
    """The happy path creates an entry."""
    result = await hass.config_entries.flow.async_init(DOMAIN, context={"source": SOURCE_USER})
    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "user"

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {CONF_USERNAME: "test-user", CONF_PASSWORD: "test-password"},
    )
    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["result"].unique_id == "test-unique-id"
```

Parametrise the error branches (`invalid_auth`, `cannot_connect`, `unknown`) and always assert that the flow **recovers**
— show the form again with the error, then succeed on the second attempt. `config-flow-test-coverage` (Bronze) expects
every step and every abort reason to be exercised.

### Time-driven updates

```python
freezer.tick(DEFAULT_SCAN_INTERVAL)
async_fire_time_changed(hass)
await hass.async_block_till_done()
```

Use the `freezer` fixture from `freezegun` and `async_fire_time_changed`. `time.sleep()` in a test is always wrong.

### Snapshots

```python
async def test_diagnostics(hass, hass_client, init_integration, snapshot: SnapshotAssertion) -> None:
    """Diagnostics output is stable and redacted."""
    assert await get_diagnostics_for_config_entry(hass, hass_client, init_integration) == snapshot
```

Snapshots are for large stable structures (diagnostics, entity registry dumps). They complement functional assertions;
they do not replace them. Regenerate with `script/test --snapshot-update` and **read the diff** before committing the
`.ambr` file — an accepted snapshot of a bug is worse than no test.

## Two settings that surprise people

**Warnings are errors.** `filterwarnings = ["error"]` in `pyproject.toml` means a `DeprecationWarning` from Home
Assistant fails the suite. That is the intended early-warning system — fix the deprecation
([`ha-modern-apis`](../ha-modern-apis/SKILL.md)) rather than adding an ignore.

The exception is a warning **Home Assistant Core raises about its own use of a library it pins**, which no change
here can fix and which would otherwise block every test that touches that subsystem — the aiohttp warnings from
`homeassistant/helpers/aiohttp_client.py` and `homeassistant/components/http/` are the ones already ignored. Before
adding one, confirm the warning's origin is a Core file and not this integration; a warning about our own code stays
an error. Then key the ignore to the exact message rather than the category, and say in a comment where it comes from
and why it cannot be fixed here — a bare `DeprecationWarning` ignore also hides the next real deprecation.

**`asyncio_mode = "auto"`**, so async tests need no `@pytest.mark.asyncio`.

The command list is in the instructions file.

## Coverage priorities

Order of value, highest first: config flow branches → setup/unload/migration → coordinator error translation → entity
state and availability → service action error paths → diagnostics redaction. Chase behaviour, not a percentage.

## Do not

- Do not mock `aiohttp` at the transport level when mocking the client is enough — you end up testing your mock.
- Do not assert on log output as a substitute for asserting on state.
- Do not commit a snapshot you have not read.
- Do not report coverage you did not measure, or describe a test as passing without running it.

The remaining rules are in
[`blueprint.tests.instructions.md`](../../instructions/blueprint.tests.instructions.md).
