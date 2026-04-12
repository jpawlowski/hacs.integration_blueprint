---
applyTo: "**/*.yaml, **/*.yml"
---

# YAML Instructions

**Applies to:** All YAML files

## Formatting Standards

- **2 spaces** for indentation (never tabs)
- No trailing whitespace
- End files with a single newline
- Use lowercase for keys (except where case matters)
- Prefer `>` for multi-line strings (folded) over inline strings
- Use `|` when preserving newlines is important

## Project-Specific Rules

- Keep files focused and readable
- Use comments to separate logical sections
- Group related configuration together

## Schema Validation

YAML schema files are available in `/schemas/yaml/`:

- `configuration_schema.yaml` — Validates Home Assistant `configuration.yaml`
- `services_schema.yaml` — Validates `services.yaml` (service action definitions)

Consult the relevant schema when editing YAML files to ensure correct structure.

## Home Assistant YAML Conventions

- Use modern HA configuration syntax (no legacy `platform:` style)
- Prefer `!include` for splitting large configurations
- Use `!secret` for sensitive values (passwords, API keys, tokens)
- Boolean values: `true`/`false` (lowercase)

## Validation

Run `script/yaml-check` after editing YAML files. yamllint has no auto-fix mode — all
errors require manual fixes.

```bash
script/yaml-check   # yamllint against integration YAML, schemas, .github/
```

Configuration: `.yamllint.yml` at the project root. Key rules:

- Line length: 120 chars (warning, not error)
- `document-start` (`---`): not required
- `truthy.check-keys: false`: allows GitHub Actions `on:` key

**Suppressing yamllint for a single line** (use sparingly):

```yaml
some_long_key: some_very_long_value_that_exceeds_120_chars # yamllint disable-line rule:line-length
```
