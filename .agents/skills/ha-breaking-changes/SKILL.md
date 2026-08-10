---
name: ha-breaking-changes
description: >-
  Handle any change to this Home Assistant custom integration that could break existing installations — unique IDs
  and entity IDs, config entry data, config options, service actions, state values, units, device classes, the
  minimum Home Assistant version, or removing entities and devices. Use when asked to "rename", "restructure",
  "clean up the unique IDs", "remove this option", "change the state format", or whenever a planned change would
  invalidate an existing install. Covers the warn-first policy, unique ID and config entry migration, repair
  issues, deprecation periods, how the bar differs before 1.0.0, and documenting the change. SYMPTOMS — load this
  if you are about to: rename an `EntityDescription.key`, unique ID, or entity ID; remove a config option because
  it looks unused; change a unit, device class, or state class; treat a prior approval as standing permission;
  write a migration or bump `VERSION` before 1.0.0; or fold a breaking change into an unrelated commit.
---

# Breaking changes

Users have automations, dashboards, scripts, and long-term statistics wired to this integration's entity IDs, unique
IDs, states, and action names. Breaking any of them is a real cost to real people, and the integration cannot see who
it broke.

## Which side of 1.0.0 is this?

Everything below assumes a released, stable integration. **Before `1.0.0` the trade-off is genuinely different, and
applying the post-1.0 rules early is its own kind of damage**: compatibility code accumulates in a codebase whose
shape is not settled yet, which is exactly what makes reaching a stable 1.0.0 harder.

Before 1.0.0:

- **A breaking change is an acceptable outcome, and usually the right one.** Getting the shape right beats preserving
  a shape you already regret.
- **What still needs asking is whether to build the migration** — not whether to break. Do not write
  `async_migrate_entry`, rewrite registry entries, or bump `VERSION` / `MINOR_VERSION` on your own initiative. Put
  the choice to the developer: break cleanly now, or carry the migration.
- **Recommend.** "The cleanest fix is to rename the key and let existing test entries be recreated; a migration would
  cost ~40 lines we would then maintain" is the useful form. Not "shall I migrate?"
- **Do not record each one in `DECISIONS.md`.** That log is for architecture. A key renamed before the first stable
  release is not an architectural decision, and a log padded with them is one nobody reads.
- **Keep the `BREAKING CHANGE:` footer anyway.** It costs one line, and it is the whole price of this freedom: HACS
  installs `0.x` versions too, and the people testing early deserve a changelog entry rather than a silent surprise.
  Release-please turns it into a minor bump pre-1.0 ([`ha-release`](../ha-release/SKILL.md)), so it is cheap.

This is also the window in which unique IDs stop being free. `{entry_id}_{key}` is the documented last resort — if the
device exposes a serial or MAC, switch to it **before** 1.0.0, because afterwards it is a migration
([`blueprint.entities`](../../instructions/blueprint.entities.instructions.md)).

After 1.0.0, everything below applies as written.

## 1. Recognise it

Treat as breaking:

- Changing entity IDs, unique IDs, or `EntityDescription.key`.
- Changing the structure of `entry.data` or `entry.options`.
- Changing a state value, its unit, `device_class`, `state_class`, or an attribute name/format.
- Renaming, removing, or changing the signature of a service action.
- Removing or renaming a config option — including one you believe is unused.
- Raising the minimum Home Assistant version in `hacs.json` / `manifest.json`.
- Removing an entity, a platform, or a device.

Long-term statistics deserve special care: changing `state_class`, the unit, or the entity ID discards or corrupts
history that cannot be recovered. One case is recoverable — when only the **spelling** of a unit changes (`"KWh"` to
`UnitOfEnergy.KILO_WATT_HOUR`), declare the pair equivalent with `recorder.async_custom_equivalent_units` instead of
letting the statistics break.

`supported_features`, `device_class` and capability attributes are changeable at runtime, but every change forces
voice-assistant integrations to resynchronise with their cloud service — treat a change at poll rate as a bug.

## 2. Warn before you implement

Never make a breaking change silently, and never as an incidental part of a larger task. State it plainly and stop:

> ⚠️ This change alters the unique ID format from `{entry_id}_{key}` to `{serial}_{key}`. Every existing entity would be
> recreated with a new entity ID, so users' automations and dashboards would break and history would be split. I can
> either (a) implement a migration that renames the existing registry entries, or (b) leave the format as it is.
> How would you like to proceed?

Wait for an explicit answer. A prior approval for one breaking change is not approval for the next.

Never do without explicit approval: removing config options, changing action parameters, changing how entry data is
stored, renaming entities or changing device classes, or changing unique ID generation.

