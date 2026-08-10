---
applyTo: "custom_components/**/alarm_control_panel/**/*.py, custom_components/**/binary_sensor/**/*.py, custom_components/**/button/**/*.py, custom_components/**/camera/**/*.py, custom_components/**/climate/**/*.py, custom_components/**/cover/**/*.py, custom_components/**/fan/**/*.py, custom_components/**/humidifier/**/*.py, custom_components/**/light/**/*.py, custom_components/**/lock/**/*.py, custom_components/**/number/**/*.py, custom_components/**/select/**/*.py, custom_components/**/sensor/**/*.py, custom_components/**/siren/**/*.py, custom_components/**/switch/**/*.py, custom_components/**/vacuum/**/*.py, custom_components/**/water_heater/**/*.py, custom_components/**/entity/**/*.py, custom_components/**/entity_utils/**/*.py"
globs: "custom_components/**/alarm_control_panel/**/*.py, custom_components/**/binary_sensor/**/*.py, custom_components/**/button/**/*.py, custom_components/**/camera/**/*.py, custom_components/**/climate/**/*.py, custom_components/**/cover/**/*.py, custom_components/**/fan/**/*.py, custom_components/**/humidifier/**/*.py, custom_components/**/light/**/*.py, custom_components/**/lock/**/*.py, custom_components/**/number/**/*.py, custom_components/**/select/**/*.py, custom_components/**/sensor/**/*.py, custom_components/**/siren/**/*.py, custom_components/**/switch/**/*.py, custom_components/**/vacuum/**/*.py, custom_components/**/water_heater/**/*.py, custom_components/**/entity/**/*.py, custom_components/**/entity_utils/**/*.py"
---

# Entity Platform Instructions

**Applies to:** All entity platform implementations (sensor, binary_sensor, switch, etc.), entity base classes, and entity utilities

## Shared Infrastructure

