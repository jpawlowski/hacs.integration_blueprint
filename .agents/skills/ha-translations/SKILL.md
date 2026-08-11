---
name: ha-translations
description: >-
  Add or fix user-facing strings for this Home Assistant custom integration — translations/en.json and other
  languages, icons.json, entity names and states, config flow labels and errors, service action descriptions,
  exception messages, and repair issue text. Use when asked to "update translations", "add a translation key",
  "translate", "fix the entity name", "add strings for the new sensor/action/option", "add icons", or when
  hassfest reports a missing or unused translation key. Covers the key structure, which keys each feature needs,
  placeholders, the icons.json contract, and the project's strict rule about only touching en.json. SYMPTOMS —
  load this if you are about to: write user-facing English into Python; edit a language file other than `en.json`;
  add an entity without its `entity.<platform>.<key>.name` key; skip `data_description` on a config flow field; or
  set `icon=` instead of using `icons.json`.
---

# Translations and icons

`translations/en.json` is the source of truth for every string a user sees. Home Assistant falls back to the raw key
when a string is missing, so a missing key is a visible bug, not a cosmetic one.

**Read [`blueprint.translations.instructions.md`](../../instructions/blueprint.translations.instructions.md)
first** — it holds the rules: placeholder syntax and the single-quote trap that breaks hassfest, why `[%key:…%]` and
`strings.json` must never appear here, entity translation requirements, which fields accept Markdown, proper nouns, the
informal-address rule per language, and cross-language structure. This skill is which keys a given change needs, and
how to write them.

## The project rule on languages

- Update **`en.json` only**. Never edit or create other language files on your own initiative — translations are
  contributed through the project's translation workflow, and machine-translating them creates churn no maintainer
  asked for.
- If the developer explicitly asks for another language, confirm which files before starting.
- During feature work, business logic comes first. Use the translation key in code immediately, and fill in `en.json`
  either when asked or when the feature is complete.

## Key structure

```jsonc
{
  "config": {
    "step": {
      "user": {
        "title": "…",
        "description": "…",
        "data": { "host": "Host" },
        "data_description": { "host": "The hostname or IP address of the device." }
      }
    },
    "error": { "cannot_connect": "…", "invalid_auth": "…", "unknown": "…" },
    "abort": { "already_configured": "…", "reauth_successful": "…" }
  },
  "options": { "step": { "init": { "data": {}, "data_description": {} } } },
  "entity": { "sensor": { "pm25": { "name": "PM2.5", "state": {} } } },
  "services": { "set_target_value": { "name": "…", "description": "…", "fields": {} } },
  "exceptions": { "set_target_value_failed": { "message": "…" } },
  "issues": { "deprecated_api_endpoint": { "title": "…", "description": "…" } },
  "selector": { "mode": { "options": { "auto": "Automatic" }, "unit_of_measurement": "seconds" } },
  "config_subentries": { "device": { "step": { "user": { "data": {} } } } },
  "device": { "gateway": { "name": "…" } },
  "system_health": { "info": { "api_endpoint": "…" } }
}
```

`config` also takes `flow_title`, `progress` and `create_entry` alongside `step`. Subentry strings live under
`config_subentries.<type>`, never under `config`.

## Which keys does my change need?

| You added…                         | Keys required                                                                                   |
| ---------------------------------- | ----------------------------------------------------------------------------------------------- |
| An entity with a `translation_key` | `entity.<platform>.<translation_key>.name`                                                      |
| An enum sensor or a `select`       | …plus `entity.<platform>.<key>.state.<value>` for **every** possible value                      |
| An entity attribute                | `entity.<platform>.<key>.state_attributes.<attr>.name` (and `.state` for enum attributes)       |
| A config flow field                | `config.step.<step>.data.<field>` **and** `config.step.<step>.data_description.<field>`         |
| A new `errors["base"] = "x"`       | `config.error.x`                                                                                |
| A new `async_abort(reason="x")`    | `config.abort.x`                                                                                |
| An options flow field              | `options.step.init.data.<field>` and `options.step.init.data_description.<field>`               |
| A service action                   | `services.<action>.name`, `.description`, `.fields.<field>.name`, `.fields.<field>.description` |
| A raised `HomeAssistantError`      | `exceptions.<translation_key>.message`                                                          |
| A repair issue                     | `issues.<issue_id>.title`, plus **either** `.description` **or** `.fix_flow.*` — never both     |
| A config subentry flow             | `config_subentries.<type>.step.<step>.…`, mirroring the `config` shape                          |
| A `system_health` value            | `system_health.info.<key>`                                                                      |

