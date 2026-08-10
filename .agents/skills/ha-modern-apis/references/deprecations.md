# Deprecated Home Assistant APIs and their replacements

Verified against the Home Assistant version pinned in this devcontainer. Check with:

```bash
.venv/bin/python -c "from homeassistant.const import __version__; print(__version__)"
```

When an entry here disagrees with the installed source, the installed source wins — grep it:

```bash
rg -n "deprecated|breaks_in_ha_version" .venv/lib/python*/site-packages/homeassistant/helpers/<module>.py
```

## Device registry — single config entry ownership

Since Home Assistant 2026.8 a device is owned by **exactly one** config entry and at most one config subentry.
Identifiers and connections are unique only _within_ the owning entry, never globally.

**Deprecated in the source, with a removal version** — these carry `@deprecated_function` or a reported usage, so
grepping confirms them:

| Do not use                                                                                            | Use instead                                                            | Removed |
| ----------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------- | ------- |
| `via_device=(DOMAIN, identifier)`                                                                     | `via_device_id=<device id>`                                            | 2027.8  |
| `DeviceEntry.suggested_area`, `DeviceInfo["suggested_area"]`, `async_get_or_create(suggested_area=…)` | Nothing — the user places devices in areas                             | 2026.9  |
| `async_update_device(add_config_entry_id=…/remove_…)`                                                 | `async_update_device(new_config_entry_id=…, new_config_subentry_id=…)` | —       |
| `DeviceEntry.config_entries` (plural)                                                                 | `DeviceEntry.config_entry_id`                                          | shim    |
| `DeviceEntry.config_entries_subentries`                                                               | `DeviceEntry.config_subentry_id`                                       | shim    |
| `DeviceEntry.primary_config_entry`                                                                    | `DeviceEntry.config_entry_id`                                          | shim    |

**Not deprecated in the source, but banned in this project** — grepping will find no warning, so the reason matters:

| Do not use                                   | Use instead                                                   | Why                                                                                                  |
| -------------------------------------------- | ------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------- |
| `async_get_device(identifiers=…)` (unscoped) | `async_get_device_by_identifier(identifier, config_entry_id)` | Resolves ambiguously across entries — it prefers a matching domain, then falls back to the first hit |
| `async_get_device(connections=…)` (unscoped) | `async_get_device_by_connection(connection, config_entry_id)` | Same                                                                                                 |

Additional rules:

- Passing **both** `via_device` and `via_device_id` raises at runtime. When migrating, remove the old one.
- Passing a pre-migration composite device id as `via_device_id` is reported and breaks in 2027.8 — pass the id of a
  single device.
- Inside an entity use `self.device_entry`; do not look the device up again.
- Never attach this integration's config entry to a device owned by another integration. A helper entity links to the
  source device through `self.device_entry`.
- Every config subentry gets its own device. Two subentries must never share one.
- A hub/account and its subentry devices are separate devices, related through `via_device_id`.
- The composite-device compatibility shims are temporary and scheduled for removal in HA Core 2027.8. Do not build on
  them.

These rules apply to migrations, repairs, diagnostics, registry listeners, **and tests**.

## Config entry runtime state

| Do not use                                  | Use instead                                                      |
| ------------------------------------------- | ---------------------------------------------------------------- |
| `hass.data[DOMAIN][entry.entry_id] = …`     | `entry.runtime_data = {ClassPrefix}Data(...)`                    |
| Untyped `ConfigEntry`                       | `type {ClassPrefix}ConfigEntry = ConfigEntry[{ClassPrefix}Data]` |
| `async_forward_entry_setup` (singular)      | `async_forward_entry_setups(entry, PLATFORMS)`                   |
| `entry.add_update_listener` without cleanup | `entry.async_on_unload(entry.add_update_listener(...))`          |

## Config flow

| Do not use                                                   | Use instead                                                  |
| ------------------------------------------------------------ | ------------------------------------------------------------ |
| `FlowResult`                                                 | `ConfigFlowResult`                                           |
| `self.hass.config_entries.async_get_entry(...)` in reauth    | `self._get_reauth_entry()` / `self._get_reconfigure_entry()` |
| Manual update + `async_abort` + reload                       | `self.async_update_reload_and_abort(entry, data_updates=…)`  |
| Manual unique-ID comparison                                  | `self._abort_if_unique_id_mismatch(reason="wrong_device")`   |
| `config_entries.OptionsFlow` storing `self.config_entry`     | The base class provides `self.config_entry`                  |
| YAML `async_setup_platform` for a device/service integration | Config flow only (ADR-0010)                                  |

## Entities

| Do not use                                        | Use instead                                                   |
| ------------------------------------------------- | ------------------------------------------------------------- |
| `DEVICE_CLASS_*` module constants                 | `SensorDeviceClass.*`, `BinarySensorDeviceClass.*`, …         |
| `EntityDescription(name="Temperature")`           | `translation_key="temperature"` + `translations/en.json`      |
| `EntityDescription(icon="mdi:x")`                 | `icons.json`                                                  |
| `self.schedule_update_ha_state()` from async code | `self.async_write_ha_state()`                                 |
| `async_update()` on a coordinator-backed entity   | Read `self.coordinator.data`                                  |
| `_attr_name` when `has_entity_name` is set        | `translation_key`, or `_attr_name = None` for the main entity |

## Async and I/O

| Do not use                                      | Use instead                                                      |
| ----------------------------------------------- | ---------------------------------------------------------------- |
| `requests`, `urllib`, blocking SDK calls        | `aiohttp` via `async_get_clientsession(hass)`                    |
| Creating your own `aiohttp.ClientSession`       | `async_get_clientsession(hass)` (Platinum `inject-websession`)   |
| `async_timeout.timeout(...)`                    | `asyncio.timeout(...)`                                           |
| `time.sleep`, `datetime.now()`                  | `asyncio.sleep`, `homeassistant.util.dt.utcnow()`                |
| `open()` / `json.load()` in the event loop      | `await hass.async_add_executor_job(...)`                         |
| `hass.async_add_job`                            | `entry.async_create_task` / `entry.async_create_background_task` |
| An `async_*` API from a worker thread           | Its sync twin — table in `blueprint.python.instructions.md`      |
| `async_track_state_change`                      | `async_track_state_change_event`                                 |
| `hass.bus.async_listen(EVENT_STATE_CHANGED)`    | `async_track_state_change_event`                                 |
| `hass.bus.async_listen(EVENT_COMPONENT_LOADED)` | `homeassistant.helpers.start.async_at_start`                     |

## Diagnostics

| Do not use                                                    | Use instead                                      |
| ------------------------------------------------------------- | ------------------------------------------------ |
| `homeassistant.components.diagnostics.util.async_redact_data` | `homeassistant.helpers.redact.async_redact_data` |

## Recent behavioural changes worth knowing (2026)

- **Button event entities** have a standard `ButtonEventType` enum — use it instead of free-text event types.
- **Device tracker**: `battery_level` is deprecated (expose a battery sensor entity instead) and `location_name` is
  replaced by `in_zones`; `BaseScannerEntity` and a `tracking_type` capability attribute were added.
- **Media sources** can implement `async_search_media`.
- **Modbus** connections are shared through the separate `modbus_connection` integration.
- Home Assistant published an official **AI policy** for contributions to its own repositories: AI assistance is fine,
  autonomous pull requests are not. That governs contributions to Open Home Foundation repos, not this custom
  integration — see [`AI_POLICY.md`](../../../../AI_POLICY.md) for what applies here.
