---
name: "Entity Platforms"
description: "Entity descriptions, translation keys, device registry ownership, and platform members"
applyTo: "custom_components/**/alarm_control_panel/**/*.py, custom_components/**/binary_sensor/**/*.py, custom_components/**/button/**/*.py, custom_components/**/camera/**/*.py, custom_components/**/climate/**/*.py, custom_components/**/cover/**/*.py, custom_components/**/device_tracker/**/*.py, custom_components/**/event/**/*.py, custom_components/**/fan/**/*.py, custom_components/**/humidifier/**/*.py, custom_components/**/image/**/*.py, custom_components/**/light/**/*.py, custom_components/**/lock/**/*.py, custom_components/**/notify/**/*.py, custom_components/**/number/**/*.py, custom_components/**/select/**/*.py, custom_components/**/sensor/**/*.py, custom_components/**/siren/**/*.py, custom_components/**/switch/**/*.py, custom_components/**/text/**/*.py, custom_components/**/time/**/*.py, custom_components/**/todo/**/*.py, custom_components/**/update/**/*.py, custom_components/**/vacuum/**/*.py, custom_components/**/valve/**/*.py, custom_components/**/water_heater/**/*.py, custom_components/**/entity/**/*.py, custom_components/**/entity_utils/**/*.py"
paths:
  - "custom_components/**/alarm_control_panel/**/*.py"
  - "custom_components/**/binary_sensor/**/*.py"
  - "custom_components/**/button/**/*.py"
  - "custom_components/**/camera/**/*.py"
  - "custom_components/**/climate/**/*.py"
  - "custom_components/**/cover/**/*.py"
  - "custom_components/**/device_tracker/**/*.py"
  - "custom_components/**/event/**/*.py"
  - "custom_components/**/fan/**/*.py"
  - "custom_components/**/humidifier/**/*.py"
  - "custom_components/**/image/**/*.py"
  - "custom_components/**/light/**/*.py"
  - "custom_components/**/lock/**/*.py"
  - "custom_components/**/notify/**/*.py"
  - "custom_components/**/number/**/*.py"
  - "custom_components/**/select/**/*.py"
  - "custom_components/**/sensor/**/*.py"
  - "custom_components/**/siren/**/*.py"
  - "custom_components/**/switch/**/*.py"
  - "custom_components/**/text/**/*.py"
  - "custom_components/**/time/**/*.py"
  - "custom_components/**/todo/**/*.py"
  - "custom_components/**/update/**/*.py"
  - "custom_components/**/vacuum/**/*.py"
  - "custom_components/**/valve/**/*.py"
  - "custom_components/**/water_heater/**/*.py"
  - "custom_components/**/entity/**/*.py"
  - "custom_components/**/entity_utils/**/*.py"
---

# Entity Platform Instructions

**Procedure:** [`ha-entity-platform`](../skills/ha-entity-platform/SKILL.md) — load it before adding a platform or an
entity. This file is the rule set; the skill is the order the layers get built in and the decisions that rule set
assumes have already been made.

**Applies to:** All entity platform implementations (sensor, binary_sensor, switch, etc.), entity base classes, and entity utilities

## Shared Infrastructure

