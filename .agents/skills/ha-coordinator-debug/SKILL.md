---
name: ha-coordinator-debug
description: >-
  Diagnose and fix runtime problems in this Home Assistant custom integration — entities showing "unavailable" or
  "unknown", stale data, the integration failing to set up, "Config entry not ready", repeated reauth prompts,
  coordinator update failures, timeouts, blocking-call warnings, or exceptions in home-assistant.log. Use when
  asked to "debug", "why is my sensor unavailable", "the integration won't load", "data isn't updating", "check
  the logs", "restart Home Assistant", or when investigating anything in coordinator/, api/, or the setup path.
  Covers the local run loop, log reading, log levels, the coordinator failure contract, and diagnostics. SYMPTOMS
  — load this if you are about to: invent your own `hass`/`pytest` command instead of the project scripts; return
  None or an empty dict from `_async_update_data` to signal failure; catch Exception broadly in the coordinator;
  log on every failed poll; or guess at the payload shape instead of logging it.
---

# Debug the running integration

Work from evidence, not from guesses. The order below is deliberate: reproduce, read the log, localise to a layer, then
fix.

## 1. Reproduce with a clean instance

Always use the project scripts — hand-rolled `hass` or `pip` invocations miss the venv, `PYTHONPATH`, port cleanup, and
debugpy setup, and are the single most common cause of agents getting stuck.

```bash
./script/develop
```

If Home Assistant is unresponsive or the port is held:

```bash
pkill -f "hass --config" || true && pkill -f "debugpy.*5678" || true && ./script/develop
```

Restart after **any** change to Python files, `manifest.json`, `services.yaml`, translations, or the config flow.

## 2. Read the log

- Live: the terminal running `./script/develop`.
- File: `config/home-assistant.log`, previous run in `config/home-assistant.log.1`.

```bash
rg -n "<domain>|Traceback|ERROR|WARNING" config/home-assistant.log | tail -50
```

Raise verbosity in `config/configuration.yaml`, then restart:

```yaml
logger:
  default: warning
  logs:
    custom_components.<domain>: debug
    homeassistant.helpers.update_coordinator: debug
```

Read the **first** error in a cascade, not the last. A wall of "Error doing job" usually has one root cause above it.

## 3. Localise the failure

| Symptom                                           | Layer to inspect                                                                   |
| ------------------------------------------------- | ---------------------------------------------------------------------------------- |
| Integration missing from the add-integration list | `manifest.json`, import error at module load — check log at startup                |
| "Config entry not ready, retrying"                | `_async_update_data` / `_async_setup` raising `ConfigEntryNotReady`                |
| Entry loads, all entities `unavailable`           | coordinator's first refresh failed, or `last_update_success` false                 |
| Entities available but values `unknown`/`None`    | key mismatch between `coordinator.data` and the entity's read path                 |
| Values never change                               | `update_interval`, caching in the API client, or a swallowed error                 |
| Endless reauth prompts                            | `ConfigEntryAuthFailed` raised for a non-auth failure                              |
| "Detected blocking call inside the event loop"    | sync I/O in async code — see [`ha-modern-apis`](../ha-modern-apis/SKILL.md)        |
| Entity duplicated after an update                 | `unique_id` changed — see [`ha-breaking-changes`](../ha-breaking-changes/SKILL.md) |

Cross-check the actual payload rather than assuming its shape:

```python
LOGGER.debug("Coordinator data: %s", self.data)
```

## 4. Check the failure contract

`_async_update_data` communicates through exception type, and getting it wrong is the root of most availability bugs.
The exception mapping table is in
[`blueprint.coordinator.instructions.md`](../../instructions/blueprint.coordinator.instructions.md) and
[`blueprint.api.instructions.md`](../../instructions/blueprint.api.instructions.md). Read the coordinator
against it and check for the four failures that table cannot express:

- **Signalling failure by returning** `None` or an empty dict instead of raising. Entities then show `unknown` forever
  instead of going unavailable, and nothing retries.
- **A broad `except Exception`** that swallows the auth error, so reauth never triggers and the entry just looks broken.
- **Logging on every failed poll.** The coordinator logs the first failure and then stays quiet by design
  (`log-when-unavailable`, Silver). Manual logging buries the real error in repetition.
- **`ConfigEntryNotReady` raised outside setup**, or `async_config_entry_first_refresh()` called outside setup.

## 5. Common fixes

**Update interval too aggressive** — the Bronze `appropriate-polling` rule. Local devices ~30 s, cloud services
~5–15 min. Read it from `entry.options` so the user can tune it.

**Timeouts** — every request needs one, and it must use `async_timeout`/`asyncio.timeout`, never a bare `await`:

```python
async with asyncio.timeout(10):
    response = await self._session.get(url)
```

**Partial data** — when only part of the payload is missing, keep the previous value instead of dropping the whole
update; only raise when the update is genuinely useless.

**Entity reads the wrong key** — compare the `EntityDescription.key` / `value_fn` against the logged payload.

**Setup ordering** — expensive one-off work (fetching device metadata, capabilities) belongs in `_async_setup()`, which
runs once before the first refresh, not in `_async_update_data`.

## 6. Confirm the fix

```bash
script/lint && script/type-check
script/test
```

Restart, reproduce the original scenario, and confirm the log is clean. Then check
_Settings → Devices & services → ⋮ → Download diagnostics_ — if the failure was data-shaped, the diagnostics output
should now show the corrected structure. Diagnostics must run everything through `async_redact_data()`; if you added a
field, make sure it is redacted when sensitive.

## 7. Add a regression test

A runtime bug that reached a user is exactly the case where a test pays for itself. Add one that reproduces the
original failure before the fix. See [`ha-testing`](../ha-testing/SKILL.md).

## Stop conditions

After three failed attempts at the same error, stop and report what you tried and what you observed. Do not keep
looping — a wrong mental model does not improve with repetition.
