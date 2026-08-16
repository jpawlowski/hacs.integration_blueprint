---
name: blueprint-skill-maintenance
description: >-
  Maintain the agent skill set that this blueprint template ships to downstream integration repositories. Use when
  asked to "add a skill", "update the skills", "this skill is out of date", "split this skill", "remove a skill",
  "the skills disagree with the instructions", or after bumping the pinned Home Assistant version, which can
  invalidate advice in several skills at once. Covers the shipped-set checklist, the rule-versus-procedure seam
  against .agents/instructions, the pointers that must exist on both sides of it, where the catalogue is duplicated,
  template-sync safety, and the validation loop. SYMPTOMS — load this if you are about to: write a concrete domain or
  class name into a skill; add a skill without listing it in the catalogue or without a pointer from its partner
  instructions file; restate in a skill a rule that already lives in an instructions file; or edit a skill through one
  of the symlinked paths instead of .agents/skills/.
---

# Maintain the shipped skill set

**This repository is the blueprint itself.** Every change here reaches every integration repository generated from
it, through the weekly template-sync pull request. A skill that is wrong or bloated is not one repository's problem —
it is everyone's.

This skill is removed by `initialize.sh` when someone initialises a project from the template. Downstream maintainers
get [`../README.md`](../README.md) instead, which covers writing skills for their own repository.

## How to write a skill

The format, frontmatter rules, folded-scalar requirement, SYMPTOMS convention, placeholders and authoring principles
are in [`../README.md`](../README.md). Read it — this skill does not repeat it. What follows is what is specific to
maintaining a set that ships to other people.

## The seam: rule or procedure?

Every piece of guidance goes in exactly one place. Before writing anything into a skill, ask which of these it is:

| It is…                                                             | It belongs in…              |
| ------------------------------------------------------------------ | --------------------------- |
| A rule that holds whenever a file of that type is edited           | `.agents/instructions/*.md` |
| An ordered procedure, or a decision the developer has to make      | `.agents/skills/*/SKILL.md` |
| An explanation or rationale for whoever builds **an integration**  | `docs/development/`         |
| An explanation or rationale for whoever maintains **the template** | `docs/blueprint/`           |

The last row is decided by audience, not by subject. `docs/development/CUSTOMIZATION.md` describes hooks and template
sync — blueprint mechanisms both — but it addresses someone who received the blueprint, so it stays there. Why the
blueprint mints its development token offline addresses whoever maintains the blueprint, so it goes in
[`docs/blueprint/DECISIONS.md`](../../../docs/blueprint/DECISIONS.md).

`initialize.sh` deletes `docs/blueprint/` wholesale, and `docs/` is already in `.templatesyncignore`, so nothing there
needs further registration. Anything blueprint-only **outside** that directory needs all three steps — see
[`docs/blueprint/README.md`](../../../docs/blueprint/README.md).

"MUST inherit from X", "never set `name=`", "the per-platform member table" are rules. "First clarify Y, then edit Z,
then validate with W" is a procedure. When a skill needs a rule in order to make sense, **link to it** — do not copy
it. Two copies of a rule become two contradicting rules within a release or two.

Copilot, VS Code and Claude Code all inject the matching instructions file automatically when a file of that type is
touched. Codex does not — its nested `AGENTS.md` support keys off the working directory, not the edited file. That is
why the pointer at the top of each skill names _what_ is in the instructions file rather than just linking it: for
Codex the skill is the only bridge.

**The pointer runs both ways, and a pair is only done when both ends exist.** The skill opens with a
`**Read … first**` block; its instructions file opens with a `**Procedure:**` line naming the skill. They cover
opposite failures. The skill's block is for an agent that already knows which task it is on but not which rules bind
it. The instructions file's line is for the commoner case: an agent that went straight into the code, loaded no skill,
and gets that file injected on the first read — the pointer is the only thing that still routes it. Neither end
summarises the other; both are links. When you rename or remove a skill, both ends move — `script/skills-check`
catches a link that no longer resolves, but it cannot invent a pointer that was never written.

When you add or change an instructions file, keep `applyTo` (Copilot, VS Code — one comma-separated string) and
`paths` (Claude Code, via the `.claude/rules/instructions` symlink — a YAML list) describing the same patterns. A file
without `paths` is loaded by Claude Code into every session. The full frontmatter contract, including the `name` and
`description` keys and the one deliberately unscoped file, is in
[`../../instructions/blueprint.markdown.instructions.md`](../../instructions/blueprint.markdown.instructions.md);
`script/skills-check` enforces it.

## Write for both roles

Every skill except this one is synced downstream and read in two kinds of repository: this template, and the
initialised integration repositories generated from it. The same sentence has to be true in both.

- **"this repository", "this project"** — the repository the agent is in, whichever that is. This is the default.
- **"the blueprint", "the template", "upstream"** — reserved for the repository this one was generated _from_.
  Correct downstream, and correct here too.