## 3. Prefer a migration over a break — after 1.0.0

Before 1.0.0 this section is an option to offer, not the default to reach for; see the threshold above.

### Unique ID migration

Rewrite existing registry entries during setup, before the platforms load:

```python
async def _async_migrate_unique_ids(hass: HomeAssistant, entry: {ClassPrefix}ConfigEntry) -> None:
    """Migrate entity unique IDs from the legacy format."""
    registry = er.async_get(hass)
    for entity in er.async_entries_for_config_entry(registry, entry.entry_id):
        if not entity.unique_id.startswith(f"{entry.entry_id}_"):
            continue
        new_unique_id = entity.unique_id.replace(entry.entry_id, serial_number, 1)
        if registry.async_get_entity_id(entity.domain, DOMAIN, new_unique_id):
            # A collision means the new entity already exists — drop the stale one.
            registry.async_remove(entity.entity_id)
            continue
        registry.async_update_entity(entity.entity_id, new_unique_id=new_unique_id)
```

The entity ID follows the registry entry, so the user's automations keep working. Migrations must be idempotent and
must handle the case where they already ran.

### Config entry migration

Bump `MINOR_VERSION` for additive changes and `VERSION` for restructuring, then implement `async_migrate_entry()` — see
[`ha-config-flow`](../ha-config-flow/SKILL.md). Return `False` for a downgrade rather than corrupting data.

### Deprecation period instead of removal

When you cannot migrate automatically, keep the old thing working and tell the user:

```python
async_create_issue(
    hass,
    DOMAIN,
    "deprecated_option_scan_interval",
    is_fixable=True,
    severity=IssueSeverity.WARNING,
    translation_key="deprecated_option_scan_interval",
)
```

- `is_fixable=True` requires a `RepairsFlow` in `repairs.py` that performs the fix.
- Delete the issue with `async_delete_issue()` as soon as the condition no longer holds — a stale repair notification
  trains users to ignore them.
- Keep the deprecated path working for at least one release cycle before removing it.
- Add the `issues.<issue_id>.title` / `.description` strings ([`ha-translations`](../ha-translations/SKILL.md)).

## 4. Implement

1. Migration or deprecation code first, the new behaviour second.
2. Test the migration explicitly: an entry created with the old shape must end up correct after setup, and running the
   migration twice must be a no-op ([`ha-testing`](../ha-testing/SKILL.md)).
3. Verify by hand: start Home Assistant with an existing `config/.storage`, load the entry, and confirm entity IDs and
   history survived.

## 5. Document it

- Commit message: a `!` after the type/scope **and** a `BREAKING CHANGE:` footer explaining what breaks and what the
  user must do. This is what drives the version bump and the changelog
  ([`ha-release`](../ha-release/SKILL.md)).

  ```text
  feat(sensor)!: derive unique IDs from the device serial number

  BREAKING CHANGE: Entity unique IDs now use the device serial number instead of the
  config entry ID. Existing entities are migrated automatically on upgrade. Users who
  removed and re-added the integration between 0.4.0 and 0.5.0 must check their
  automations for renamed entities.
  ```

- Update `docs/user/` and the README where the old behaviour is described.
- Record the reasoning in `docs/development/DECISIONS.md` if it was an architectural call
  ([`ha-planning`](../ha-planning/SKILL.md)).

## 6. Removing entities and devices

Removing an entity does not remove its registry entry, and **the entity registry writes an `unavailable` state for
every registered entity that no longer has an entity object behind it** — so the entity lingers in the UI forever.
Clean up explicitly:

The registry cascades downward: config entry → device → entity. Removing a device removes its entities with it, which
is why `stale-devices` needs no per-entity cleanup.

- Entities: `er.async_get(hass).async_remove(entity_id)` during setup for the IDs you know are gone.
- Devices: remove devices that no longer exist upstream (`stale-devices`, Gold), scoped to the owning config entry —
  see [`ha-modern-apis`](../ha-modern-apis/SKILL.md).
- Implement `async_remove_config_entry_device()` so users can delete a stale device from the UI themselves. It
  returns `True` when the device's identifier is no longer in the coordinator's data.

Entity names and entity IDs are generated from the **backend language at the moment the entity is created**, not the
user's current UI language. Fixing wording in `en.json` therefore does not rename anyone's existing entities, and an
entity ID created under another backend language cannot be assumed to match the English one.

## Do not

- Do not rename something because the new name is nicer.
- Do not remove a config option because it looks unused — someone's YAML-restored entry may still carry it.
- Do not batch a breaking change into an unrelated commit.
- Do not describe a change as non-breaking because the code still runs; the test is whether a user's existing setup
  still behaves the same.
