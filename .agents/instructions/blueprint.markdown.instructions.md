---
name: "Markdown Documentation"
description: "markdownlint rules, document structure, and the instructions-file frontmatter contract"
applyTo: "**/*.md"
paths:
  - "**/*.md"
---

# Markdown Instructions

**Applies to:** All Markdown documentation files

## Linting and Validation

`script/markdown` formats and reports; the configuration is `.markdownlint.json`. The three rules that differ from the
defaults and would otherwise surprise you: **MD013 off** (no line-length limit), **MD033 off** (inline HTML allowed),
**MD041 off** (the first line need not be an H1). MD049/MD050 enforce `_italic_` and `**bold**`.

## Conventions here

- Unordered lists use `-`; code fences always name their language (`text` for plain output).
- Relative links for anything inside the repository, absolute URLs for everything else.
- `✅` / `❌` / `⚠️` are the project's markers for do / don't / warning. Use them or plain prose, not a third scheme.

## Structure

- `docs/development/` — developer documentation (architecture, decisions)
- `docs/user/` — end-user guides (installation, configuration)
- `.agents/scratch/` — temporary AI notes, never committed
- Root `*.md` — project metadata (README, CONTRIBUTING, …)

Past ~500 lines, add a table of contents or split the file.

## Instructions Files

**Path-scoped instructions (`.agents/instructions/*.instructions.md`):**

These files are shared by two agents through different frontmatter keys, so every file needs **both**, describing the
same set of patterns in the two shapes each agent expects:

```yaml
---
name: "Entity Platforms" # Copilot — display name in the Chat view
description: "Entity descriptions, translation keys, and device registry ownership" # Copilot — hover text
applyTo: "custom_components/**/sensor/**/*.py, custom_components/**/entity/**/*.py" # Copilot and VS Code
paths: # Claude Code — the same patterns as a YAML list
  - "custom_components/**/sensor/**/*.py"
  - "custom_components/**/entity/**/*.py"
---
```

`name` and `description` are documented Copilot keys and are only cosmetic there; Claude Code ignores them. They are
required on every file anyway, so the set reads consistently in the Chat view — `script/skills-check` enforces that.

`applyTo` takes one comma-separated string; `paths` takes a YAML list with one pattern per item. `paths` is the only
key Claude Code recognises — `globs` belongs to Cursor and is silently ignored here. `.claude/rules/instructions` is a
symlink to this directory, so Claude Code reads the same files.

A file **without** `paths` is loaded by Claude Code into every session. That is the documented behaviour for unscoped
rules, so a wrong or missing key never errors — it just quietly stops scoping. `script/skills-check` is what makes it
visible: it verifies that `paths` equals `applyTo` split on commas, and rejects a stray `globs`.

> [!NOTE]
> Path-scoped rules load when Claude Code **reads** a matching file, not at session start and not when the file is
> merely open in the editor. They are also not re-injected after `/compact`. Only
> `blueprint.commit-message.instructions.md` is deliberately unscoped, because commit conventions are not tied to
> reading a particular file; it is allowlisted in `script/.lib/skills_check.py`.

- Keep focused and concise (~50-300 lines)
- Enforce standards, not tutorials — procedures belong in an agent skill
- Use compact examples over verbose explanations

Every file with a partner skill **opens with a `Procedure:` line naming it**, directly under the `#` heading — see the
routing table in `AGENTS.md` for the pairing. Link the skill, do not summarise what it says; a rule lives in exactly
one of the two files. This is the recovery path: an agent that started editing without loading the skill gets this
file injected automatically, and the pointer is its only second chance. Files with no partner skill (`—` in the
routing table) get no line. `script/skills-check` verifies the link resolves.
