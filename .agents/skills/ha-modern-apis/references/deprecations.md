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

| Do not use                                            | Use instead                                                            |
| ----------------------------------------------------- | ---------------------------------------------------------------------- |
| `async_get_device(identifiers=…)` (unscoped)          | `async_get_device_by_identifier(identifier, config_entry_id)`          |
| `async_get_device(connections=…)` (unscoped)          | `async_get_device_by_connection(connection, config_entry_id)`          |
| `DeviceEntry.config_entries` (plural)                 | `DeviceEntry.config_entry_id`                                          |
| `DeviceEntry.config_entries_subentries`               | `DeviceEntry.config_subentry_id`                                       |
| `DeviceEntry.primary_config_entry`                    | `DeviceEntry.config_entry_id`                                          |
| `via_device=(DOMAIN, identifier)`                     | `via_device_id=<device id>` (removal in HA Core 2027.8)                |
| `async_update_device(add_config_entry_id=…/remove_…)` | `async_update_device(new_config_entry_id=…, new_config_subentry_id=…)` |
| `DeviceEntry.suggested_area`                          | Nothing — ignore it; removed in HA Core 2026.9                         |

Additional rules:

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

| Do not use                                 | Use instead                                                     |
| ------------------------------------------ | --------------------------------------------------------------- |
| `requests`, `urllib`, blocking SDK calls   | `aiohttp` via `async_get_clientsession(hass)`                   |
| Creating your own `aiohttp.ClientSession`  | `async_get_clientsession(hass)` (Platinum `inject-websession`)  |
| `async_timeout.timeout(...)`               | `asyncio.timeout(...)`                                          |
| `time.sleep`, `datetime.now()`             | `asyncio.sleep`, `homeassistant.util.dt.utcnow()`               |
| `open()` / `json.load()` in the event loop | `await hass.async_add_executor_job(...)`                        |
| `hass.async_add_job`                       | `hass.async_create_task` / `entry.async_create_background_task` |

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
