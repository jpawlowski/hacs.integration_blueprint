---
name: "Translation Files"
description: "Key structure, placeholders, entity translations, and formality rules"
applyTo: "**/translations/*.json"
paths:
  - "**/translations/*.json"
---

# Translation Files Instructions

**Procedure:** [`ha-translations`](../skills/ha-translations/SKILL.md) — load it before adding or changing strings.
This file is the rule set; the skill is which keys a given change actually needs, which is where most missing-key
findings from `script/hassfest` come from.

**Applies to:** `custom_components/<your_domain>/translations/*.json`

## Schema Validation

**Schema:** `/schemas/json/translation_schema.json` - Defines complete structure

Translation files define user-facing text for config flows, options, entities, and errors.

## File Location

**Custom integrations** use the `translations/` folder with language-specific files:

- `en.json` - English (required base language)
- `de.json`, `fr.json`, etc. - Additional languages

**Language codes:** BCP47 format (e.g., `en`, `de`, `fr-CA`)

## Critical Instructions

### Translation Placeholders

**Runtime values:** Use `{variable}` syntax - replaced with actual values at runtime

- Never translate placeholder names (e.g., `{host}` stays `{host}`, not `{hôte}`)
- Placeholder names must match code exactly

**CRITICAL: Quotes inside string values** - Do not use single quotes (`'`) within string content around placeholders:

- ✅ `"message": "Service {service} is unavailable"` (no quotes around placeholder)
- ✅ `"message": "Service \"{service}\" is unavailable"` (escaped double quotes)
- ❌ `"message": "Service '{service}' is unavailable"` (single quotes cause hassfest errors)

**Why:** Single quotes within strings around placeholders are not translatable across languages (e.g., German uses „…", French uses «…») and cause validation failures.

**Note:** This is about quotes _inside the string value_, not the JSON delimiter quotes (which must always be double quotes per JSON spec).

**Placeholder names are valid identifiers** (`[a-zA-Z_][a-zA-Z0-9_]*`) **and say what they hold** — `{device_name}`, not
`{name2}` or `{0}`; the name is the translator's only context. Entity state values take no placeholders at all.

**No plural syntax.** ICU forms like `{count, plural, one {…} other {…}}` are frontend-only. Phrase the string so it
reads right for any number: "Devices found: {count}", not "{count} device(s) found".

**A translation whose placeholders differ from `en.json` is dropped** — Home Assistant logs an error and shows the
English string instead. Keep the placeholder set identical in every language.

### What hassfest rejects in a string

- A URL — put it in a placeholder (`"Get a key from {settings_url}."`) and pass it from code
- HTML tags — Markdown where the field supports it, plain text elsewhere
- Leading or trailing whitespace
- A key that is not lowercase `a-z`, `0-9`, `_` or `-`, or that starts, ends or doubles a `_`/`-` — entity, state,
  action and field keys alike

### Core's shared strings

**NEVER use `[%key:...%]` references, and never create `strings.json`.** Both are Home Assistant **Core**
build-time features. Core compiles `strings.json` into `translations/en.json` and resolves the references on the way;
a custom integration has no such build step, so its `translations/*.json` is served exactly as written.

- ❌ `"stale_auth": "[%key:component::{domain}::config::error::invalid_auth%]"` — the UI shows that literal string
- ❌ `"off": "[%key:common::state::off%]"` — Core's `common` strings do not exist here
- ✅ Write out the full English text for every key, even when it duplicates another key or a Core string

**Copy Core's wording rather than inventing a variant.** The shared strings are under `common` in the installed
`.venv/lib/python3.*/site-packages/homeassistant/strings.json` — `cannot_connect` is "Failed to connect",
`invalid_auth` is "Invalid authentication", the reauth title is "Authentication expired for {name}".

Symptom when this is wrong: the config flow shows raw keys (`username` instead of `Username`) instead of translated
labels.

### Entity Translations

**Requirements in code:**

- Set `has_entity_name=True` on entity
- Set `translation_key` property to match JSON key
- For placeholders: Set `translation_placeholders` dict

**Example:**

```json
"entity": {
  "sensor": {
    "air_quality": {
      "name": "Air quality index",
      "state": {
        "good": "Good",
        "poor": "Poor"
      }
    }
  }
}
```

### Markdown Support

These fields support Markdown formatting:

- Config/Options: `description`, `abort`, `progress`, `create_entry`
- Issues: `title`, `description`

### Proper Nouns

**Never translate:**

- Home Assistant
- Supervisor
- Brand names (product names)
- Technical identifiers

### Formality Level

**Use the form of address Home Assistant already uses in that language**, so the integration does not switch register
mid-dialog: German "du" not "Sie", Spanish "tú" not "usted", French "vous" not "tu". The per-language agreements are on
the [language guidelines](https://contributors.home-assistant.io/translate/reference/languages/) page; for a language
it does not list, follow Core's own `translations/<lang>.json`. German additionally needs the correct imperative:
"Gib deine Anmeldedaten ein", never "Gebe" ([Duden: Bildung des
Imperativs](https://www.duden.de/sprachwissen/sprachratgeber/Bildung-des-Imperativs)).

### Multi-Language Files

All language files must have identical structure — only the values differ. A region-specific file (`fr-CA`, `pt-BR`)
falls back to **English**, not to its base language, for every key it lacks — so copy the base language's string for
each key that reads the same in the region, rather than leaving it out.

## UI Text Style

English strings follow Home Assistant's [UI text guidelines](https://contributors.home-assistant.io/design/ui-text/)
and its [style guide](https://contributors.home-assistant.io/writing/reference/style/):

- American English, active voice, and "you"/"your" — never "the user"
- Sentence case for titles, labels, buttons and names: "Scan interval", not "Scan Interval"
- "Home Assistant" in full — never "HA" or "HASS"
- No "e.g.", "i.e." or "etc." — "like", "for example", "such as"
- The Oxford comma: "Zigbee, Z-Wave, and Matter"
- No all caps for emphasis
- "Select", not "click"
- Backticks around code-like values (entity IDs, file names); brand and protocol names as their owners write them
- Product terms in lowercase mid-sentence: automation, entity, device
- **Remove** when the thing still exists afterwards, **delete** when it is gone for good; **add** something that
  exists, **create** something new

**One thing has one name**, the one the [glossary](https://contributors.home-assistant.io/glossary/) gives it. Never
the retired ones: "action", not "service"; "integration", not "component"; "app", not "add-on"; "dashboard", not
"Lovelace"; "backward-incompatible change", not "breaking change" (in text users read — commit footers keep
`BREAKING CHANGE:`).

## Best Practices

- **Only native speakers** should provide translations
- **Keep badge labels short** — a `state_badge` translation that overflows is only visible in the UI
- **Keep consistent terminology** within and across languages
- **Provide helpful descriptions** for non-obvious fields in `data_description`

## References

- [Translations](https://contributors.home-assistant.io/core/integrations/translations/) - **Primary reference** for
  the key structure; it documents Core's `strings.json` and `[%key:...%]` syntax, neither of which applies here
- [UI text](https://contributors.home-assistant.io/design/ui-text/) and the
  [glossary](https://contributors.home-assistant.io/glossary/) - wording and terms
