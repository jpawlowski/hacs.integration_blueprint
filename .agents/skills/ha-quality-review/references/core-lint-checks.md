# Checks Home Assistant Core lints, and this repository cannot

Home Assistant Core ships a pylint plugin (`pylint/plugins/pylint_home_assistant` in `home-assistant/core`) with
integration-specific checkers that need type inference, `manifest.json`, or cross-file analysis — things a per-file
linter cannot do. Its README states it is for Core's own CI and **not** intended for linting custom integration
repositories: it is not published to PyPI, and its path filters expect `homeassistant/components/…`.

So these are review checks, not tooling. Ruff, pyright, hassfest and `references/quality-scale-rules.md` already
cover the rest; what follows is the part that otherwise reaches nobody. The identifier in the first column is Core's,
kept so a finding can be traced back to the upstream rule.

## Unique IDs

Migrating a unique ID after release breaks every existing install, so these are the most expensive to get wrong.

| Core rule | Check                                                                                                                                                                                                                                           |
| --------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `W7406`   | `async_set_unique_id()` is never given an IP address or hostname — including indirectly via a variable holding `data[CONF_HOST]`.                                                                                                               |
| `W7424`   | No entity assigns a literal `_attr_unique_id` in the class body. Unique IDs are scoped per `(domain, platform)` across all config entries, so a constant collides on the second entry unless the manifest declares `single_config_entry: true`. |
| `W7425`   | The unique ID does not contain the integration's domain, in a literal or through `DOMAIN` — the registry key already carries it.                                                                                                                |
| `W7427`   | The unique ID does not contain the entity platform name (`sensor`, `light`, …) either, for the same reason.                                                                                                                                     |

## Config flow

| Core rule | Check                                                                                                                                                                         |
| --------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `W7407`   | No polling-interval field (`CONF_SCAN_INTERVAL`, `update_interval`, `refresh_interval`) in any config or options schema — the author picks the interval, not the user.        |
| `W7408`   | No name field (`CONF_NAME`, `"name"`, `CONF_DEVICE_NAME`) in the schema; the name comes from the device or from discovery. Helper integrations and subentry flows are exempt. |

## Entities and platforms

| Core rule | Check                                                                                                                                                                                                                                                    |
| --------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `W7416`   | `_attr_has_entity_name = True` holds statically — class level, unconditionally at the top of a method, or via the `EntityDescription`. A conditional assignment does not count.                                                                          |
| `C7412`   | No `EntityDescription` field is set to a default the class hierarchy already declares (`None`, `True`, `False`). `name=None` is **not** such a case — the field defaults to `UNDEFINED`, and `None` is the deliberate "name it after the device" marker. |
| `C7409`   | The `PLATFORMS` list is sorted alphabetically.                                                                                                                                                                                                           |
| `C7411`   | An entity class deriving from a platform base lives in that platform's package, never in `__init__.py` or an unrelated module.                                                                                                                           |
| `E7404`   | Entity methods that require it call `super()`. In `async_added_to_hass` this is not ceremony: subscribing before the base class has run breaks any callback touching `self.hass` or writing state.                                                       |
| `W7429`   | No `format_mac()` inside a `CONNECTION_NETWORK_MAC` tuple passed as `connections=` — the device registry normalises it already. Comparisons against `device.connections` still need it.                                                                  |

## Service actions and errors

| Core rule | Check                                                                                                                                              |
| --------- | -------------------------------------------------------------------------------------------------------------------------------------------------- |
| `E7405`   | No action handler swallows an exception. An empty `except`, one that only logs, and `contextlib.suppress(...)` all hide the failure from the user. |
| `W7414`   | Action registration happens in `async_setup()`, never in `async_setup_entry()`.                                                                    |
| `W7417`   | Raised `HomeAssistantError` subclasses carry `translation_domain` and `translation_key`, not an English message.                                   |
| `E7418`   | Every placeholder the translated message expects is supplied in `translation_placeholders`.                                                        |
| `E7409`   | Every `mdi:` name referenced in Python exists in the Material Design Icons set.                                                                    |
| `E7410`   | The same for every `mdi:` name in `icons.json`.                                                                                                    |

## Runtime and time handling

| Core rule | Check                                                                                                                            |
| --------- | -------------------------------------------------------------------------------------------------------------------------------- |
| `W7405`   | State lives in `entry.runtime_data`, never `hass.data[DOMAIN]`.                                                                  |
| `W7415`   | Consecutive `async_add_executor_job()` calls are merged into one job instead of bouncing back to the event loop between them.    |
| `C7414`   | `dt_util.utcnow()` rather than `datetime.now(UTC)`.                                                                              |
| `C7425`   | `dt_util.now()` rather than `datetime.now(<tz>)`.                                                                                |
| `C7427`   | `dt_util.naive_now()` rather than a bare `datetime.now()`.                                                                       |
| `C7413`   | No constant redefines one `homeassistant.const` already exports with the same value.                                             |
| `C7410`   | Micro-prefixed units use the Greek small letter mu (U+03BC `μ`), not the ANSI micro sign (U+00B5 `µ`) — they render identically. |
| `C7401`   | Log messages do not end in a period.                                                                                             |
| `C7402`   | Log messages above debug level start with a capital letter; if a message does not warrant one, it belongs at debug level.        |

## Manifest

| Core rule | Check                                                                                                                                               |
| --------- | --------------------------------------------------------------------------------------------------------------------------------------------------- |
| `W7430`   | A config flow using `SerialPortSelector` declares `usb` in `dependencies` — `after_dependencies` does not force the `usb` integration to be set up. |

## Tests

Also worth raising in a review of `tests/`; the procedure for fixing them is
[`ha-testing`](../../ha-testing/SKILL.md).

| Core rule | Check                                                                                                                                                                                      |
| --------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `W7409`   | No `if` or `match` inside a test body — a branch that never runs hides a failure. Use `@pytest.mark.parametrize` or split the test. Guard clauses and branches without an assert are fine. |
| `R7404`   | Registry access goes through the `entity_registry` / `device_registry` / `issue_registry` fixtures, not `er.async_get(hass)`.                                                              |
| `R7402`   | A fixture argument a test never references becomes `@pytest.mark.usefixtures("name")`.                                                                                                     |
| `W7404`   | Fixture files are read with async I/O, so the event loop is not blocked.                                                                                                                   |
| `W7418`   | Tests drive setup through the public path, not by calling `async_setup_entry()` (or `async_setup`, `async_migrate_entry`, `async_unload_entry`) directly.                                  |
