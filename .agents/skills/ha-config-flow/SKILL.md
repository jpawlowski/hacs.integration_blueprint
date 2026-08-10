---
name: ha-config-flow
description: >-
  Work on the Home Assistant config flow of this custom integration — the setup UI, options flow,
  reauthentication, reconfigure, discovery (zeroconf, dhcp, ssdp, bluetooth, usb, mqtt, homekit), subentries,
  unique IDs, and config entry version migration. Use when asked to "add a config option", "add a setting", "ask
  the user for X during setup", "add an options flow", "support reauth", "add discovery", "make the host
  configurable", "migrate the config entry", or when editing config_flow_handler/, its schemas/ and validators/,
  or manifest discovery matchers. Covers reserved step names, acceptable unique IDs, abort reasons, validation,
  and the migration contract. SYMPTOMS — load this if you are about to: use a host or IP as the unique ID; create
  a config entry without validating the connection; store a credential in `entry.options`; read `entry.data[key]`
  for a key old entries will not have; or change entry data without bumping VERSION/MINOR_VERSION.
---

# Work on the config flow

The config flow is the only supported way to configure a device or service integration (ADR-0010). Everything the user
can change lives here, and mistakes here are expensive: `unique_id` and the shape of `entry.data` are effectively
permanent.

**Read [`blueprint.config_flow.instructions.md`](../../instructions/blueprint.config_flow.instructions.md)
first.** It is the authoritative rule set: data-vs-options, reserved step names, acceptable unique IDs and their
normalisation, the MUST/NEVER lists for user, discovery, reauth, reconfigure and subentry flows, title placeholders,
and the migration contract. Copilot injects it automatically when you edit a config flow file; other agents must open
it. This skill is the order of operations and the decisions.

## Package layout

```text
config_flow_handler/
├── __init__.py          # exports
├── config_flow.py       # user, reauth, reauth_confirm, reconfigure, discovery steps
├── options_flow.py      # post-setup options
├── subentry_flow.py     # multi-device / multi-account subentries
├── schemas/
│   ├── config.py        # voluptuous schemas for setup steps
│   └── options.py       # voluptuous schemas for the options flow
└── validators/
    ├── credentials.py   # "can we actually talk to it" checks
    └── sanitizers.py    # input normalisation (strip, lowercase host, …)
```

The top-level `config_flow.py` is a thin shim Home Assistant discovers — leave it alone.

## Adding a config option

1. **Decide data or options** using the table in the instructions file. This is the one irreversible choice here.
2. Add the `CONF_*` key to `const.py`.
3. Add the field to `schemas/config.py` or `schemas/options.py` with a selector and a default.
4. Consume it: coordinator reads `entry.options`, client reads `entry.data`.
5. Add the `data` and `data_description` translation keys ([`ha-translations`](../ha-translations/SKILL.md)).
6. **Handle existing entries** that predate the key — a default at read time, or a `MINOR_VERSION` bump plus migration.
   This is the step that gets forgotten and breaks upgrades.

## Adding discovery

1. Add the matcher to `manifest.json`:

   ```json
   "zeroconf": [{ "type": "_myservice._tcp.local.", "name": "blueprint*" }]
   ```

2. Implement the matching `async_step_<method>()` following the discovery MUST/NEVER list in the instructions.
3. Decide what the discovery payload gives you as a stable unique ID. If it offers nothing stable, stop and discuss it
   — do not fall back to the IP address.
4. Confirm the flow end-to-end in the UI: the card shows a useful name, a second discovery of the same device aborts,
   and a device that changed IP updates the existing entry rather than creating a second one.

## Config entry migration

Bump `MINOR_VERSION` for additive changes, `VERSION` for restructuring. Read
[`ha-breaking-changes`](../ha-breaking-changes/SKILL.md) first — changing entry data affects every existing install.

Implement `async_migrate_entry()` in `custom_components/<domain>/__init__.py`:

```python
async def async_migrate_entry(hass: HomeAssistant, entry: {ClassPrefix}ConfigEntry) -> bool:
    """Migrate an old config entry."""
    if entry.version > 1:
        # Downgrade from a future version — refuse rather than corrupt data.
        return False
    if entry.version == 1 and entry.minor_version < 2:
        data = {**entry.data, CONF_PORT: DEFAULT_PORT}
        hass.config_entries.async_update_entry(entry, data=data, minor_version=2)
    return True
```

Migrations must be idempotent and must never delete a key they do not understand. Cover every migration with a test
([`ha-testing`](../ha-testing/SKILL.md)).

## Validate

```bash
script/lint && script/type-check
script/hassfest          # cross-checks every step/error/abort key against translations
script/test
```

Then restart Home Assistant and **walk every flow you touched in the UI** — add, reconfigure, options, and, by
invalidating the credential, reauth. hassfest proves the translation keys exist; only the UI proves the flow is usable.
A flow that passes CI and dead-ends on the second step is the normal failure here.

## Do not

- Do not do blocking I/O or long retries inside a flow step; validate with a short timeout.
- Do not call the flow done before walking it in the UI.
