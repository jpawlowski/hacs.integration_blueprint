# Blueprint-only documentation

Everything in this directory is about **the template itself** — how it is built, why it is built that way, and what a
maintainer of the blueprint needs to know. None of it applies to an integration created from the blueprint.

`initialize.sh` deletes this whole directory, so a repository that has been initialised never carries it.

## What belongs here

| Here — `docs/blueprint/`                                 | There — `docs/development/`                       |
| -------------------------------------------------------- | ------------------------------------------------- |
| Decisions about the template's own tooling and structure | Decisions about the integration being built       |
| Guides for adopting or maintaining the blueprint         | Guides for developing the integration             |
| Audience: whoever develops the blueprint                 | Audience: whoever develops an integration with it |

The test is the audience, not the subject. `docs/development/CUSTOMIZATION.md` describes hooks and template sync — both
blueprint mechanisms — but it is written for someone who _received_ the blueprint and wants to adapt it. It belongs
there. A record of why the blueprint mints its development token offline is written for whoever maintains the blueprint,
and belongs here.

## Why it cannot live in `docs/development/`

Two independent reasons, and either one is sufficient:

- **A downstream repository would inherit decisions nobody there made.** A maintainer reading their own decision log
  should find only their own choices in it.
- **It could never be kept up to date.** `docs/` is listed in `.templatesyncignore`, so no file under it ever reaches an
  existing downstream repository through the weekly template-sync pull request. Blueprint documentation left in
  `docs/development/` would be frozen at whatever the repository was created from, and would drift silently.

The second reason is why deleting at initialisation is the right answer rather than a tidiness preference: content that
cannot be updated must not be handed on in the first place.

## Adding another blueprint-only artefact

Files inside this directory need no further work — `initialize.sh` removes the directory as a whole, and `docs/` is
already excluded from template sync, so nothing reinstates it.

Outside this directory, a blueprint-only artefact needs all three steps:

1. Remove it in `remove_blueprint_specific_files()` in `initialize.sh` — in **both** the `--dry-run` and the real branch.
2. Add it to `.templatesyncignore`, or the next sync will reinstate what `initialize.sh` deleted.
3. For a fragment rather than a whole file, wrap it in `<!-- blueprint-only:start -->` and `<!-- blueprint-only:end -->`.
   `initialize.sh` strips the range; `script/skills-check` verifies the markers are balanced, because an unbalanced
   `start` would make the deletion run to the end of the file.

Maintaining the shipped agent skills has its own procedure:
[`blueprint-skill-maintenance`](../../.agents/skills/blueprint-skill-maintenance/SKILL.md).

## Contents

- [`DECISIONS.md`](DECISIONS.md) — architectural decisions about the blueprint itself
- [`MIGRATION.md`](MIGRATION.md) — adopting the blueprint in an existing HACS integration
- [`TRANSFORMATION_PROMPT.md`](TRANSFORMATION_PROMPT.md) — prompting a coding agent to run the transformation

`MIGRATION.md` and `TRANSFORMATION_PROMPT.md` are read **before** `initialize.sh` runs, which is why deleting them at
initialisation loses nothing: by then their job is done. The procedures they hand over to —
[`blueprint-import`](../../.agents/skills/blueprint-import/SKILL.md) and
[`blueprint-scaffold`](../../.agents/skills/blueprint-scaffold/SKILL.md) — are skills, and skills survive.
