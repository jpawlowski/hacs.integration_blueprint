# AI Agent Instructions

Always-loaded project context for every AI coding agent working on this Home Assistant custom integration. Per-file
style rules and task procedures live elsewhere — the routing table below says where.

Only what an agent cannot infer from the code belongs in this file. General Python, async or Home Assistant knowledge
does not; this project's identity, layering, workflow policy and traps do.

<!-- repo-role:start -->

## Which repository is this?

`initialize.sh` is present, so **this repository has not been initialised yet** — the domain, class prefix and
directory names below are still the template's placeholders. The script replaces them across the whole repository and
then deletes itself, and template sync never restores it. **Its absence, not any wording here, is what marks an
initialised integration.**

Two kinds of repository are in this state, and they are byte-identical — nothing in the working tree tells them apart:

- **The upstream template.** The placeholders are permanent here, and the example integration is itself the thing
  being maintained. Every change ships to every downstream repository through the weekly template-sync pull request,
  so skills and instruction files must use the `<domain>` and `{ClassPrefix}` placeholders rather than the concrete
  identifiers, and [`blueprint-skill-maintenance`](.agents/skills/blueprint-skill-maintenance/SKILL.md) governs the
  shipped skill set.
- **A fresh copy** made with GitHub's "Use this template" button, which still has to be initialised. **Do not write
  integration code first** — `initialize.sh` would overwrite it. Run `./initialize.sh`, then
  [`blueprint-scaffold`](.agents/skills/blueprint-scaffold/SKILL.md); when existing integration code is being migrated
  in, [`blueprint-import`](.agents/skills/blueprint-import/SKILL.md) covers the order instead.

When the request does not make clear which of the two this is, ask. **Do not infer it from the git remote** — a
contributor's fork of the template is not a copy awaiting initialisation.

<!-- repo-role:end -->

## Project Overview

**Identity — use these everywhere, never a variant:**

- **Domain:** `ha_integration_domain`
- **Title:** Integration Blueprint
- **Class prefix:** `IntegrationBlueprint`
- **Repository:** jpawlowski/hacs.integration_blueprint

**Key directories:**

- `custom_components/ha_integration_domain/` — integration code
- `config/` — Home Assistant configuration for local testing
- `tests/` — mirrors the integration structure
- `script/` — development and validation scripts
- `.agents/` — instructions, skills, and scratch space

## Where the rules live

| Layer                       | Loaded                | Contains                                          |
| --------------------------- | --------------------- | ------------------------------------------------- |
| `AGENTS.md`                 | always                | project identity, workflow rules, validation loop |
| `.agents/instructions/*.md` | per touched file      | passive style rules for one file type             |
| `.agents/skills/*/SKILL.md` | when a task matches   | active procedures for a specific kind of work     |
| `docs/development/`         | when someone reads it | architecture, decisions, rationale                |

Instruction files load automatically for the file you are touching in **GitHub Copilot and VS Code** (via `applyTo`)
and in **Claude Code** (via `paths`, through the `.claude/rules/instructions` symlink) — one copy serves both.
**Codex has no file-triggered mechanism: open the matching instructions file yourself** before editing a file of that
type.

