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

**NEVER use `[%key:...%]` references, and never create `strings.json`.** Both are Home Assistant **Core**
build-time features. Core compiles `strings.json` into `translations/en.json` and resolves the references on the way;
a custom integration has no such build step, so its `translations/*.json` is served exactly as written.

- ❌ `"stale_auth": "[%key:component::{domain}::config::error::invalid_auth%]"` — the UI shows that literal string
- ❌ `"off": "[%key:common::state::off%]"` — Core's `common` strings do not exist here
- ✅ Write out the full English text for every key, even when it duplicates another key or a Core string

Symptom when this is wrong: the config flow shows raw keys (`username` instead of `Enter Username`) instead of
translated labels.

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
      "name": "Air Quality Index",
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

**Use informal address** in every language that distinguishes it — German "du" not "Sie", French "tu" not "vous",
Spanish "tú" not "usted", and the same for the plural forms. German additionally needs the correct imperative:
"Gib deine Anmeldedaten ein", never "Gebe" ([Duden: Bildung des
Imperativs](https://www.duden.de/sprachwissen/sprachratgeber/Bildung-des-Imperativs)).

### Multi-Language Files

All language files must have identical structure — only the values differ. For a region-specific file (`en-US`,
`fr-CA`), only include keys whose translation actually differs from the base language.

## Best Practices

- **Only native speakers** should provide translations
- **Keep badge labels short** — a `state_badge` translation that overflows is only visible in the UI
- **Accept duplicated text** — there is no reference syntax here, so the same sentence is written out per key
- **Keep consistent terminology** within and across languages
- **Provide helpful descriptions** for non-obvious fields in `data_description`

## References

- [Custom Integration Localization](https://developers.home-assistant.io/docs/internationalization/custom_integration) - **Primary reference**
- [Backend Localization](https://developers.home-assistant.io/docs/internationalization/core) - Key structure only; it
  documents Core's `strings.json` and its `[%key:...%]` syntax, neither of which applies here
- [ICU Message Format](https://formatjs.github.io/docs/core-concepts/icu-syntax/) - Placeholder syntax for plurals
