---
applyTo: "**/*.md"
globs: "**/*.md"
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

These files are shared by two agents through different frontmatter keys, so every file needs **both**, listing the
same globs:

```yaml
---
applyTo: "custom_components/**/sensor/**/*.py" # Copilot and VS Code
globs: "custom_components/**/sensor/**/*.py" # Claude Code — identical string
---
```

`.claude/rules/instructions` is a symlink to this directory, so Claude Code reads the same files. A file **without**
`globs` is loaded by Claude Code unconditionally into every session — the key is not optional, and
`script/skills-check` verifies that both keys match exactly.

> [!NOTE]
> Claude Code's documentation names the key `paths`, but community testing
> ([anthropics/claude-code#17204](https://github.com/anthropics/claude-code/issues/17204)) reports that `paths` as a
> quoted YAML list never matches and fails **silently**. `globs` with a comma-separated string is reported to work and
> happens to take the same value as `applyTo`. Re-test if Claude Code changes this.

- Keep focused and concise (~50-300 lines)
- Enforce standards, not tutorials — procedures belong in an agent skill
- Use compact examples over verbose explanations
