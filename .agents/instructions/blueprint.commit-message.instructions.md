---
name: "Commit Message Conventions"
description: "Conventional Commits types, scopes, and rules enforced by commitlint"
applyTo: "**"
---

# Commit Message Conventions

**Procedure:** [`ha-release`](../skills/ha-release/SKILL.md) — load it when cutting a version, or when the choice of
type decides whether a change reaches users. This file is the rule set commitlint enforces; the skill is how
release-please turns those commits into a version and a changelog.

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

A scope names the affected _component_, never a change _category_. Using a type
name as a scope is rejected by commitlint (`scope-enum`), because it publishes
the change in the wrong changelog section: `feat(ci): …` lands under "Features"
as if it were user-facing, while the `ci` **type** is `hidden` in
`release-please-config.json`. Pipeline and tooling work takes the `ci` or
`chore` type — `ci: enable brands validation`, not
`feat(ci): enable brands validation`.

## Rules

1. **Always include a body** when more than one file changes or the subject alone is ambiguous
2. **Always include a scope** when the change is clearly scoped to one component or layer
3. Subject line: ≤ 72 chars, no capital after colon, no trailing period
4. Body: blank line between subject and body; use bullet points, not prose
5. Breaking changes: add `BREAKING CHANGE:` footer **and** warn the developer before implementing
6. Multiple unrelated changes → separate commits, not one large commit

## Example

The breaking-change shape, which the rules above do not show:

```text
feat!: redesign config entry data structure

- Replace flat dict with TypedDict ConfigEntryData
- Update coordinator and config flow to use new structure

BREAKING CHANGE: existing config entries must be re-created after upgrading
  from v1.x — no automatic migration provided
```
