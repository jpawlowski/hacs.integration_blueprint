---
name: blueprint-import
description: >-
  Migrate an existing Home Assistant custom integration into the blueprint's structure and tooling without
  breaking the installations already running it. Use when asked to "import my integration", "migrate my existing
  integration into the blueprint", "adopt the blueprint in my repository", "move my custom component over",
  "restructure my integration to match this layout", or when a repository is being switched from another template
  such as the upstream ludeeus one. Covers what must stay byte-identical, the git and repository strategy, the
  phase order that keeps every step revertable, and how to apply this project's agent rules to code that
  predates them. SYMPTOMS — load this if you are about to: change the integration's domain during the move; run
  the whole migration as one commit; restructure packages before the imported code is green; let an automated
  rename touch unique IDs or translation keys; or start editing without a record of the current entity IDs.
---

# Import an existing integration

A published integration has users. Their automations, dashboards, and statistics are bound to entity IDs, unique IDs,
state values and action names — none of which the migration is allowed to change. Everything else is negotiable.

**The whole procedure is one long behaviour-preserving refactor.** Treat any observable difference as a bug in the
migration, not as an improvement, unless the developer explicitly asked for it.

## Phase 0 — Baseline first, before touching anything

Without a record of the current behaviour, nothing in the later phases is verifiable.

1. **Capture the identity of every entity.** From a running installation, export the entity IDs and unique IDs of the
   integration's entities (the entity registry, or the diagnostics download). If no live instance is available, derive
   them from the code and say so — a derived baseline is weaker.
2. **Record the contract** in a scratch file under `.agents/scratch/`:
   - the domain
   - the `unique_id` format for the config entry and for each entity
   - the keys stored in `entry.data` and `entry.options`, and the config entry `VERSION` / `MINOR_VERSION`
   - the service action names and their field names
   - the `device_class`, `state_class`, unit and attribute names of every entity
   - any `Store` / `.storage` key the integration writes
3. **Note what the integration depends on**: `manifest.json` → `requirements`, the minimum Home Assistant version, and
   whether it uses discovery.

This file is the acceptance test for phases 3 to 5. Nothing in it may change without an explicit decision under
[`ha-breaking-changes`](../ha-breaking-changes/SKILL.md).

## Phase 1 — Repository, then `initialize.sh`

**Stay in the existing GitHub repository.** Issues, stars, releases and the HACS listing are tied to the repository
URL, not to the commit history inside it. Pull the blueprint into that repository rather than starting a new one from
the template. The git strategies — clean force-push versus merging unrelated histories — and the repository settings
to re-check are in [`references/git-strategy.md`](references/git-strategy.md).

Then run `initialize.sh` **with the identifiers the integration already has**:

- `--domain` **must** be the existing domain. It is the primary key of every config entry and the prefix of every
  entity ID. Changing it does not migrate anything — it orphans every installation. If the developer wants a
  different domain, stop and treat it as its own breaking change with its own decision.
- `--title` should match the name users already see, unless a rename is deliberate.
- `--namespace` sets the class prefix. Picking the prefix the code already uses means no rename happens at all, which
  is the safest option. If you do pick a new one, phase 2's verification exists precisely to catch what the rename
  swept up.

`initialize.sh` normally refuses to run outside a fresh single-commit template clone; `--force` is required here. Use
`--dry-run` first.

## Phase 2 — Drop the code in unchanged, and get it green

Copy `custom_components/<domain>/` from the old repository over the blueprint's generated one — **replacing it, not
merging into it**. The blueprint's example platforms, API client and entities are demonstrations; keeping any of them
alongside real code ships broken entities.

Home Assistant does not care about the internal file layout, so a flat set of modules is perfectly valid at this
point. Do not restructure yet.

Then make it pass, changing as little as possible:

```bash
script/lint          # fixes formatting, reports the rest
script/type-check
script/hassfest
script/test
```

Reconcile `manifest.json` → `requirements` with the root `requirements.txt`, and restore any `hacs.json` fields the
old repository had that `initialize.sh` did not carry over ([`blueprint-tooling`](../blueprint-tooling/SKILL.md)).

**Verify against phase 0 and commit.** This checkpoint — old code, new tooling, everything green — is the fallback
every later phase can be reverted to. Reaching it is the milestone worth reporting.

## Phase 3 — Modernise the APIs, and nothing else