Skills follow the [Agent Skills standard](https://agentskills.io/specification) and are loaded automatically by every
agent that implements it. If yours does not, read the `SKILL.md` before starting that kind of task.

### Routing table

| Working on                                             | Procedure                                                              | Style rules (`.agents/instructions/`)                  |
| ------------------------------------------------------ | ---------------------------------------------------------------------- | ------------------------------------------------------ |
| an entity platform or an individual entity             | [`ha-entity-platform`](.agents/skills/ha-entity-platform/SKILL.md)     | `blueprint.entities`                                   |
| a service action                                       | [`ha-service-action`](.agents/skills/ha-service-action/SKILL.md)       | `blueprint.service_actions`, `blueprint.services_yaml` |
| config flow, options, reauth, reconfigure, discovery   | [`ha-config-flow`](.agents/skills/ha-config-flow/SKILL.md)             | `blueprint.config_flow`                                |
| the coordinator, the API client, runtime debugging     | [`ha-coordinator-debug`](.agents/skills/ha-coordinator-debug/SKILL.md) | `blueprint.coordinator`, `blueprint.api`               |
| translations, `icons.json`                             | [`ha-translations`](.agents/skills/ha-translations/SKILL.md)           | `blueprint.translations`                               |
| tests                                                  | [`ha-testing`](.agents/skills/ha-testing/SKILL.md)                     | `blueprint.tests`                                      |
| repair issues and flows                                | [`ha-breaking-changes`](.agents/skills/ha-breaking-changes/SKILL.md)   | `blueprint.repairs`                                    |
| anything that could break existing installs            | [`ha-breaking-changes`](.agents/skills/ha-breaking-changes/SKILL.md)   | —                                                      |
| a Quality Scale audit or pre-release review            | [`ha-quality-review`](.agents/skills/ha-quality-review/SKILL.md)       | —                                                      |
| deprecation warnings, verifying an API is current      | [`ha-modern-apis`](.agents/skills/ha-modern-apis/SKILL.md)             | —                                                      |
| planning a large change, recording a decision          | [`ha-planning`](.agents/skills/ha-planning/SKILL.md)                   | —                                                      |
| commit messages, versioning, changelog, release notes  | [`ha-release`](.agents/skills/ha-release/SKILL.md)                     | `blueprint.commit-message`                             |
| validation scripts, dependencies, hooks, template sync | [`blueprint-tooling`](.agents/skills/blueprint-tooling/SKILL.md)       | `blueprint.shell`                                      |
| `manifest.json`                                        | —                                                                      | `blueprint.manifest`                                   |
| diagnostics                                            | —                                                                      | `blueprint.diagnostics`                                |
| any Python, YAML, JSON or Markdown file                | —                                                                      | `blueprint.python`, `.yaml`, `.json`, `.markdown`      |

Two one-time skills exist for a fresh repository and remove themselves as their final step:
[`blueprint-scaffold`](.agents/skills/blueprint-scaffold/SKILL.md) (turn the template into an integration for one real
device) and [`blueprint-import`](.agents/skills/blueprint-import/SKILL.md) (migrate an existing integration in).

Skills are validated by `script/skills-check` (part of `script/lint-check`, so CI enforces it).

## Contracts that hold everywhere

These are the ones an agent typically breaks _before_ it realises a skill or instructions file applies.

- **Entities → Coordinator → API client.** Never skip a layer; entities read `coordinator.data` and never call the API.
- **Register service actions in `async_setup()`**, not `async_setup_entry()` (Quality Scale rule `action-setup`).
- **A unique ID is a serial number, MAC, device ID or account ID** — never an IP address, hostname, URL, or a name the
  user chose.
- **Entity metadata comes from `EntityDescription` + `translation_key`** — never a hardcoded `name=` or `icon=`.
- **Coordinator failures raise**: `ConfigEntryAuthFailed` (triggers reauth), `UpdateFailed` (retry), or
  `ConfigEntryNotReady` during setup. Do not log `ConfigEntryNotReady` manually — HA already logs it at debug level.
- **Diagnostics must call `async_redact_data()`** for credentials, tokens, location and personal data.
- **YAML configuration is deprecated** for integrations talking to devices or services (ADR-0010) — config flow only.
- **Changing the shape of `entry.data`** requires a `VERSION`/`MINOR_VERSION` bump and `async_migrate_entry()`.

### Device registry ownership (Home Assistant 2026.8+)

Model priors are usually wrong here, and the rules apply across migrations, repairs, diagnostics, listeners and tests.

Every device is owned by exactly one config entry and at most one config subentry. Identifiers and connections are
unique only within their owning entry — never assume they are globally unique.

- Scope lookups with `async_get_device_by_identifier()` or `async_get_device_by_connection()`; the unscoped
  `async_get_device()` is out.
- Inside an entity, use `self.device_entry` rather than looking the device up again.
- Never attach this config entry to a device owned by another integration; helper entities link through
  `self.device_entry`.
- One device per config subentry; model a hub or account parent and its subentry devices as separate devices related
  by `via_device_id`.
- Do not rely on the composite-device compatibility shims — they are scheduled for removal in HA Core 2027.8.

Full "do not use → use instead" table: [`ha-modern-apis`](.agents/skills/ha-modern-apis/SKILL.md).

## Integration Structure

**Package organization — do not create packages outside this list:**

- `api/` — API client and exceptions
- `coordinator/` — data update coordinator
- `config_flow_handler/` — config flow, options, `validators/`, `schemas/`
- `entity/` — base entity classes
- `entity_utils/` — entity helpers (device info, state formatting)
- `<platform>/` — entity platforms (sensor, switch, …), one entity class per file
- `service_actions/` — service action implementations
- `utils/` — integration-wide utilities

`helpers/`, `common/`, `shared/`, `lib/` and any other new top-level package need explicit approval — use `utils/` or
`entity_utils/` instead.

`PLATFORMS` is defined in `__init__.py`. The top-level `config_flow.py` is only a discovery shim; the real flow lives
in `config_flow_handler/`. `services.yaml` keeps its legacy filename.

**Keep files focused** — roughly 200–400 lines, one class per file for entities.

Architecture and rationale: [`docs/development/ARCHITECTURE.md`](docs/development/ARCHITECTURE.md).

## Validation

**Always use the project's scripts** — do NOT craft your own `hass`, `pip`, `pytest`, `ruff` or `pyright` commands. The
scripts handle virtualenv activation, port management and cleanup that raw commands miss.

**The agent loop — fix-mode scripts auto-heal files _and_ print what they could not fix:**

```bash
# Run until both exit 0:
script/lint         # fixes Python + shell + markdown formatting; checks yaml + shellcheck; shows all remaining
script/type-check   # Pyright — no auto-fix, always a manual loop
# Fix what remains in the output above, then repeat.
```

No separate check-run is needed after a fix-mode script — its exit code and output are the complete picture.
`script/check`, `script/lint-check` and `script/python-check` are check-only variants for CI; agents should use fix
mode. `script/hassfest` validates the manifest, translations and `services.yaml` against Home Assistant's own rules.

```bash
script/test                    # all tests
script/test --cov-html         # with coverage report
script/test --snapshot-update  # update Syrupy snapshots
```

Which script for which change, the full fix/check matrix, and the configured tools:
[`blueprint-tooling`](.agents/skills/blueprint-tooling/SKILL.md).

`# noqa: CODE` and `# type: ignore` are allowed where genuinely warranted — a false positive or an untyped external
library — not to silence a real finding.

**When a fix does not take:** try once more with a different approach, and if that fails too, stop and explain what you
tried rather than looping. Report failing terminal commands, network timeouts and failed git operations instead of
working around them.

## Home Assistant test instance

```bash
./script/develop                                                  # start
pkill -f "hass --config" || true && pkill -f "debugpy.*5678" || true && ./script/develop   # force restart
```

Restart after changing Python files, `manifest.json`, `services.yaml`, translations or the config flow. Logs are live
in that terminal and in `config/home-assistant.log`. Log levels are set in `config/configuration.yaml` — raising
`custom_components.ha_integration_domain` to `debug` while investigating is expected.

Log reading, failure triage and the debugging loop: [`ha-coordinator-debug`](.agents/skills/ha-coordinator-debug/SKILL.md).

**Devcontainer CLI tools:** `bat`, `delta`, `eza`, `fd`, `fzf`, `http`, `hyperfine`, `ipython`, `jq`, `jo`, `mlr`,
`rg`, `shellcheck`, `shfmt`, `sponge`, `sqlite3`, `tree`, `yq`, `yamllint`. Debian package names differ from the
common spellings, so `fdfind`, `git-delta`, `httpie`, `miller` and `ripgrep` also resolve. `yq` is the Mike Farah
variant (`yq eval` syntax).

## Working With Developers

### Community AI policy

Read and follow [`AI_POLICY.md`](AI_POLICY.md). This project permits extensive AI assistance, but agents must not
overstate human review, maintainer understanding, automated coverage, or real-device testing. Prepare publication
material as drafts for human review, and follow the policy of any destination repository. Contributions to Open Home
Foundation repositories are additionally governed by the official OHF AI Policy.

### Commits

- **Never commit automatically** — only on an explicit request. A previous request is not standing permission; each
  commit needs a fresh instruction.
- **Never ask about pushing** — the developer handles `git push` themselves.
- When a task completes and the developer moves on, offer a commit message based on the work done.
- Format: [Conventional Commits](https://www.conventionalcommits.org/), enforced by the commitlint hook — see
  `.agents/instructions/blueprint.commit-message.instructions.md`.

### Scope of a change

- **One logical feature or fix:** implement it completely, even across 5–8 files.
- **Several independent features:** one at a time, offering a commit between them.
- **More than ~10 files or an architectural change:** propose a plan and get confirmation first
  ([`ha-planning`](.agents/skills/ha-planning/SKILL.md)).

**Tests:** for behavioural changes, bug fixes and regressions, add proportionate automated tests where they verify
something meaningful; if you omit them deliberately, say why and what risk remains. Documentation- and
formatting-only changes need none. Automated tests supplement rather than replace human review and real-device
testing.

**Translations:** update `en.json` only, and only when asked or at a feature milestone. **Never** touch another
language file without asking — code works without translations, so business logic comes first.

### Breaking changes — warn before implementing

Warn, and get explicit approval, before anything that changes entity IDs or unique IDs, config entry data, state
values, units, device classes or attributes, service call signatures, or that removes or renames a config option —
including options that look unused.

> ⚠️ This changes the entity ID format from `sensor.device_name` to `sensor.device_name_sensor`. Existing automations
> and dashboards will break. Should I proceed, or would you prefer a migration path?

Prefer a migration path over a break, and record it with a `BREAKING CHANGE:` footer.
Procedure: [`ha-breaking-changes`](.agents/skills/ha-breaking-changes/SKILL.md).

### When instructions conflict with a request

Say which instruction the request contradicts and restate what you understood, then follow the developer's decision.
If it reflects a permanent change of approach, offer to update the instruction file — and propose updates whenever you
notice repeated deviations, stale rules, or a new pattern worth standardising.

### Documentation

Style rules go in `.agents/instructions/`, procedures go in a skill, explanations go in `docs/development/` (developer)
or `docs/user/` (end user). Use `.agents/scratch/` for temporary notes; it is never committed.

- ❌ Never create stray markdown files in code directories
- ❌ Never create documentation in `.github/` unless it is a file GitHub specifies
- ✅ Ask before creating permanent documentation
- ✅ Prefer a module docstring over a separate markdown file

## Custom Integration Flexibility

**This is a custom integration, not a Core one.** It follows Core patterns for quality, but implementation decisions
have more room.

**Third-party library or own client?** Prefer a maintained PyPI library that fits. Write a client instead when the
device speaks a simple REST or GraphQL API, or when the available libraries are unmaintained, bloated or badly
designed. Evaluate maintenance, async support, documentation and dependency footprint; complex OAuth2 and standards
like MQTT argue for a library. Record the outcome in [`docs/development/DECISIONS.md`](docs/development/DECISIONS.md).

**Aim for Silver or Gold on the Quality Scale.** Always implement type hints, async I/O, proper error handling,
actions registered in `async_setup()`, redacted diagnostics and device info. Add config flow validation, reauth,
discovery and repair flows where they apply. Multiple config entries, advanced discovery, YAML import and exhaustive
coverage may be deferred.

Discovery can come later, breaking changes are allowed when documented, and experimental features are acceptable.

## Code Style

**Python** 4 spaces, 120 columns, double quotes, full type hints, async for all I/O · **YAML** 2 spaces, modern HA
syntax · **JSON** 2 spaces, no trailing commas, no comments.

Everything beyond that is in the per-file-type instruction files listed in the routing table.

## Reference

Home Assistant's APIs change often, and a pattern from an older integration, a blog post or model memory may already be
deprecated. Verify against the [developer docs](https://developers.home-assistant.io/), the
[developer blog](https://developers.home-assistant.io/blog/) and the installed Home Assistant source before relying on
one — [`ha-modern-apis`](.agents/skills/ha-modern-apis/SKILL.md) is the procedure.

- [Integration Quality Scale](https://developers.home-assistant.io/docs/integration_quality_scale_index)
- [Architecture docs](https://developers.home-assistant.io/docs/architecture_index)
- [`CONTRIBUTING.md`](CONTRIBUTING.md) — contribution guidelines
