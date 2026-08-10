---
name: blueprint-skill-maintenance
description: >-
  Maintain the agent skill set that this blueprint template ships to downstream integration repositories. Use when
  asked to "add a skill", "update the skills", "this skill is out of date", "split this skill", "remove a skill",
  "the skills disagree with the instructions", or after bumping the pinned Home Assistant version, which can
  invalidate advice in several skills at once. Covers the shipped-set checklist, the rule-versus-procedure seam
  against .agents/instructions, where the catalogue is duplicated, template-sync safety, and the validation and
  eval loop. SYMPTOMS — load this if you are about to: write a concrete domain or class name into a skill; add a
  skill without evals or without listing it in the catalogue; restate in a skill a rule that already lives in an
  instructions file; or edit a skill through one of the symlinked paths instead of .agents/skills/.
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

| It is…                                                        | It belongs in…              |
| ------------------------------------------------------------- | --------------------------- |
| A rule that holds whenever a file of that type is edited      | `.agents/instructions/*.md` |
| An ordered procedure, or a decision the developer has to make | `.agents/skills/*/SKILL.md` |
| An explanation, a rationale, or a one-time human setup step   | `docs/development/`         |

"MUST inherit from X", "never set `name=`", "the per-platform member table" are rules. "First clarify Y, then edit Z,
then validate with W" is a procedure. When a skill needs a rule in order to make sense, **link to it** — do not copy
it. Two copies of a rule become two contradicting rules within a release or two.

Copilot, VS Code and Claude Code all inject the matching instructions file automatically when a file of that type is
touched. Codex does not — its nested `AGENTS.md` support keys off the working directory, not the edited file. That is
why the pointer at the top of each skill names _what_ is in the instructions file rather than just linking it: for
Codex the skill is the only bridge.

When you add or change an instructions file, keep `applyTo` (Copilot, VS Code) and `globs` (Claude Code, via the
`.claude/rules/instructions` symlink) byte-identical. A file without `globs` is loaded by Claude Code into every
session. `script/skills-check` verifies both.

## Adding a skill to the shipped set

1. Decide it is really a skill and not a rule (see the seam above), and that no existing skill should absorb it.
   Name it `ha-*` for Home Assistant integration work or `blueprint-*` for this repository's tooling — both prefixes
   are reserved for the shipped set, so downstream repositories can use their own without risking a collision. Keep
   the name short: it is what people type to invoke the skill.
2. Create `.agents/skills/<name>/SKILL.md`. Use the `<domain>` and `{ClassPrefix}` placeholders — never the concrete
   domain and class-prefix values this repository ships with, or `initialize.sh` will personalise them downstream and
   the next template sync will overwrite the result with the blueprint's own names. `script/skills-check` fails the
   build if a concrete identifier slips in, including in a code sample or a negative example.
3. Write `evals/evals.json` with 2–3 realistic prompts. At least one should be a _bad_ instruction that the skill is
   supposed to push back on — those catch regressions that happy-path evals never will.
4. Add it to the catalogue in **every** place listed below.
5. `script/skills-check && script/markdown`, then `script/skill-evals <name>`.

## Where the catalogue is duplicated

Adding or renaming a skill means touching these. There is no generator, so this list is the safeguard:

| File                       | Form                           |
| -------------------------- | ------------------------------ |
| `.agents/skills/README.md` | table with a "Use when" column |
| `AGENTS.md`                | table with a "Use when" column |

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
- **Re-run that skill's evals.** A skill edit that does not move an eval either fixed nothing or is untested.
- If a downstream maintainer would reasonably have edited this skill locally, remember their change is protected only
  if they listed it in `.templatesyncignore` — see the downstream section of [`../README.md`](../README.md).

## Removing or renaming a skill

Renaming changes the invocation name (`/skill-name`) and every catalogue entry, and silently breaks any downstream
`.templatesyncignore` entry that pinned the old path. Prefer rewriting a skill in place over renaming it. If it must
go, remove the directory, all catalogue entries, and any cross-links from other skills — `script/skills-check`
verifies that no link dangles.

## After a Home Assistant version bump

`script/ha-version-sync` changes the pinned version; several skills make version-specific claims that may now be
stale. Re-verify against the newly installed source, not from memory:

- `ha-modern-apis` — the whole deprecation table, plus `references/deprecations.md`
- `ha-quality-review` — `references/quality-scale-rules.md` against `script/hassfest/quality_scale.py` upstream
- `ha-entity-platform`, `ha-config-flow` — any API named in a code sample
- `ha-testing` — new `DeprecationWarning`s become test failures, because warnings are errors here

Then `script/skill-evals` across the set. This is the one moment where running all of them is worth the cost.

## Do not

- Do not edit skills through `.claude/skills/` — it is a symlink; edit `.agents/skills/` so the path in your diff
  matches what other maintainers see.
- Do not add a `.github/skills/` symlink back. Every client that reads it also reads `.agents/skills/`.
- Do not add frontmatter fields beyond `name` and `description` without a concrete reason — each one is a portability
  risk across the clients this template targets.

`script/skills-check` covers the spec's mechanical limits, so do not restate them in a skill either.