- **`entity/`** - Base entity classes (inherit the integration's base entity class from `entity/base.py`)
- **`entity_utils/`** - Shared utilities (device info, state helpers) used by 3+ entity classes
- **`coordinator/`** - Data fetching (entities never call API directly)

## Base Entity Inheritance

**MUST inherit from:** `(PlatformEntity, {ClassPrefix}Entity)` — the integration's base entity class from `..entity`, order matters for MRO

**Base class provides:** Coordinator integration, device info, unique ID (`{entry_id}_{description.key}`), attribution, entity naming

`{entry_id}_{key}` is the documented **unique ID of last resort**. If the device or account exposes a serial, MAC or
account ID, switch to it **before the first release** — afterwards it is a breaking change needing a registry
migration ([`ha-breaking-changes`](../skills/ha-breaking-changes/SKILL.md)).

**You implement:** Platform-specific properties/methods (`native_value`, `is_on`, `async_press`, etc.)

**Imports pattern:** `from homeassistant.components.PLATFORM import PlatformEntity, PlatformEntityDescription` + `from custom_components.<domain>.entity import {ClassPrefix}Entity` — absolute, because Ruff rejects a relative import that reaches into a parent package (`blueprint.python`)

**Constructor:** Call `super().__init__(coordinator, entity_description)` - base handles setup

## Entity Descriptions

**Define at module level:** `ENTITY_DESCRIPTIONS: tuple[PlatformEntityDescription, ...]`

**Required fields:**

- `key` - Used in unique_id, must match coordinator data key. Never rename it after release.
- `translation_key` - Entity name comes from `translations/en.json`. **NEVER set `name=` to a string** — the base
  entity sets `_attr_has_entity_name = True`, and a hardcoded name breaks localisation (quality scale
  `entity-translations`). Two exceptions:
  - On `binary_sensor`, `number`, `sensor` and `update`, an entity whose `device_class` already produces the wanted
    name needs **no** `translation_key` — a `SensorDeviceClass.TEMPERATURE` sensor is named "Temperature" by itself.
    Adding one only creates a redundant key for translators.
  - The entity that **is** the device's main feature (the light of a bulb, the fan of a purifier) sets `name=None`
    on its description, or `_attr_name = None` on the class. `friendly_name` then becomes the device name alone and
    the entity id is `<platform>.<device_name>` — without it the UI reads "Air Purifier Air Purifier".
- Platform-specific: `device_class`, `state_class`, `native_unit_of_measurement`, `options`, etc.
- **Set `device_class` whenever one fits** - drives unit conversion, icons and voice assistants.
- **Set `state_class` on every numeric measurement** - without it there are no long-term statistics. But
  `MEASUREMENT` is **invalid** with a `device_class` of `ENERGY`, `GAS`, `WATER`, `VOLUME`, `MONETARY`, `DATE`,
  `TIMESTAMP` or `ENUM` — meters take `TOTAL` or `TOTAL_INCREASING`. See
  [`platform-members.md`](../skills/ha-entity-platform/references/platform-members.md).
- **NEVER set `icon=`** - icons belong in `icons.json` (quality scale `icon-translations`).

**Value extraction:** Subclass the description dataclass with a `value_fn` rather than branching on `key` in the entity:

```python
@dataclass(frozen=True, kw_only=True)
class {ClassPrefix}SensorEntityDescription(SensorEntityDescription):
    """Describes a sensor and how to read it from coordinator data."""

    value_fn: Callable[[dict[str, Any]], StateType]
```

**Entity Categories:**

- `None` - Primary functionality (prominent display)
- `EntityCategory.DIAGNOSTIC` - Diagnostic info (uptime, signal, errors)
- `EntityCategory.CONFIG` - Configuration settings

## Platform Setup

**Pattern:** `async_setup_entry()` creates entities from descriptions

- Import entity classes + DESCRIPTIONS from submodules
- Generator: `async_add_entities(EntityClass(entry.runtime_data.coordinator, desc) for desc in DESCRIPTIONS)`
- Combine multiple entity types in one platform
- Access coordinator: `entry.runtime_data.coordinator`

## Coordinator Data Access

**MUST use coordinator only:** `self.coordinator.data.get(self.entity_description.key)`

**NEVER call API directly:** No `self.coordinator.client` or `await api_call()` in entities

**Missing data is `unknown`, not `unavailable`.** The two are not interchangeable: `unavailable` hides the entity and
breaks templates that read its state, so it is only correct when the thing behind the entity is genuinely gone.

- The poll succeeded but one field is absent → return `None` from `native_value` / `is_on`. The state becomes
  `unknown` and the entity stays usable.
- The whole device or channel is gone → override `available`. Only do this when a missing key really means a missing
  sub-device; the base `CoordinatorEntity` already covers the whole-device case.

## File Organization

**Group related entities:** `primary_entities.py`, `diagnostic.py`, `configuration.py`

**Split when:** Complex entity >100 lines → one file per entity class

## Custom State Attributes

**Prefer a second entity.** Every attribute is written to the recorder database on every state change, so a frequently
changing attribute on a frequently changing entity multiplies database growth. A value worth showing is usually worth
its own sensor.

**If attributes are still right:** use the `extra_state_attributes` property returning a dict, and exclude the volatile
ones from history with a **class-level** `_unrecorded_attributes: frozenset[str]` (instance attributes are ignored).
`MATCH_ALL` excludes everything except `device_class`, `state_class`, `unit_of_measurement` and `friendly_name`.

**NEVER override `state_attributes` or `capability_attributes`** - reserved for base platform components (brightness,
color, etc.)

## Disabled and Hidden By Default

Two different things, and the wrong one is a common mistake:

- **Disabled** — not created at all, no state, unusable in automations. `_attr_entity_registry_enabled_default = False`
  on the class, or `entity_registry_enabled_default=False` on the description. Note the `_attr_` prefix on the class
  form: writing the bare property name silently does nothing.
- **Hidden** — created and recorded, usable in automations, just kept off auto-generated dashboards.
  `_attr_entity_registry_visible_default = False`. Usually what a noisy-but-useful diagnostic actually wants.

**Config-controlled visibility:** Conditionally add/remove entities in setup, NOT via `disabled_by`. When an option
turns a group off, also remove the stale registry entries (`er.async_remove(entity_id)`, and the device once it has no
entities left) — merely not creating them leaves entities the registry reports as `unavailable` forever.

## Device Info Fields

The base entity supplies `identifiers`, `name`, `manufacturer` and `model`. Fill in whatever else the source actually
knows — the Gold `devices` rule wants a complete device, and a `DeviceInfo` must match one of the registry's shapes
(Link: `connections` + `identifiers` only; Primary: the full metadata set; Secondary), never a partial mix.

| Field                                | Source                                                              |
| ------------------------------------ | ------------------------------------------------------------------- |
| `serial_number`                      | The device serial, when the API exposes one                         |
| `sw_version`, `hw_version`           | Firmware and hardware revision                                      |
| `model_id`                           | The machine-readable model code, next to the human-readable `model` |
| `configuration_url`                  | The device's own web UI; `homeassistant://<path>` to link inside HA |
| `entry_type=DeviceEntryType.SERVICE` | For a cloud account or service, which is not a physical device      |

Device info is only read when the entity is set up from a **config entry** and has a `unique_id`. No unique ID means
`device_info` and every registry property are silently ignored.

## Platform-Required Methods

Per-platform members and the trap each platform carries:
[`ha-entity-platform/references/platform-members.md`](../skills/ha-entity-platform/references/platform-members.md).
Read the row for the platform you are adding.

**Write operations:** call the API client through `entry.runtime_data`, then `await coordinator.async_request_refresh()`.
Never mutate local state and assume it took — unless the device cannot report its state back at all (one-way RF or IR),
in which case set `_attr_assumed_state = True` and write the optimistic state. The frontend then shows discrete on/off
buttons instead of a toggle.

Failures follow the same split as everywhere else: `ServiceValidationError` for a value the user got wrong,
`HomeAssistantError` for a device or communication failure, both with a `translation_key`, never `ValueError`.

**Event subscriptions:** subscribe in `async_added_to_hass()` and release every subscription via `self.async_on_remove(...)`
(quality scale `entity-event-setup`). Call `await super().async_added_to_hass()` first — the base class needs it, and
subscribing earlier breaks any callback that touches `self.hass` or writes state. Never register a reference to an
entity object outside `async_added_to_hass`: a disabled entity is never added, and the reference would dangle.

**Runtime-varying metadata:** derive `supported_features` from coordinator data **once, at construction**, not in a
property that re-reads it every poll. `supported_features`, `device_class` and capability attributes may change, but
each change forces voice-assistant integrations to resynchronise with their cloud service.

**Reference:** [Entity Developer Docs](https://developers.home-assistant.io/docs/core/entity)

## Entity Utilities

**Add to `entity_utils/` when:**

- Used by 3+ entity classes
- Complex logic benefiting from testing
- Device info customization, state formatting

**Import pattern:** `from custom_components.<domain>.entity_utils.module import function`

## Device Registry Ownership

Home Assistant Core 2026.8 and newer assigns every device to exactly one config entry and at most one config subentry.

**MUST:**

- Return `DeviceInfo` for a device owned by the entity's own config entry.
- Create a separate device for each config subentry; never share one device across subentries.
- Use `via_device_id` when linking a subentry device to a separate hub/account device.
- Use `self.device_entry` inside an entity when the registered device is needed.
- Scope explicit registry lookups with `async_get_device_by_identifier(identifier, config_entry_id)` or
  `async_get_device_by_connection(connection, config_entry_id)`.

**NEVER:**

- Use the unscoped `async_get_device()` lookup — it resolves ambiguously across entries.
- Use `via_device`, because identifiers are not globally unique across config entries. Passing **both** `via_device`
  and `via_device_id` raises at runtime, so a half-finished migration fails loudly — remove the old one.
- Add this integration's config entry to a device owned by another integration. Helper entities link to the source
  device by assigning `self.device_entry` instead of copying its identifiers or connections into `DeviceInfo`.
- Depend on a device being shared or merged across config entries.

## PARALLEL_UPDATES

Home Assistant reads `PARALLEL_UPDATES` from the platform module, so every platform `__init__.py` declares it as a
module-level literal — the same way Core integrations do. Do not import it from `const.py`: the value is a per-platform
decision, and a shared constant can only get it wrong for half the platforms.

```python
# Read-only platform: the coordinator already serializes the fetch.
PARALLEL_UPDATES = 0
```

**The value depends on whether the platform acts on the device**, because a coordinator only centralizes the inbound
fetch — it does not limit outbound calls:

| Value | Platforms                                                                                                                                                                        |
| ----- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `0`   | Read-only: `sensor`, `binary_sensor`, `event`, `image`, `device_tracker`. Throttling these only slows startup.                                                                   |
| `1`   | Everything that writes: `switch`, `light`, `number`, `select`, `button`, `climate`, `cover`, `fan`, `lock`, `valve`, `text`, `time`, `todo`, `update`, `notify`, `water_heater`. |

Missing it on a platform is a quality scale failure (`parallel-updates`).

## Dynamic Entity Creation

**Filter by available data:** Check `desc.key in coordinator.data` before creating entities

**Conditional features:** Use `self.coordinator.data.get("capability")` to determine `supported_features`

**Never log in a property getter** — they are called on every state read.