Two rules that catch most mistakes:

- **`name` vs. `data`.** Entity names live under `entity.*.name`; form field labels live under `step.*.data.*`. They are
  not interchangeable.
- **`data_description` is not optional in practice.** It is the small helper text under a field, and its absence is what
  makes a setup form feel unfinished.

## Raising a translated exception

The pattern that ties Python to the JSON — every `{placeholder}` in the string must be supplied at the call site, and
vice versa (hassfest checks both):

```json
{ "exceptions": { "set_target_value_failed": { "message": "Could not set the value: {error}" } } }
```

```python
raise HomeAssistantError(
    translation_domain=DOMAIN,
    translation_key="set_target_value_failed",
    translation_placeholders={"error": str(err)},
)
```

## Writing the strings

- Sentence case for names and labels ("Target temperature", not "Target Temperature"). Proper nouns and capitalised
  abbreviations keep their casing.
- **Keys** are `snake_case` — including translated state values and state attributes. Only the values are prose.
- No trailing period on `name` and `data` labels; full sentences with a period for `description` and `data_description`.
- Do not repeat the device or integration name in an entity name — `_attr_has_entity_name = True` means Home Assistant
  prefixes it already. "Temperature", not "Blueprint device temperature".
- Error messages say what happened and what to do, and never leak credentials, tokens, or raw stack traces.
- Match the wording Home Assistant uses for the same situation ("Failed to connect", "Invalid authentication") rather
  than inventing a variant — but write the text out. Core's `[%key:…%]` references do not resolve in a custom
  integration, so duplication is the correct outcome here, not a smell.
- Use the word the project already settled on. If `docs/development/GLOSSARY.md` exists it decides the wording here,
  because renaming an entity later is a breaking change ([`ha-grill`](../ha-grill/SKILL.md) is where those terms are
  agreed).

## icons.json

Entity icons belong in `custom_components/<domain>/icons.json`, not in `EntityDescription(icon=...)`.

**Do not give an entity an icon its device class already provides.** A PM2.5 sensor, a temperature sensor, a battery
sensor are all iconed correctly by Home Assistant; overriding them makes the integration look inconsistent with every
other one. Add an icon where there is no device class, or where the context genuinely differs from it.

Beyond a plain icon, a key can carry:

- `range` — pick by value: `{"0": "mdi:battery-outline", "10": "mdi:battery-10", …}`, ascending, and the icon chosen
  is the highest bound less than or equal to the current value. `default` covers unavailable or unparseable states.
  If a key defines both `state` and `range`, **`state` wins**.
- `state_attributes` — icons per attribute value, for things like a climate preset or a fan mode. Only attributes,
  not arbitrary keys.

```json
{
  "entity": {
    "sensor": {
      "pm25": { "default": "mdi:air-filter" },
      "mode": { "default": "mdi:cog", "state": { "auto": "mdi:autorenew", "off": "mdi:power-off" } }
    }
  },
  "services": {
    "set_target_value": { "service": "mdi:target" }
  }
}
```

Note the nesting: a service icon is `{"service": "mdi:…"}`, not a bare string. Sections get their own icons under
`"sections"`.

Prefer a `device_class` over an icon whenever one fits — device classes give correct icons, unit conversion, and
assistant behaviour for free.

## Validate

```bash
script/hassfest        # the authoritative check: missing keys, unused keys, bad placeholders
script/lint            # Prettier formats the JSON (2 spaces, no trailing commas)
```

Then restart Home Assistant and look at the actual UI — hassfest verifies structure, not whether the text reads well.

## Do not

- Do not add keys "for later" — hassfest flags unused keys.
- Do not reformat the whole file while adding one key; keep the diff small and the ordering as it is.
- Do not translate `key` values, entity IDs, or anything that ends up in an automation.

The remaining rules are in
[`blueprint.translations.instructions.md`](../../instructions/blueprint.translations.instructions.md).
