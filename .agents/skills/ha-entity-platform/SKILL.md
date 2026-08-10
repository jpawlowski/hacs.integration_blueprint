---
name: ha-entity-platform
description: >-
  Add or change a Home Assistant entity platform or an individual entity in this custom integration — sensor,
  binary_sensor, switch, button, number, select, fan, climate, cover, light, lock, and friends. Use when asked to
  "add a sensor", "add a new entity", "add a platform", "expose <value> as an entity", "add an entity to the
  device", "make this entity diagnostic", or when changing EntityDescription metadata, device classes, state
  classes, entity categories, or availability. Covers the platform directory layout, the coordinator-backed entity
  contract, unique IDs, device grouping, and the translation and validation steps that must follow. SYMPTOMS —
  load this if you are about to: hardcode `name=` or `icon=` in an EntityDescription instead of `translation_key`;
  omit `state_class` on a numeric measurement; call the API client from an entity property; set `_attr_unique_id`
  or `_attr_device_info` in a platform entity; or put two entity classes in one file.
---

# Add or change an entity platform

Entities are the user-visible surface of the integration. Getting the metadata right at creation time matters more than
usual: unique IDs, device classes, and entity IDs are effectively permanent once a user has installed the integration.

**Read [`blueprint.entities.instructions.md`](../../instructions/blueprint.entities.instructions.md) first** —
it holds the rules this procedure assumes: base-class inheritance and MRO, required `EntityDescription` fields, the
coordinator-only data rule, the per-platform member table, `PARALLEL_UPDATES`, and device registry ownership. Copilot
injects it automatically when you edit an entity file; other agents must open it. Python style is in
[`blueprint.python.instructions.md`](../../instructions/blueprint.python.instructions.md).

This skill is the procedure and the decisions — it does not restate those rules.

## Before you write code

Clarify — ask the developer if any of this is missing:

- Which platform (`sensor`, `switch`, …) and whether it already exists in the integration.
- Which field of `coordinator.data` backs the entity, and its unit and value range.
- Whether it is a primary entity or a diagnostic/config entity (`EntityCategory`).
- For writable platforms: which API method performs the write.

Then read the closest existing sibling — for a new sensor that is
`custom_components/<domain>/sensor/air_quality.py`. Match it rather than inventing a second style.

## Layout

Each platform is a package, one entity class per file:

```text
custom_components/<domain>/<platform>/
├── __init__.py        # async_setup_entry + aggregated ENTITY_DESCRIPTIONS
└── <group>.py         # ENTITY_DESCRIPTIONS + entity class for one logical group
```

## Procedure

### 1. Decide the metadata, then write the descriptions

The mechanical rules are in the instructions file. What this step actually costs you is judgement:

- **`key`** becomes part of the unique ID. Pick it once — renaming it later is a breaking change
  ([`ha-breaking-changes`](../ha-breaking-changes/SKILL.md)).
- **Primary, diagnostic or config?** Anything a user would not put on a dashboard is
  `EntityCategory.DIAGNOSTIC`, and if it is also noisy, `entity_registry_enabled_default=False`.
- **Is there a matching `device_class`?** Check the platform's enum before inventing units or icons. A device class
  buys unit conversion, correct icons and voice-assistant behaviour for free.
- **Is the value a measurement?** Then it needs a `state_class`, or the user gets no history.

### 2. Entity class

Implement only the platform members and the value extraction; everything else comes from the base class.

```python
class {ClassPrefix}AirQualitySensor(SensorEntity, {ClassPrefix}Entity):
    """Air quality sensor."""

    entity_description: {ClassPrefix}SensorEntityDescription

    @property
    def native_value(self) -> StateType:
        """Return the current value."""
        return self.entity_description.value_fn(self.coordinator.data)
```

Only override `available` when a single entity can be unavailable while the rest of the device is fine — the base
`CoordinatorEntity` already handles the whole-device case:

```python
@property
def available(self) -> bool:
    """Return True if the backing value is present."""
    return super().available and self.entity_description.key in self.coordinator.data
```

### 3. Register the platform

For a brand-new platform only:

1. Add the `Platform.<NAME>` member to the `PLATFORMS` list in `custom_components/<domain>/__init__.py`
   (keep the list alphabetical).
2. Nothing else — `async_setup_entry` already forwards with `async_forward_entry_setups(entry, PLATFORMS)` and
   `async_unload_entry` already tears down with `async_unload_platforms(entry, PLATFORMS)`.

### 4. Device grouping

The base entity places every entity on the config entry's device. Only deviate when the integration genuinely models
multiple physical devices, and then follow the single-owner registry rules in
[`ha-modern-apis`](../ha-modern-apis/SKILL.md) — one device belongs to exactly one config entry and at most one
subentry, and parent/child relationships use `via_device_id`.

### 5. Translations

Add the `translation_key` under `entity.<platform>.<key>.name` in `translations/en.json`, plus `state` keys for enum
sensors. Do not touch other language files. See [`ha-translations`](../ha-translations/SKILL.md).

### 6. Validate

```bash
script/lint && script/type-check
script/hassfest
script/test
```

Then restart Home Assistant (`./script/develop`) and confirm the entity appears with the expected name, unit, icon, and
category. If it does not appear at all, switch to [`ha-coordinator-debug`](../ha-coordinator-debug/SKILL.md).

## Do not

- Do not add an entity for data the coordinator does not already fetch — extend the coordinator first, or you will be
  tempted to call the API from the entity.
- Do not rename an existing `key`, `translation_key`, or unique ID without reading
  [`ha-breaking-changes`](../ha-breaking-changes/SKILL.md).
- Do not skip the sibling-file read in step 0. Most "new" entities are a variation of one that already exists.

The per-platform member table and the remaining hard rules are in
[`blueprint.entities.instructions.md`](../../instructions/blueprint.entities.instructions.md).
