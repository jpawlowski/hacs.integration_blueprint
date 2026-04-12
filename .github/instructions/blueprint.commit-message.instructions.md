---
name: "Commit Message Conventions"
description: "Conventional Commits format for this Home Assistant integration project"
---

# Commit Message Conventions

Follow the [Conventional Commits](https://www.conventionalcommits.org/) specification.

## Format

```text
type(scope): short summary (max 72 chars)

- Body bullet point: explain WHAT changed and WHY, not HOW
- One bullet per logical change; include all non-trivial changes
- Reference issues if applicable: Closes #123 or Fixes #456

BREAKING CHANGE: Description (required if breaking, triggers major version bump)
```

**Always analyze the full staged diff before writing the message.** Summarize every meaningful change in the body — do not omit files or changes that are not obvious from the subject line.

## Types

| Type       | When to use                                                        |
| ---------- | ------------------------------------------------------------------ |
| `feat`     | User-facing new functionality (new sensor, service, config option) |
| `fix`      | Bug fix for user-facing issues                                     |
| `chore`    | Dev tooling, dependencies, devcontainer — NOT visible to users     |
| `refactor` | Code restructuring without functional change                       |
| `docs`     | Documentation only                                                 |
| `test`     | Adding or fixing tests                                             |
| `ci`       | CI/CD pipeline changes                                             |
| `perf`     | Performance improvements                                           |

Use `feat!` or `fix!` (with `!`) as shorthand for breaking changes when the summary line is sufficient. Always add the `BREAKING CHANGE:` footer for clarity.

## Scopes

Scope is optional but clarifies the affected component. Use the name of the affected layer or platform:

- **Platforms:** `sensor`, `switch`, `fan`, `binary_sensor`, `button`, `number`, `select`, `light`, `climate`, …
- **Layers:** `coordinator`, `api`, `entity`, `config-flow`, `service-actions`, `entity-utils`
- **System:** `diagnostics`, `repairs`, `manifest`, `translations`, `deps`, `devcontainer`, `tests`

## Rules

1. **Always analyze the full staged diff** — every modified file must be accounted for
2. **Always include a body** when more than one file changes or the subject alone is ambiguous
3. **Always include a scope** when the change is clearly scoped to one component or layer
4. Subject line: ≤ 72 chars, no capital after colon, no trailing period
5. Body: blank line between subject and body; use bullet points, not prose
6. Breaking changes: add `BREAKING CHANGE:` footer **and** warn the developer before implementing
7. Multiple unrelated changes → separate commits, not one large commit

## Examples

```text
feat(sensor): add temperature sensor for air purifier

- Add AirPurifierTemperatureSensor entity class
- Register sensor in sensor/__init__.py platform setup
- Add TEMPERATURE key to AirPurifierSensorEntityDescription

fix(coordinator): handle API timeout during initial refresh

- Wrap async_config_entry_first_refresh in try/except for TimeoutError
- Raise ConfigEntryNotReady instead of letting exception propagate

chore(devcontainer): add commit message instructions for Copilot

- Add .github/instructions/blueprint.commit-message.instructions.md with
  Conventional Commits types, scopes, rules, and examples
- Wire github.copilot.chat.commitMessageGeneration.instructions
  in devcontainer.json and settings.default.jsonc
- Add JSONC trailingComma override in .prettierrc.yml
- Trim verbose commit format blocks from copilot-instructions.md
  and AGENTS.md; both now reference the new file

feat!: redesign config entry data structure

- Replace flat dict with TypedDict ConfigEntryData
- Update coordinator and config flow to use new structure

BREAKING CHANGE: existing config entries must be re-created after upgrading
  from v1.x — no automatic migration provided
```