- **`entity/`** - Base entity classes (inherit the integration's base entity class from `entity/base.py`)
- **`entity_utils/`** - Shared utilities (device info, state helpers) used by 3+ entity classes
- **`coordinator/`** - Data fetching (entities never call API directly)

## Base Entity Inheritance

**MUST inherit from:** `(PlatformEntity, {ClassPrefix}Entity)` — the integration's base entity class from `..entity`, order matters for MRO

**Base class provides:** Coordinator integration, device info, unique ID (`{entry_id}_{description.key}`), attribution, entity naming

**You implement:** Platform-specific properties/methods (`native_value`, `is_on`, `async_press`, etc.)

**Imports pattern:** `from homeassistant.components.PLATFORM import PlatformEntity, PlatformEntityDescription` + `from ..entity import {ClassPrefix}Entity`

**Constructor:** Call `super().__init__(coordinator, entity_description)` - base handles setup

## Entity Descriptions

**Define at module level:** `ENTITY_DESCRIPTIONS: tuple[PlatformEntityDescription, ...]`

**Required fields:**

- `key` - Used in unique_id, must match coordinator data key. Never rename it after release.
- `translation_key` - Entity name comes from `translations/en.json`. **NEVER set `name=`** — the base entity sets
  `_attr_has_entity_name = True`, and a hardcoded name breaks localisation (quality scale `entity-translations`).
- Platform-specific: `device_class`, `state_class`, `native_unit_of_measurement`, `options`, etc.
- **Set `device_class` whenever one fits** - drives unit conversion, icons and voice assistants.
- **Set `state_class` on every numeric measurement** - without it there are no long-term statistics.
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

**Handle missing data:** Override `available` property to check `self.entity_description.key in self.coordinator.data`

## File Organization

**Group related entities:** `primary_entities.py`, `diagnostic.py`, `configuration.py`

**Split when:** Complex entity >100 lines → one file per entity class

## Custom State Attributes

**Use `extra_state_attributes` property** returning dict for supplemental data

**NEVER override `state_attributes`** - reserved for base platform components (brightness, color, etc.)

## Disabled By Default

**Set property:** `entity_registry_enabled_default = False` for advanced/diagnostic entities

**Config-controlled visibility:** Conditionally add/remove entities in setup, NOT via `disabled_by`

## Platform-Required Methods

| Platform        | Required members                                                      | Notes                                                          |
| --------------- | --------------------------------------------------------------------- | -------------------------------------------------------------- |
| `sensor`        | `native_value`                                                        | `state_class` for statistics; `device_class` drives conversion |
| `binary_sensor` | `is_on`                                                               | `BinarySensorDeviceClass` instead of icons                     |
| `switch`        | `is_on`, `async_turn_on`, `async_turn_off`                            | refresh after write                                            |
| `button`        | `async_press`                                                         | stateless; no `is_on`                                          |
| `number`        | `native_value`, `async_set_native_value`, min/max/step                | `NumberDeviceClass`, `mode`                                    |
| `select`        | `current_option`, `options`, `async_select_option`                    | options are translated via `state` keys                        |
| `fan`           | `is_on`, `percentage`, `async_set_percentage`, `supported_features`   | declare `FanEntityFeature` accurately                          |
| `climate`       | `hvac_mode`, `hvac_modes`, `target_temperature`, `supported_features` | always set `_attr_temperature_unit`                            |
| `cover`         | `is_closed`, `async_open_cover`, `async_close_cover`                  | `current_cover_position` when known                            |
| `update`        | `installed_version`, `latest_version`                                 | `UpdateEntityFeature.INSTALL` only if it really installs       |

**Write operations:** call the API client through `entry.runtime_data`, then `await coordinator.async_request_refresh()`.
Never mutate local state and assume it took. Wrap failures in `HomeAssistantError` with a `translation_key`.

**Event subscriptions:** subscribe in `async_added_to_hass()` and release every subscription via `self.async_on_remove(...)`
(quality scale `entity-event-setup`).

**Reference:** [Entity Developer Docs](https://developers.home-assistant.io/docs/core/entity)

## Entity Utilities

**Add to `entity_utils/` when:**

- Used by 3+ entity classes
- Complex logic benefiting from testing
- Device info customization, state formatting

**Import pattern:** `from ..entity_utils.module import function`

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

- Use the deprecated unscoped `async_get_device()` lookup.
- Use `via_device`, because identifiers are not globally unique across config entries.
- Add this integration's config entry to a device owned by another integration. Helper entities link to the source
  device by assigning `self.device_entry` instead of copying its identifiers or connections into `DeviceInfo`.
- Depend on a device being shared or merged across config entries.

## Type Hints

**Avoid circular imports:** Use `TYPE_CHECKING` block for coordinator imports

```python
from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..coordinator import {ClassPrefix}DataUpdateCoordinator
```

## PARALLEL_UPDATES

Home Assistant reads `PARALLEL_UPDATES` from the platform module, so every platform `__init__.py` must re-export it
with the redundant-looking alias — without it Ruff flags the import as unused:

```python
from custom_components.<domain>.const import PARALLEL_UPDATES as PARALLEL_UPDATES
```

The value is defined once in `const.py`. Missing it on a platform is a quality scale failure (`parallel-updates`).

## Dynamic Entity Creation

**Filter by available data:** Check `desc.key in coordinator.data` before creating entities

**Conditional features:** Use `self.coordinator.data.get("capability")` to determine `supported_features`

## Common Pitfalls

**❌ Don't:**

- Call API directly from entities
- Create entities without EntityDescription
- Override base class methods unnecessarily
- Hardcode unique IDs
- Log in property getters (called frequently)
- Duplicate constants (use `homeassistant.const` or integration `const.py`)

**✅ Do:**

- Use coordinator data exclusively
- Define EntityDescriptions with all metadata
- Generate unique IDs from `entry_id + description.key`
- Log only in async methods or `__init__`
- Consult HA docs for platform-specific patterns
- Use `entity_utils/` for shared logic
