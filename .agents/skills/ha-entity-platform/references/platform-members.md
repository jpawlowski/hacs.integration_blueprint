# Per-platform members and their traps

What each entity platform requires you to implement, and the rule per platform that is easiest to get wrong. Read the
row for the platform you are adding — not the whole file.

The general rules (descriptions, translation keys, `PARALLEL_UPDATES`, device info, availability) are in
[`blueprint.entities.instructions.md`](../../../instructions/blueprint.entities.instructions.md); this file is only
what differs per platform.

## Sensor and binary sensor

| Platform        | Required       | Notes                                                                  |
| --------------- | -------------- | ---------------------------------------------------------------------- |
| `sensor`        | `native_value` | `device_class` drives unit conversion; see the state-class rules below |
| `binary_sensor` | `is_on`        | Use `BinarySensorDeviceClass`, not icons                               |

**State class is not universal.** `SensorStateClass.MEASUREMENT` must **not** be combined with a `device_class` of
`DATE`, `ENUM`, `ENERGY`, `GAS`, `MONETARY`, `TIMESTAMP`, `VOLUME` or `WATER`. A meter is `TOTAL` or
`TOTAL_INCREASING`, never `MEASUREMENT` — the blanket "set a state class on every number" rule produces an invalid
combination exactly here.

- `TOTAL` without `last_reset` is the recommended default.
- `TOTAL_INCREASING` for a value that only rises and resets to zero — a drop of more than 10% is read as a new cycle.
- `SensorDeviceClass.ENUM` requires `options` and **cannot** carry `state_class` or `native_unit_of_measurement`.
- `SensorDeviceClass.DURATION` must not change just because time passes.
- `suggested_display_precision` decides how the value renders; without it a raw `21.34567` is shown in full.
- `suggested_unit_of_measurement` overrides the automatic conversion when the device class' default is wrong.
- Restoring state after a restart needs `RestoreSensor` and `async_get_last_sensor_data()` — plain `RestoreEntity`
  does not store `native_value`. Same for `RestoreNumber` / `async_get_last_number_data()`.
- `BinarySensorDeviceClass.UPDATE` should be avoided; use an `update` entity.

## Controls

| Platform | Required                                           | Notes                                                                                                                      |
| -------- | -------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------- |
| `switch` | `is_on`, `async_turn_on`, `async_turn_off`         | refresh after write                                                                                                        |
| `button` | `async_press`                                      | stateless; no `is_on`. `ButtonDeviceClass.IDENTIFY` belongs in `DIAGNOSTIC`                                                |
| `number` | `native_value`, `async_set_native_value`           | `native_min_value` (0), `native_max_value` (100), `native_step`; `mode` is `auto`/`box`/`slider` and `auto` is recommended |
| `select` | `current_option`, `options`, `async_select_option` | options are translated via `state` keys, in `snake_case`                                                                   |
| `text`   | `native_value`, `async_set_value`                  | `native_min`, `native_max`, `pattern`, `mode` (`text` or `password`)                                                       |
| `time`   | `native_value`, `async_set_value`                  | takes a `datetime.time`                                                                                                    |

## Covers, valves and climate

| Platform  | Required                                                              | Notes                                                                                                                                                               |
| --------- | --------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `cover`   | `is_closed`, `supported_features`                                     | implement `async_open_cover` / `async_close_cover` **only** with the matching `CoverEntityFeature`; use `Number` for something that is not an opening               |
| `valve`   | `reports_position`                                                    | `current_valve_position` is required when it is `True`; with position support implement `set_valve_position` and leave open/close out                               |
| `climate` | `hvac_mode`, `hvac_modes`, `target_temperature`, `supported_features` | always set `_attr_temperature_unit`; only built-in HVAC modes — device-specific variations become presets; omit `hvac_action` entirely when it cannot be determined |
| `fan`     | `is_on`, `percentage`, `async_set_percentage`, `supported_features`   | `preset_modes` must not contain speeds; `speed_count` defaults to 100; `async_turn_on`/`off` need the explicit `FanEntityFeature.TURN_ON`/`TURN_OFF` flags          |
| `lock`    | `is_locked`, `async_lock`, `async_unlock`                             | `is_open` is only relevant with `LockEntityFeature.OPEN`                                                                                                            |

## Stateless and media-ish

| Platform | Required                              | Notes                                                                                                                                                                                                                                                          |
| -------- | ------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `event`  | `event_types`                         | drive state with `self._trigger_event(type, data)` + `async_write_ha_state()` from a callback registered in `async_added_to_hass`; firing an undeclared type raises `ValueError`. Doorbells must use `DoorbellEventType.RING`; buttons use `ButtonEventType.*` |
| `update` | `installed_version`, `latest_version` | `UpdateEntityFeature.INSTALL` only if it really installs; `PROGRESS` + `update_percentage`, `RELEASE_NOTES` + `async_release_notes()`, `BACKUP`, `SPECIFIC_VERSION`; `version_is_newer()` for non-semver schemes                                               |
| `image`  | `async_image`                         | never bump `image_last_updated` inside `async_image` — set it from the coordinator; cache in `self._cached_image` and set it to `None` to invalidate                                                                                                           |
| `notify` | `async_send_message`                  | stateless; the state is the timestamp of the last message. Only record notifications originating **inside** Home Assistant via `_async_record_notification()` — externally generated ones belong on an event entity                                            |
| `todo`   | `todo_items`                          | state is the count of incomplete items; note `SET_DUE_DATE_ON_ITEM` vs `SET_DUE_DATETIME_ON_ITEM`                                                                                                                                                              |

## Light

`supported_color_modes` is required — **a light that does not set it raises when its state is written.** `color_mode`
must be one of the declared modes. `async_turn_on` receives exactly one colour attribute, already translated into the
mode you declared. An active effect may narrow `color_mode` to `ONOFF` or `BRIGHTNESS`.
