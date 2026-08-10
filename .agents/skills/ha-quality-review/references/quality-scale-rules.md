# Integration Quality Scale — full rule list

The authoritative list is `script/hassfest/quality_scale.py` in `home-assistant/core`, and each rule has a page under
<https://developers.home-assistant.io/docs/core/integration-quality-scale/rules/>. Tiers are cumulative: Silver requires
all of Bronze, Gold all of Silver, Platinum all of Gold.

For a **custom** integration the `quality_scale` key in `manifest.json` is optional and is not shown in the Home
Assistant UI. It is still worth setting, because it documents the intended bar. This project targets Silver, ideally
Gold.

## Bronze (20 rules)

| Rule                             | What it requires                                                                                                                                                                                 |
| -------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `action-setup`                   | Actions are registered in `async_setup()`, and each handler resolves its entry and checks `ConfigEntryState.LOADED`                                                                              |
| `appropriate-polling`            | Coordinator `update_interval`, or `SCAN_INTERVAL` in the platform when `_attr_should_poll`; minimum 5 s, sensible for the source, documented                                                     |
| `brands`                         | Icon and logo ship in `custom_components/<domain>/brand/` (HA 2026.3+); `home-assistant/brands` is Core-only                                                                                     |
| `common-modules`                 | The coordinator and the base entity live in the expected place. Upstream says `coordinator.py` and `entity.py`; this project's `coordinator/` and `entity/` packages are the accepted equivalent |
| `config-flow`                    | Setup happens through the UI; every field has a `data_description`; everything needed to connect is in `ConfigEntry.data` and everything else in `ConfigEntry.options`                           |
| `config-flow-test-coverage`      | The config flow has full test coverage, including every abort and error path                                                                                                                     |
| `dependency-transparency`        | Four separate checks: OSI-approved licence, published on PyPI with a source distribution, built by a public CI pipeline, and the PyPI version matches a tagged release. The tracker must be open |
| `docs-actions`                   | Every service action is documented                                                                                                                                                               |
| `docs-conditions`                | Every condition the integration provides is documented                                                                                                                                           |
| `docs-high-level-description`    | The docs open with what the device/service is and what the integration does                                                                                                                      |
| `docs-installation-instructions` | The docs explain how to install and set it up                                                                                                                                                    |
| `docs-removal-instructions`      | The docs explain how to remove it cleanly                                                                                                                                                        |
| `docs-triggers`                  | Every trigger the integration provides is documented                                                                                                                                             |
| `entity-event-setup`             | Event subscriptions happen in `async_added_to_hass()` and are released on removal                                                                                                                |
| `entity-unique-id`               | Every entity has a stable unique ID                                                                                                                                                              |
| `has-entity-name`                | Entities set `_attr_has_entity_name = True`. Leaving it False is deprecated upstream, not a style choice                                                                                         |
| `runtime-data`                   | State is stored in `ConfigEntry.runtime_data`, typed via a `ConfigEntry[...]` alias                                                                                                              |
| `test-before-configure`          | The config flow verifies the connection before creating the entry                                                                                                                                |
| `test-before-setup`              | Setup checks reachability and raises `ConfigEntryNotReady` / `ConfigEntryAuthFailed`                                                                                                             |
| `unique-config-entry`            | Duplicate entries for the same device/account are prevented                                                                                                                                      |

## Silver (10 rules)

| Rule                            | What it requires                                                                                                                                                                        |
| ------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `action-exceptions`             | Actions raise `ServiceValidationError` / `HomeAssistantError`, never fail silently                                                                                                      |
| `config-entry-unloading`        | The entry unloads cleanly and releases every resource and subscription                                                                                                                  |
| `docs-configuration-parameters` | All options-flow parameters are documented                                                                                                                                              |
| `docs-installation-parameters`  | All setup parameters are documented                                                                                                                                                     |
| `entity-unavailable`            | Entities report unavailable when the fetch fails. A fetch that succeeded but lacks one value is `unknown`, not unavailable                                                              |
| `integration-owner`             | `manifest.json` names at least one codeowner                                                                                                                                            |
| `log-when-unavailable`          | Logged once at **`info`** level on the way down and once on recovery, never per poll. With a coordinator this is automatic; without one it needs an explicit `_unavailable_logged` flag |
| `parallel-updates`              | Every platform declares `PARALLEL_UPDATES`                                                                                                                                              |
| `reauthentication-flow`         | Expired credentials trigger a reauth flow instead of a broken entry                                                                                                                     |
| `test-coverage`                 | Above 95% test coverage across all modules                                                                                                                                              |

## Gold (21 rules)

| Rule                         | What it requires                                                                                                                                                                                                                |
| ---------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `devices`                    | Entities are grouped onto devices with meaningful device info                                                                                                                                                                   |
| `diagnostics`                | Diagnostics are implemented and sensitive values are redacted                                                                                                                                                                   |
| `discovery`                  | The device/service is discovered automatically where the protocol allows                                                                                                                                                        |
| `discovery-update-info`      | Discovery updates network information (e.g. a changed IP) on the existing entry                                                                                                                                                 |
| `docs-data-update`           | The docs explain how data is fetched (poll vs. push, interval)                                                                                                                                                                  |
| `docs-examples`              | The docs contain automation examples                                                                                                                                                                                            |
| `docs-known-limitations`     | Known limitations are documented                                                                                                                                                                                                |
| `docs-supported-devices`     | Supported devices/models are listed                                                                                                                                                                                             |
| `docs-supported-functions`   | Supported functionality is described                                                                                                                                                                                            |
| `docs-troubleshooting`       | Common problems and fixes are documented                                                                                                                                                                                        |
| `docs-use-cases`             | Typical use cases are described                                                                                                                                                                                                 |
| `dynamic-devices`            | A listener diffs `set(coordinator.data)` against a `known_devices` set and adds the new ones — not a one-off filter at setup                                                                                                    |
| `entity-category`            | Diagnostic and configuration entities set `EntityCategory`                                                                                                                                                                      |
| `entity-device-class`        | Entities set a `device_class` where one applies                                                                                                                                                                                 |
| `entity-disabled-by-default` | Noisy or rarely used entities are disabled by default                                                                                                                                                                           |
| `entity-translations`        | Entity names come from `translation_key`, except where a `device_class` already names the entity                                                                                                                                |
| `exception-translations`     | Raised exceptions use `translation_domain` + `translation_key`                                                                                                                                                                  |
| `icon-translations`          | Icons come from `icons.json`, not `EntityDescription(icon=...)`. Do **not** override an icon the device class already gives — a PM2.5 sensor needs none                                                                         |
| `reconfiguration-flow`       | Users can change settings without deleting and re-adding the entry                                                                                                                                                              |
| `repair-issues`              | Actionable problems raise repair issues, and resolved ones are deleted. Do not raise one for something the user cannot fix themselves                                                                                           |
| `stale-devices`              | Devices that disappear upstream are removed. The upstream example predates 2026.8 — use `async_get_device_by_identifier(identifier, entry_id)` and `new_config_entry_id=`, not the unscoped lookup or `remove_config_entry_id=` |

## Platinum (3 rules)

| Rule                | What it requires                                                                                                                                                                                  |
| ------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `async-dependency`  | The library is fully async — no executor jobs wrapping sync calls                                                                                                                                 |
| `inject-websession` | Home Assistant's shared `aiohttp`/`httpx` session is injected. Exception: when cookies must not be shared, create an isolated one with `async_create_clientsession` / `create_async_httpx_client` |
| `strict-typing`     | Full type coverage, and any external dependency ships `py.typed`                                                                                                                                  |