- **"this blueprint"** — almost always wrong. Downstream it claims the maintainer's integration is a template.

The `blueprint-` prefix names where a skill came from, not what the repository is. `blueprint-tooling` is about the
tooling the template ships, and it applies in an initialised integration exactly as it does here.

The `repo-role` block at the top of `AGENTS.md` settles which role a repository is in, and `AGENTS.md` is always
loaded — a skill never needs to work it out for itself, and must not try to. In particular, the upstream template and
a not-yet-initialised copy are byte-identical, so no file in the working tree distinguishes them and the git remote is
not a reliable substitute.

## Adding a skill to the shipped set

1. Decide it is really a skill and not a rule (see the seam above), and that no existing skill should absorb it.
   Name it `ha-*` for Home Assistant integration work or `blueprint-*` for this repository's tooling — both prefixes
   are reserved for the shipped set, so downstream repositories can use their own without risking a collision. Keep
   the name short: it is what people type to invoke the skill.
2. Create `.agents/skills/<name>/SKILL.md`. Use the `<domain>` and `{ClassPrefix}` placeholders — never the concrete
   domain and class-prefix values this repository ships with, or `initialize.sh` will personalise them downstream and
   the next template sync will overwrite the result with the blueprint's own names. `script/skills-check` fails the
   build if a concrete identifier slips in, including in a code sample or a negative example.
3. Add it to the catalogue in **every** place listed below.
4. If it has a partner instructions file, add the `**Procedure:**` pointer there (see the seam above) and fill in the
   instructions column of the `AGENTS.md` routing table. A skill with no partner file leaves that column `—`.
5. `script/skills-check && script/markdown`.

## Where the catalogue is duplicated

Adding or renaming a skill means touching these:

| File                       | Form                                                     |
| -------------------------- | -------------------------------------------------------- |
| `.agents/skills/README.md` | table with a "Use when" column                           |
| `AGENTS.md`                | routing table: task → skill → matching instructions file |

There is no generator. In this blueprint, `script/skills-check` verifies both directions: every skill directory is
linked from both files, and every skill link in them resolves. In an initialized repository, `AGENTS.md` is owned by
that repository and excluded from template sync, so the checker requires new synchronized skills only in the skills
README; it still verifies that every existing link in `AGENTS.md` resolves. It cannot check that the "Use when" text
is any good.

No other file carries a catalogue, and none should. Codex and Copilot read `AGENTS.md` natively, and `CLAUDE.md`
imports it — all three already have the table. Every extra copy is another place to forget.

`README.md` and `CONTRIBUTING.md` describe the set by theme rather than by name, so they only need touching when a
whole new area appears. Neither states a skill count — do not reintroduce one, it is a maintenance trap that goes
stale silently and is wrong downstream anyway, where this skill has been removed.

## Changing an existing skill

- **Behaviour changes are the point; churn is not.** Downstream maintainers review a diff every week. Rewording for
  taste costs them attention and buys nothing.
- **Check the counterpart instructions file** in the same change. If you add a rule to a skill, it probably belongs in
  the instructions file instead, and if it contradicts one already there, one of the two is now wrong.
- If a downstream maintainer would reasonably have edited this skill locally, remember their change is protected only
  if they listed it in `.templatesyncignore` — see the downstream section of [`../README.md`](../README.md).

## Removing or renaming a skill

Renaming changes the invocation name (`/skill-name`) and every catalogue entry, and silently breaks any downstream
`.templatesyncignore` entry that pinned the old path. Prefer rewriting a skill in place over renaming it. If it must
go, remove the directory, all catalogue entries, the `**Procedure:**` pointer in its partner instructions file, and any
cross-links from other skills. `script/skills-check` covers all four — it link-checks the skills, the two catalogues
and `.agents/instructions/` — so run it and fix what it names rather than hunting by hand.

## After a Home Assistant version bump

`script/ha-version-sync` changes the pinned version; several skills make version-specific claims that may now be
stale. Re-verify against the newly installed source, not from memory:

- `ha-modern-apis` — the whole deprecation table, plus `references/deprecations.md`
- `ha-quality-review` — `references/quality-scale-rules.md` against `script/hassfest/quality_scale.py` upstream
- `ha-entity-platform`, `ha-config-flow` — any API named in a code sample
- `ha-testing` — new `DeprecationWarning`s become test failures, because warnings are errors here

## Do not

- Do not edit skills through `.claude/skills/` — it is a symlink; edit `.agents/skills/` so the path in your diff
  matches what other maintainers see.
- Do not add a `.github/skills/` symlink back. Every client that reads it also reads `.agents/skills/`.
- Do not add frontmatter fields beyond `name` and `description` without a concrete reason — each one is a portability
  risk across the clients this template targets.

`script/skills-check` covers the spec's mechanical limits, so do not restate them in a skill either.
