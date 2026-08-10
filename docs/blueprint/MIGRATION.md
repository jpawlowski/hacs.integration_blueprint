# Migrating an Existing HACS Integration to This Blueprint

This guide is for developers who already have a HACS integration and want to adopt this
blueprint's project structure, DevContainer environment, and tooling.

> [!NOTE]
> This file is part of the blueprint template and is removed automatically when you run
> `./initialize.sh`. That is deliberate — by that point the decisions below are made, and
> the rest of the migration is driven by the `blueprint-import` agent skill, which stays.
> The original lives at
> [jpawlowski/hacs.integration_blueprint](https://github.com/jpawlowski/hacs.integration_blueprint/blob/main/docs/blueprint/MIGRATION.md).

## The Core Idea

The only thing that really needs to come from your existing repository is the contents of
`custom_components/<your_domain>/`. Everything else — DevContainer, scripts, workflows,
configuration — comes from the blueprint and stays as-is (or is extended via hooks).

## The Two Decisions Only You Can Make

### 1. Keep your existing repository

> [!IMPORTANT]
> Issues, pull requests, stars, releases, and the HACS listing are all tied to the repository
> URL — not to the git history inside it. Creating a new repository from the template and
> abandoning the old one means losing all of that, and leaving your users subscribed to a
> repository that no longer updates.

Pull the blueprint **into** your existing repository. Either force-push a clean history
(simplest) or merge the blueprint with `--allow-unrelated-histories` (keeps your commit log,
expect nearly every file to conflict). Both procedures, with the exact commands and the
repository settings to re-check afterwards, are in
[`.agents/skills/blueprint-import/references/git-strategy.md`](../../.agents/skills/blueprint-import/references/git-strategy.md).

### 2. Your domain does not change

`./initialize.sh` must be run with the domain your integration **already** has. The domain is
the primary key of every config entry and the prefix of every entity ID your users have wired
into automations and dashboards. Changing it during the migration does not migrate anything —
it orphans every existing installation.

The same caution applies to `--namespace`: passing the class prefix your code already uses
means no rename happens at all, which is the safest option.

## Then Hand Over to the Agent Skill

Everything after those two decisions — importing the code, getting it green, modernising
deprecated Home Assistant APIs, restructuring into the blueprint's packages, and applying this
project's code rules to code that predates them — is an ordered procedure with a phase order
that matters. It lives in the
[`blueprint-import`](../../.agents/skills/blueprint-import/SKILL.md) skill, which your agent
loads automatically when you ask it to import your integration.

Read it yourself if you are migrating by hand. In particular, phase 0 — recording your current
entity IDs, unique IDs, entry data keys, and action names before touching anything — is what
makes the rest of the migration verifiable.

## See Also

- [ARCHITECTURE.md](../development/ARCHITECTURE.md) — the package layout the blueprint expects
- [CUSTOMIZATION.md](../development/CUSTOMIZATION.md) — template sync, `.templatesyncignore`, and hook scripts
- [`blueprint-tooling`](../../.agents/skills/blueprint-tooling/SKILL.md) — the validation scripts,
  and keeping `manifest.json` requirements in sync with `requirements.txt`
