# Climate and appliances

Only what differs per platform — read your platform's row; the general rules are in
[`blueprint.entities`](../../../instructions/blueprint.entities.instructions.md).

| Platform       | Required                                                                        | Notes                                                                                                                                                                                             |
| -------------- | ------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `climate`      | `hvac_mode`, `hvac_modes`, `temperature_unit`, `supported_features`             | always set `_attr_temperature_unit`; only built-in HVAC modes — device-specific variations become presets; omit `hvac_action` entirely when it cannot be determined. Temperature names: see below |
| `water_heater` | `current_operation`, `operation_list`, `temperature_unit`, `supported_features` | same temperature renaming as `climate`, below; `min_temp` / `max_temp` are in the device's unit                                                                                                   |
| `humidifier`   | `is_on`, `target_humidity`, `async_turn_on`/`off`, `async_set_humidity`         | `device_class` is `HUMIDIFIER` or `DEHUMIDIFIER`; `action` (`HumidifierAction`) only when the device reports it; `mode` / `available_modes` need `HumidifierEntityFeature.MODES`                  |
| `vacuum`       | `activity`, `supported_features`                                                | subclass `StateVacuumEntity` and return `VacuumActivity`, never a string. Expose the battery level as a separate `sensor` with `SensorDeviceClass.BATTERY` (see deprecations.md)                  |
| `lawn_mower`   | `activity`, `supported_features`                                                | return `LawnMowerActivity`; implement `async_start_mowing` / `async_pause` / `async_dock` only with the matching `LawnMowerEntityFeature`                                                         |
| `media_player` | `state`, `supported_features`                                                   | return `MediaPlayerState`. Never `STANDBY` (see deprecations.md): a player HA can still wake is `OFF`, one it cannot reach is unavailable. Every command needs its `MediaPlayerEntityFeature`     |

## Climate and water heater temperatures

Code uses `current_temperature`, `target_temperature`, `target_temperature_high`, `target_temperature_low` and
`temperature_unit` (with their `_attr_` forms), in the device's unit — the base class converts to the user's unit
system.

(HA 2026.11+) Both platforms rename these five with a `native_` prefix
([`deprecations.md`](../../ha-modern-apis/references/deprecations.md)). **Keep the old names while the minimum
supported Home Assistant version is below 2026.11** — the new ones do nothing there; switch in the change that raises
it ([`ha-modern-apis`](../../ha-modern-apis/SKILL.md)). `min_temp`, `max_temp` and `target_temperature_step` are not
renamed.