Old integrations accumulate APIs that Home Assistant has since deprecated or removed. Fix those now, while the file
layout is still familiar and a diff is easy to read. [`ha-modern-apis`](../ha-modern-apis/SKILL.md) carries the full
table; the ones that show up in nearly every legacy integration, together with the upstream-template patterns worth
recognising, are in [`references/legacy-patterns.md`](references/legacy-patterns.md).

This phase is strictly behaviour-preserving. Resist every improvement that changes what a user observes — note it for
later instead. Commit separately from phase 4.

## Phase 4 — Restructure into the blueprint layout

Only now move code into `api/`, `coordinator/`, `entity/`, `config_flow_handler/`, `<platform>/`, `service_actions/`,
`utils/` as described in `docs/development/ARCHITECTURE.md` and the "Integration Structure" section of
[`AGENTS.md`](../../../AGENTS.md).

This is file movement and import rewriting, not redesign. Two things to be deliberate about:

- The blueprint keeps a thin `config_flow.py` shim at the top level and the real flow in `config_flow_handler/`.
  Home Assistant discovers the flow through the shim, so it must stay.
- One entity class per file. Splitting a large platform module is the main real work of this phase.

After moving, re-run the full validation and re-verify the phase 0 contract. Unique IDs and translation keys are the
things most easily lost in a bulk rename.

## Phase 5 — Apply this project's rules to the imported code

The linters are mandatory but they only cover mechanics. What makes the import worthwhile is the guidance the linters
cannot express — apply it as a review pass, file type by file type, using the matching instructions file and skill:

| Area                      | What typically needs fixing in imported code                                                             |
| ------------------------- | -------------------------------------------------------------------------------------------------------- |
| Entities                  | `name=` and `icon=` in code instead of `translation_key` and `icons.json`; missing `state_class`         |
| Entity/coordinator layers | entities calling the API client directly instead of reading `coordinator.data`                           |
| Service actions           | registered in `async_setup_entry()` instead of `async_setup()`; `services.yaml` fields without selectors |
| Config flow               | no `unique_id`, or one derived from a host or IP; credentials in `entry.options`                         |
| Errors                    | bare `HomeAssistantError` with an English message instead of a translated one                            |
| Diagnostics               | absent, or present without `async_redact_data()`                                                         |
| Device registry           | unscoped registry lookups, or several subentries sharing one device                                      |

**Each of these can be a breaking change.** Adding a `translation_key` to an entity that had `name=` changes its
name, and adding a missing `state_class` changes its statistics. Check every one against the phase 0 contract and
raise it with the developer before implementing — see [`ha-breaking-changes`](../ha-breaking-changes/SKILL.md).

Work through this in small commits, not one sweep. If the developer wants only the mandatory parts, phases 0 to 4
already stand on their own.

## Phase 6 — Tests, review, release

- Add tests for whatever the old repository had none of, starting with the config flow and one platform
  ([`ha-testing`](../ha-testing/SKILL.md)).
- Run a full audit with [`ha-quality-review`](../ha-quality-review/SKILL.md).
- Start Home Assistant with the **existing** `config/.storage` and confirm the entry loads, the entity IDs are
  unchanged and history is intact. A mocked suite cannot prove this.
- Release under [`ha-release`](../ha-release/SKILL.md). If anything in the phase 0 contract did change, it needs a
  `BREAKING CHANGE:` footer and a migration note for users.

Report which verification actually happened and which did not ([`AI_POLICY.md`](../../../AI_POLICY.md)).

## Retire this skill when the import is done

Importing happens once. Afterwards this skill is dead weight in every session:

1. Delete `.agents/skills/blueprint-import/`.
2. Remove its rows from the catalogues in `.agents/skills/README.md` and `AGENTS.md`.
3. Add `.agents/skills/blueprint-import/` to `.templatesyncignore`, or the next weekly template-sync pull request
   restores it.

## Do not

- Do not change the domain, and do not "tidy up" a unique ID format, entity ID, or action name in passing.
- Do not apply the phase 5 rules as routine cleanup: swapping `name=` for a `translation_key` renames the entity in
  every dashboard, and adding a missing `state_class` rewrites its long-term statistics. Both need approval.
- Do not run phases 2 to 5 as one commit — a failure then has no revertable checkpoint.
- Do not restructure before the imported code is green in its original layout.
- Do not merge the blueprint's example entities with the imported ones.
- Do not trust an automated class rename around `unique_id`, `translation_key`, storage keys, or anything else the
  user's installation persisted; diff them explicitly.
- Do not abandon the old repository for a fresh one created from the template.
