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

**markdownlint is configured but not enforced:**

- Extension installed: `davidanson.vscode-markdownlint`
- Configuration: `.markdownlint.json` in project root
- Shows warnings in editor, but **no automatic formatting on save**
- User can manually format via Command Palette if desired

**Key rules from `.markdownlint.json`:**

- ✅ Fenced code blocks preferred (`code-block-style: fenced`)
- ✅ Underscore for emphasis (`_italic_`), asterisks for strong (`**bold**`) — MD049/MD050 enforce this split
- ❌ MD013 disabled (no line length limit for prose)
- ❌ MD033 disabled (inline HTML allowed: `<br>`, `<details>`, `<kbd>`, etc.)
- ❌ MD041 disabled (first line doesn't need to be H1)

## Formatting Standards

**Headers:**

- Use ATX-style (`#` not underlines)
- One H1 per file (usually)
- Don't skip heading levels (H1 → H2 → H3, not H1 → H3)

**Code blocks:**

- Always specify language: ` ```python `, ` ```bash `, ` ```yaml `
- Use `console` or `bash` for terminal commands
- Use `text` for plain output

**Lists:**

- Unordered: Use `-` (dash)
- Ordered: Use `1.` with proper numbering
- Consistent indentation (2 spaces for nested items)

**Links:**

- Relative links for internal docs: `[Getting Started](../../docs/user/GETTING_STARTED.md)`
- Absolute URLs for external: `https://developers.home-assistant.io/`
- Reference-style for repeated URLs

## Structure

**Documentation organization:**

- `docs/development/` - Developer documentation (architecture, decisions)
- `docs/user/` - End-user guides (installation, configuration)
- `.agents/scratch/` - Temporary AI notes (not committed)
- Root `*.md` files - Project metadata (README, CONTRIBUTING, etc.)

**Long documents (>500 lines):**

- Add table of contents near top
- Use clear section headers
- Consider splitting into multiple files

## Common Patterns

**Inline code:** Use backticks for `filenames`, `symbols`, `commands`

**Emphasis:** Use `_italic_` for emphasis, `**bold**` for strong emphasis

**Tables:** Use proper alignment, pipes, and headers:

```markdown
| Column 1 | Column 2 | Column 3 |
| -------- | -------- | -------- |
| Value    | Value    | Value    |
```

**Admonitions (optional):** Use `> **Note:**` or emoji indicators:

- ✅ Do this
- ❌ Don't do this
- 🎯 Best practice
- ⚠️ Warning

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
