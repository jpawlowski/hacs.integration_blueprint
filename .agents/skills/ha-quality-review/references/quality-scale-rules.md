# Integration Quality Scale — full rule list

The authoritative list is `script/hassfest/quality_scale.py` in `home-assistant/core`, and each rule has a page under
<https://developers.home-assistant.io/docs/core/integration-quality-scale/rules/>. Tiers are cumulative: Silver requires
all of Bronze, Gold all of Silver, Platinum all of Gold.

For a **custom** integration the `quality_scale` key in `manifest.json` is optional and is not shown in the Home
Assistant UI. It is still worth setting, because it documents the intended bar. This project targets Silver, ideally
Gold.

## Bronze (20 rules)

| Rule                             | What it requires                                                                               |
| -------------------------------- | ---------------------------------------------------------------------------------------------- |
| `action-setup`                   | Service actions are registered in `async_setup()`, not `async_setup_entry()`                   |
| `appropriate-polling`            | The polling interval is sensible for the data source and documented                            |
| `brands`                         | The integration has an icon/logo in `home-assistant/brands` (not applicable to HACS-only)      |
| `common-modules`                 | Common patterns live in the expected modules (coordinator, base entity)                        |
| `config-flow`                    | Setup happens through the UI, every field has a `data_description`                             |
| `config-flow-test-coverage`      | The config flow has full test coverage, including every abort and error path                   |
| `dependency-transparency`        | Dependencies are published on PyPI, source-available, versioned, and built from a known source |
| `docs-actions`                   | Every service action is documented                                                             |
| `docs-conditions`                | Every condition the integration provides is documented                                         |
| `docs-high-level-description`    | The docs open with what the device/service is and what the integration does                    |
| `docs-installation-instructions` | The docs explain how to install and set it up                                                  |
| `docs-removal-instructions`      | The docs explain how to remove it cleanly                                                      |
| `docs-triggers`                  | Every trigger the integration provides is documented                                           |
| `entity-event-setup`             | Event subscriptions happen in `async_added_to_hass()` and are released on removal              |
| `entity-unique-id`               | Every entity has a stable unique ID                                                            |
| `has-entity-name`                | Entities set `_attr_has_entity_name = True`                                                    |
| `runtime-data`                   | State is stored in `ConfigEntry.runtime_data`, typed via a `ConfigEntry[...]` alias            |
| `test-before-configure`          | The config flow verifies the connection before creating the entry                              |
| `test-before-setup`              | Setup checks reachability and raises `ConfigEntryNotReady` / `ConfigEntryAuthFailed`           |
| `unique-config-entry`            | Duplicate entries for the same device/account are prevented                                    |

## Silver (10 rules)

| Rule                            | What it requires                                                                   |
| ------------------------------- | ---------------------------------------------------------------------------------- |
| `action-exceptions`             | Actions raise `ServiceValidationError` / `HomeAssistantError`, never fail silently |
| `config-entry-unloading`        | The entry unloads cleanly and releases every resource and subscription             |
| `docs-configuration-parameters` | All options-flow parameters are documented                                         |
| `docs-installation-parameters`  | All setup parameters are documented                                                |
| `entity-unavailable`            | Entities report unavailable when data cannot be fetched                            |
| `integration-owner`             | `manifest.json` names at least one codeowner                                       |
| `log-when-unavailable`          | Unavailability is logged once, and recovery is logged once — not every poll        |
| `parallel-updates`              | Every platform declares `PARALLEL_UPDATES`                                         |
| `reauthentication-flow`         | Expired credentials trigger a reauth flow instead of a broken entry                |
| `test-coverage`                 | Above 95% test coverage across all modules                                         |

## Gold (21 rules)

| Rule                         | What it requires                                                                |
| ---------------------------- | ------------------------------------------------------------------------------- |
| `devices`                    | Entities are grouped onto devices with meaningful device info                   |
| `diagnostics`                | Diagnostics are implemented and sensitive values are redacted                   |
| `discovery`                  | The device/service is discovered automatically where the protocol allows        |
| `discovery-update-info`      | Discovery updates network information (e.g. a changed IP) on the existing entry |
| `docs-data-update`           | The docs explain how data is fetched (poll vs. push, interval)                  |
| `docs-examples`              | The docs contain automation examples                                            |
| `docs-known-limitations`     | Known limitations are documented                                                |
| `docs-supported-devices`     | Supported devices/models are listed                                             |
| `docs-supported-functions`   | Supported functionality is described                                            |
| `docs-troubleshooting`       | Common problems and fixes are documented                                        |
| `docs-use-cases`             | Typical use cases are described                                                 |
| `dynamic-devices`            | Devices appearing after setup are added automatically                           |
| `entity-category`            | Diagnostic and configuration entities set `EntityCategory`                      |
| `entity-device-class`        | Entities set a `device_class` where one applies                                 |
| `entity-disabled-by-default` | Noisy or rarely used entities are disabled by default                           |
| `entity-translations`        | Entity names come from `translation_key`, not hardcoded strings                 |
| `exception-translations`     | Raised exceptions use `translation_domain` + `translation_key`                  |
| `icon-translations`          | Icons come from `icons.json`, not `EntityDescription(icon=...)`                 |
| `reconfiguration-flow`       | Users can change settings without deleting and re-adding the entry              |
| `repair-issues`              | Actionable problems raise repair issues, and resolved ones are deleted          |
| `stale-devices`              | Devices that disappear upstream are removed from the registry                   |

## Platinum (3 rules)

| Rule                | What it requires                                                               |
| ------------------- | ------------------------------------------------------------------------------ |
| `async-dependency`  | The library is fully async — no executor jobs wrapping sync calls              |
| `inject-websession` | Home Assistant's shared `aiohttp`/`httpx` session is injected into the library |
| `strict-typing`     | Full type coverage, and any external dependency ships `py.typed`               |
