# AI Agent Instructions

This document provides guidance for AI coding agents working on this Home Assistant custom integration project.

## Project Overview

This is a Home Assistant custom integration that was generated from a blueprint template. The integration follows Home Assistant Core development patterns and quality standards.

**Integration details:**

- **Domain:** `ha_integration_domain`
- **Title:** Integration Blueprint
- **Repository:** jpawlowski/hacs.integration_blueprint

**Key directories:**

- `custom_components/ha_integration_domain/` - Main integration code
- `config/` - Home Assistant configuration for local testing
- `tests/` - Unit and integration tests
- `script/` - Development and validation scripts

**Local Home Assistant instance:**

**Always use the project's scripts** — do NOT craft your own `hass`, `pip`, `pytest`, or similar commands. The scripts handle environment setup, virtual environments, port management, and cleanup that raw commands miss. Agents that bypass scripts frequently break.

**Devcontainer CLI tools:** The devcontainer provides common agent-facing CLI tools including `bat`, `delta`/`git-delta`, `eza`, `fd`/`fdfind`, `fzf`, `http`/`httpie`, `hyperfine`, `ipython`, `jq`, `jo`, `mlr`/`miller`, `rg`/`ripgrep`, `shellcheck`, `shfmt`, `sponge`, `sqlite3`, `tree`, `yq`, and `yamllint`. Prefer these explicit container tools over assuming a VS Code extension exposes an equivalent CLI on `PATH`.

**CLI compatibility notes:** Some commands are available via compatibility aliases because Debian package names differ from what agents often expect. Prefer `bat`, `fd`, `git-delta`, `httpie`, `ipython`, `miller`, and `ripgrep` as stable spellings. `yq` is installed as the Mike Farah variant, so standard `yq eval`/`yq e` syntax is expected.

**Start Home Assistant:**

```bash
./script/develop
```

**Force restart (when HA is unresponsive or port conflicts):**

```bash
pkill -f "hass --config" || true && pkill -f "debugpy.*5678" || true && ./script/develop
```

- Kills any existing instance (hass + debugpy on port 5678) and starts fresh
- Avoids state confusion and port conflicts

**When to restart:** After modifying Python files, `manifest.json`, `services.yaml`, translations, or config flow changes

**Reading logs:**

- Live: Terminal where `./script/develop` runs
- File: `config/home-assistant.log` (most recent), `config/home-assistant.log.1` (previous)

**Adjusting log levels:**

- Integration logs: `custom_components.ha_integration_domain: debug` in `config/configuration.yaml`
- You can modify log levels when debugging - just restart HA after changes

**Context-specific instructions:**

Path-specific style rules live in `.agents/instructions/*.instructions.md`, one file per file type (Python, YAML, entities, config flow, …). They load automatically for the file you are touching in **GitHub Copilot and VS Code** (via `applyTo`) and in **Claude Code** (via `globs`, through the `.claude/rules/instructions` symlink) — one copy of each file serves both.

**Codex and other agents have no such mechanism: open the matching instructions file yourself before editing a file of that type.** Each agent skill names the one it depends on.

**How each agent reaches this file:**

- **ChatGPT Codex:** reads `AGENTS.md` natively — nothing else needed
- **Claude Code:** reads [`CLAUDE.md`](CLAUDE.md), which imports this file with `@AGENTS.md`
- **GitHub Copilot / VS Code:** read `AGENTS.md` natively (`chat.useAgentsMdFile`, pinned on in this devcontainer)

## Agent Skills

Task-specific procedures live in [`.agents/skills/`](.agents/skills/README.md) as
[Agent Skills](https://agentskills.io/specification). Agents that support the open `SKILL.md` standard load the
matching skill automatically: Codex CLI, GitHub Copilot and VS Code read `.agents/skills/` directly, and Claude Code
reaches the same files through the `.claude/skills/` symlink.

**If your agent does not support skills, read the relevant `SKILL.md` manually before starting that kind of task.**

| Skill                                                                  | Use when                                                            |
| ---------------------------------------------------------------------- | ------------------------------------------------------------------- |
| [`ha-entity-platform`](.agents/skills/ha-entity-platform/SKILL.md)     | adding or changing an entity platform or an individual entity       |
| [`ha-service-action`](.agents/skills/ha-service-action/SKILL.md)       | adding or changing a service action                                 |
| [`ha-config-flow`](.agents/skills/ha-config-flow/SKILL.md)             | config flow, options, reauth, reconfigure, discovery, subentries    |
| [`ha-coordinator-debug`](.agents/skills/ha-coordinator-debug/SKILL.md) | entities unavailable, stale data, setup failures, runtime debugging |
| [`ha-translations`](.agents/skills/ha-translations/SKILL.md)           | translations, `icons.json`, entity and exception strings            |
| [`ha-testing`](.agents/skills/ha-testing/SKILL.md)                     | writing or fixing tests                                             |
| [`ha-quality-review`](.agents/skills/ha-quality-review/SKILL.md)       | auditing against the Integration Quality Scale                      |
| [`ha-modern-apis`](.agents/skills/ha-modern-apis/SKILL.md)             | deprecation warnings, verifying an API is still current             |
| [`ha-breaking-changes`](.agents/skills/ha-breaking-changes/SKILL.md)   | anything that could break existing installs                         |
| [`ha-planning`](.agents/skills/ha-planning/SKILL.md)                   | planning a large change, recording an architectural decision        |
| [`ha-release`](.agents/skills/ha-release/SKILL.md)                     | commit messages, versioning, changelog, release notes               |
| [`blueprint-tooling`](.agents/skills/blueprint-tooling/SKILL.md)       | validation scripts, dependencies, hooks, template sync              |

The layering is deliberate: this file is always-loaded project context, `.agents/instructions/*.instructions.md` are
passive per-file-type style rules, and skills are active procedures loaded only for the task at hand.

Skills are validated by `script/skills-check` (part of `script/lint-check`, so CI enforces it) and behaviourally tested
by `script/skill-evals`. If you change a skill, run both.

## Working With Developers

### Community AI Policy

Read and follow [`AI_POLICY.md`](AI_POLICY.md). This custom-integration blueprint permits extensive AI assistance, but
agents must not overstate human review, maintainer understanding, automated coverage, or real-device testing. Prepare
publication material as drafts for human review and follow the policy of any destination repository. Contributions to
Open Home Foundation repositories are additionally governed by the official OHF AI Policy.

### When Instructions Conflict With Requests

If a developer requests something that contradicts these instructions:

1. **Clarify the intent** - Ask if they want you to deviate from the documented guidelines
2. **Confirm understanding** - Restate what you understood to avoid misinterpretation
3. **Suggest instruction updates** - If this represents a permanent change in approach, offer to update these instructions
4. **Proceed once confirmed** - Follow the developer's explicit direction after clarification

### Maintaining These Instructions

**This project was recently initialized from a template.** Instructions should evolve as the project matures:

- Refine guidelines based on actual project needs
- Remove outdated rules that no longer apply
- Consolidate redundant sections to prevent bloat
- Keep files focused - Move architectural decisions to `docs/development/`

**Propose updates when:**

- You notice repeated deviations from documented patterns
- Instructions become outdated or contradict actual code
- New patterns emerge that should be standardized

### Documentation vs. Instructions

**Four types of content with clear separation:**

1. **Agent Instructions** - How AI should write code (`AGENTS.md`, `.agents/instructions/`)
2. **Agent Skills** - How to carry out a specific task (`.agents/skills/*/SKILL.md`)
3. **Developer Documentation** - Architecture and design decisions (`docs/development/`)
4. **User Documentation** - End-user guides (`docs/user/`)

Style rules go in `.agents/instructions/`, procedures go in a skill, explanations go in `docs/`.

**AI Planning:** Use `.agents/scratch/` for temporary notes (never committed)

**Rules:**

- ❌ **NEVER** create random markdown files in code directories
- ❌ **NEVER** create documentation in `.github/` unless it's a GitHub-specified file
- ✅ **ALWAYS ask first** before creating permanent documentation
- ✅ **Prefer module docstrings** over separate markdown files

### Session and Context Management

**Commit suggestions:**

When a task completes and the developer moves to a new topic, suggest committing changes. Offer a commit message based on the work done.

**Commit rules (CRITICAL):**

- **Never commit automatically** — only commit when the developer explicitly requests it
- A previous commit request is NOT a standing permission; each commit requires a fresh explicit instruction
- **Never ask about pushing** — the developer always handles `git push` themselves; do not offer or suggest it

**Commit message format:** Follow [Conventional Commits](https://www.conventionalcommits.org/) — see `.agents/instructions/blueprint.commit-message.instructions.md` for full conventions, types, scopes, and examples.

## Custom Integration Flexibility

**This is a CUSTOM integration, not a Home Assistant Core integration.** While we follow Core patterns for quality and maintainability, we have more flexibility in implementation decisions:

**Third-party libraries (PyPI):**

- ✅ Prefer existing PyPI libraries when maintained and fit the use case
- ✅ Build custom API client when:
  - Device/service uses simple REST API or GraphQL (HTTP, JSON)
  - Available libraries are unmaintained, bloated, or poorly designed
  - Using aiohttp + json is more maintainable than a framework

**Decision process:**

1. Research available libraries (PyPI, GitHub)
2. Evaluate: Maintained? Async? Well-documented? Dependency footprint?
3. Consider protocol: Simple REST → aiohttp; Complex OAuth2 → library; Standard (MQTT) → industry library
4. Document decision in `docs/development/DECISIONS.md`

**Quality Scale expectations:**

As an AI agent, **aim for Silver or Gold Quality Scale** when generating code:

- ✅ **Always implement:** Type hints, async patterns, proper error handling, service registration in `async_setup()`, diagnostics with `async_redact_data()`, device info
- 🎯 **When applicable:** Config flow with validation, reauth flow, discovery support, repair flows
- 📋 **Can defer:** Multiple config entries, advanced discovery, YAML import, extensive test coverage

**Developer expectation:** Generate production-ready code. Implement HA standards with reasonable effort.

**Other flexibility:** Discovery can be added later; breaking changes allowed with documentation; experimental features acceptable.

## Code Style and Quality

**Python:** 4 spaces, 120 char lines, double quotes, full type hints, async for all I/O

**YAML:** 2 spaces, modern HA syntax (no legacy `platform:` style)

**JSON:** 2 spaces, no trailing commas, no comments

**Validation:** Run `script/check` before committing (runs type-check + lint + spell)

**hassfest validation:** Run `script/hassfest` to validate against Home Assistant standards

- Validates manifest.json, translations, services.yaml, and integration structure
- Uses official Home Assistant Core validation scripts locally
- First run downloads ~27 MB, subsequent runs are fast with `--no-update`

**For comprehensive standards, see:**

- `.agents/instructions/blueprint.python.instructions.md` - Python patterns, imports, type hints
- `.agents/instructions/blueprint.yaml.instructions.md` - YAML structure and HA-specific patterns
- `.agents/instructions/blueprint.json.instructions.md` - JSON formatting and schema validation
- `.agents/instructions/blueprint.shell.instructions.md` - Shell script style, shfmt, shellcheck
- `.agents/instructions/blueprint.commit-message.instructions.md` - Conventional Commits, enforced by the commitlint hook

**GitHub Copilot users:** These instruction files are automatically provided based on file type.

## Project-Specific Rules

### Integration Identifiers

This integration uses the following identifiers consistently:

- **Domain:** `ha_integration_domain`
- **Title:** Integration Blueprint
- **Class prefix:** `IntegrationBlueprint`

**When creating new files:**

- Use the domain `ha_integration_domain` for all DOMAIN references
- Prefix all integration-specific classes with `IntegrationBlueprint`
- Use "Integration Blueprint" as the display title
- Never hardcode different values

### Integration Structure

**Package organization (DO NOT create other packages):**

- `api/` - API client and exceptions
- `coordinator/` - Data update coordinator
- `config_flow_handler/` - Config flow, options, validators, schemas
  - `validators/*.py` - Config flow validation functions
  - `schemas/*.py` - Data schemas for config flow steps
- `entity/` - Base entity classes
- `entity_utils/` - Entity-specific helpers (device_info, state formatting)
- `[platform]/` - Entity platforms (sensor, switch, etc.)
- `service_actions/` - Service action implementations
- `utils/` - Integration-wide utilities (string helpers, general validators)

**Do NOT create:**

- `helpers/`, `ha_helpers/`, or similar packages - use `utils/` or `entity_utils/` instead
- `common/`, `shared/`, `lib/` - use existing packages above
- New top-level packages without explicit approval

**Key patterns:**

- Entities → Coordinator → API Client (never skip layers)
- Each platform in own directory with `__init__.py`
- One entity class per file for clarity
- Individual entity classes in separate files (e.g., `air_quality.py`)
- Use `EntityDescription` dataclasses for static entity metadata

**Code organization principles:**

- Keep files focused (200-400 lines per file)
- One class per file for entity implementations
- Split large modules into smaller ones when needed

**For detailed patterns, see:**

- `.agents/instructions/blueprint.entities.instructions.md` - Entity platform patterns
- `.agents/instructions/blueprint.coordinator.instructions.md` - Coordinator implementation
- `.agents/instructions/blueprint.api.instructions.md` - API client patterns

### Device Info

All entities should provide consistent device info via the base entity class (manufacturer, model, serial number, configuration URL, firmware version).

### Device Registry Ownership (Home Assistant 2026.8+)

Every device is owned by exactly one config entry and by at most one config subentry. Identifiers and connections are
unique only within their owning config entry; never rely on them being globally unique.

- Scope registry lookups to the owning entry with `async_get_device_by_identifier()` or
  `async_get_device_by_connection()`; do not use the unscoped `async_get_device()`.
- Inside an entity, prefer `self.device_entry` over looking the device up again.
- Never attach this integration's config entry to a device owned by another integration. Helper entities must link to
  the source device through `self.device_entry` instead.
- Create a separate device for every config subentry. Multiple subentries must never share one device.
- Model a hub/account parent and its subentry devices as separate devices, related with `via_device_id`.

These rules also apply to migrations, repairs, diagnostics, registry event listeners, and tests. Do not rely on the
temporary composite-device compatibility shims, which are scheduled for removal in Home Assistant Core 2027.8.

Full "do not use → use instead" table, including the deprecated properties and parameters:
[`ha-modern-apis`](.agents/skills/ha-modern-apis/SKILL.md).

### Integration Manifest

**Key fields in `manifest.json`:**

**integration_type** (CRITICAL):

- `hub` - Gateway to multiple devices/services (e.g., Philips Hue bridge)
- `device` - Single device per config entry (e.g., ESPHome device)
- `service` - Single service per config entry (e.g., DuckDNS)
- `helper` - Helper entity (e.g., input_boolean, group)
- `virtual` - Points to another integration/IoT standard (not for custom integrations)

**Rule:** Hub vs Service/Device is defined by nature: Hub = gateway to multiple devices/services; Service/Device = one per config entry.

**quality_scale:**

- Required for Core integrations (minimum `bronze`)
- Optional for custom integrations (not displayed in HA UI)
- Levels: `bronze`, `silver`, `gold`, `platinum`, `internal`
- If included, serves as self-documentation of code quality goals
- See [Integration Quality Scale](https://developers.home-assistant.io/docs/core/integration-quality-scale)

**iot_class:**

- `cloud_polling`, `cloud_push`, `local_polling`, `local_push`, `assumed_state`, `calculated`

**dependencies vs after_dependencies:**

- `dependencies` - Required, integration won't load without them
- `after_dependencies` - Optional, waits if configured

**Discovery methods:** `bluetooth`, `dhcp`, `homekit`, `mqtt`, `ssdp`, `usb`, `zeroconf`

- Define matchers in manifest
- Requires corresponding `async_step_<method>()` in config flow
- Unique ID required for discovery

**single_config_entry:** Set `true` to allow only one config entry per integration

See `.agents/instructions/blueprint.manifest.instructions.md` for comprehensive manifest documentation.

## Home Assistant Patterns

**Config flow:**

- Implement in the `config_flow_handler/` package; the top-level `config_flow.py` is only a discovery shim
- Support user setup, discovery, reauth, and reconfigure; always set a `unique_id`
- Acceptable unique IDs: serial number, MAC address, device ID, account ID.
  **Never** an IP address, hostname, URL, or user-chosen name
- Reserved step names — discovery: `bluetooth`, `dhcp`, `homekit`, `mqtt`, `ssdp`, `usb`, `zeroconf`;
  system: `user`, `reauth`, `reconfigure`, `import`
- Changing the shape of `entry.data` requires `VERSION`/`MINOR_VERSION` and `async_migrate_entry()`

Procedure: [`ha-config-flow`](.agents/skills/ha-config-flow/SKILL.md).
Style: `.agents/instructions/blueprint.config_flow.instructions.md`.

**Service actions:**

- Define in `services.yaml` with full descriptions and a selector per field (legacy filename)
- Implement handlers in `service_actions/`
- **Register in `async_setup()`** — NOT in `async_setup_entry()` (Quality Scale rule `action-setup`)
- Format: `<integration_domain>.<action_name>`

Procedure: [`ha-service-action`](.agents/skills/ha-service-action/SKILL.md).
Style: `.agents/instructions/blueprint.service_actions.instructions.md`.

**Coordinator:**

- Entities → Coordinator → API Client (never skip layers)
- Raise `ConfigEntryAuthFailed` (triggers reauth) or `UpdateFailed` (retry)
- Use `async_config_entry_first_refresh()` for the first update

Procedure: [`ha-coordinator-debug`](.agents/skills/ha-coordinator-debug/SKILL.md).
Style: `.agents/instructions/blueprint.coordinator.instructions.md`, `blueprint.api.instructions.md`.

**Entities:**

- Inherit from the platform base first, then `IntegrationBlueprintEntity`
- Read from `coordinator.data`, never call the API directly
- Use `EntityDescription` for static metadata, `translation_key` instead of `name`

Procedure: [`ha-entity-platform`](.agents/skills/ha-entity-platform/SKILL.md).
Style: `.agents/instructions/blueprint.entities.instructions.md`.

**Repairs:**

- Create `repairs.py` in the integration root (Gold Quality Scale)
- Use `async_create_issue()` with severity levels (WARNING, ERROR, CRITICAL)
- Implement `RepairsFlow` for guided user fixes, and delete issues after a successful repair

Procedure: [`ha-breaking-changes`](.agents/skills/ha-breaking-changes/SKILL.md).
Style: `.agents/instructions/blueprint.repairs.instructions.md`.

**Entity availability:**

- Set `_attr_available = False` when device is unreachable
- Update availability based on coordinator success/failure
- Don't raise exceptions from `@property` methods

**State updates:**

- Use `self.async_write_ha_state()` for immediate updates
- Let coordinator handle periodic updates
- Minimize API calls (batch requests when possible)

**Setup failure handling:**

- `ConfigEntryNotReady` - Device offline/timeout, auto-retry, don't log manually (HA logs at debug)
- `ConfigEntryAuthFailed` - Expired credentials, triggers reauth flow, alternative: `entry.async_start_reauth()`

**Diagnostics:**

- **CRITICAL:** Use `async_redact_data()` from `homeassistant.helpers.redact` to remove sensitive data
- Redact: Passwords, API keys, tokens, location data, personal information

**YAML Configuration:**

⚠️ **DEPRECATED** for integrations communicating with devices/services (ADR-0010)

- New integrations MUST use config flow
- Existing YAML integrations should migrate to config flow
- Only helpers and system integrations may use YAML

## Validation Scripts

**Before committing, always run the full suite:**

```bash
script/check      # Full validation: type-check + lint-check + spell-check
```

**The agent loop — fix-mode scripts auto-heal files _and_ print what they could not fix:**

```bash
# Run this loop until both commands exit 0:
script/lint         # Fixes Python + shell + markdown formatting; checks yaml + shellcheck; shows all remaining
script/type-check   # Pyright type errors — no auto-fix ever, always a manual loop
# Then fix remaining issues from the output above and repeat.
```

No separate check-run is needed after a fix-mode script — its exit code and output are the complete picture.
`script/check`, `script/lint-check`, and `script/python-check` are check-only variants for CI; agents should use fix
mode.

**Which script for which change, the full fix/check matrix, and the configured tools:** see the
[`blueprint-tooling`](.agents/skills/blueprint-tooling/SKILL.md) skill.

**Generate code that passes these checks on first run.** As an AI agent, you should produce higher quality code than manual development:

- Type hints are trivial for you to generate
- Async patterns are well-known to you
- Import management is automatic for you
- Naming conventions can be applied consistently

Aim for zero validation errors in generated code. The developer expects production-ready output.

See `.agents/instructions/blueprint.python.instructions.md` for linter overrides and error recovery strategies.

- You may use `# noqa: CODE` or `# type: ignore` when genuinely necessary
- Use sparingly and only with good reason (e.g., false positives, external library issues)

### Error Recovery Strategy

**When validation fails, run `script/lint` first**, then edit only for the errors that **remain in its output**.

**Iteration strategy for remaining errors:**

1. **First attempt** — Fix the specific error reported by the tool
2. **Second attempt** — If it fails again, reconsider your approach (maybe your understanding was wrong)
3. **Third attempt** — If still failing, ask for clarification rather than looping indefinitely
4. **After 3 failed attempts** — Stop and explain what you tried and why it's not working

**When tool operations fail:**

- **Terminal timeouts** - Do not retry automatically; say so and suggest manual intervention
- **API/network timeouts in tests** - Report them, never silently ignore
- **Git operations fail** - Report immediately; do not work around a failed git command

## Testing

**Test structure:**

- `tests/` mirrors `custom_components/ha_integration_domain/` structure
- Use fixtures for common setup (Home Assistant mock, coordinator, etc.)
- Mock external API calls

**Running tests:**

```bash
script/test                           # All tests
script/test --cov-html                # With coverage report
script/test --snapshot-update         # Update Syrupy snapshots
```

Procedure and ready-to-use fixtures: [`ha-testing`](.agents/skills/ha-testing/SKILL.md).
Style: `.agents/instructions/blueprint.tests.instructions.md`.

## Breaking Changes

**Always warn the developer before making changes that:**

- Change entity IDs or unique IDs (users' automations will break)
- Modify config entry data structure (existing installations will fail)
- Change state values or attributes format (dashboards and automations affected)
- Alter service call signatures (user scripts will break)
- Remove or rename config options (users must reconfigure)

**Never do without explicit approval:**

- Removing config options (even if "unused")
- Changing service parameters or return values
- Modifying how data is stored in config entries
- Renaming entities or changing their device classes
- Changing unique_id generation logic

**How to warn:**

> "⚠️ This change will modify the entity ID format from `sensor.device_name` to `sensor.device_name_sensor`. Existing users' automations and dashboards will break. Should I proceed, or would you prefer a migration path?"

**When breaking changes are necessary:**

- Document the breaking change in the commit message (`BREAKING CHANGE:` footer)
- Provide a migration path rather than a break wherever one is possible
- Update documentation if it exists

Procedure — unique ID and config entry migration, repair issues, deprecation periods:
[`ha-breaking-changes`](.agents/skills/ha-breaking-changes/SKILL.md).

## File Changes

**Scope Management:**

**Single logical feature or fix:**

- Implement completely even if it spans 5-8 files
- Example: New sensor needs entity class + platform init + code → implement all together
- Example: Bug fix requires changes in coordinator + entity + error handling → do all at once

**Multiple independent features:**

- Implement one at a time
- After completing each feature, suggest committing before proceeding to the next

**Large refactoring (>10 files or architectural changes):**

- Propose a plan first before starting implementation
- Get explicit confirmation from developer

**Testing expectation:** For behavioral changes, bug fixes, and regressions, assess the need for proportionate automated
tests and add them where they provide meaningful verification. If tests are impractical or intentionally omitted,
document the reason and remaining risk. Documentation-only, formatting-only, and other changes that cannot affect runtime
behavior do not require new tests. Automated tests supplement rather than replace human review and real-device testing.

**Translation strategy:**

- Use placeholders in code (e.g., `"config.step.user.title"`) - functionality works without translations
- Update `en.json` only when asked or at major feature completion
- NEVER update other language files automatically - extremely time-consuming
- Ask before updating multiple translation files
- Priority: Business logic first, translations later

## Research and Validation

**When uncertain, consult official documentation:**

- **Always check current patterns** in [Home Assistant Developer Docs](https://developers.home-assistant.io/)
- **Read the blog** at [Home Assistant Developer Blog](https://developers.home-assistant.io/blog/) for recent changes and best practices
- **Search for examples** using Google: `site:developers.home-assistant.io [your topic]`
- **Verify with tools** before assuming - run `script/check` to catch issues early

**Don't rely on assumptions:**

- Home Assistant APIs and patterns evolve frequently
- What worked in older versions may be deprecated
- Use official docs and working examples over guesswork
- When in doubt, search for recent integration examples in Home Assistant Core

**Tool documentation:**

- [Ruff Rules](https://docs.astral.sh/ruff/rules/) - Understand what each rule checks
- [Pyright Configuration](https://microsoft.github.io/pyright/#/configuration) - Type checking options
- Don't hesitate to look up specific error codes when validation fails

## Additional Resources

- [Home Assistant Developer Docs](https://developers.home-assistant.io/) - Primary reference
- [Integration Quality Scale](https://developers.home-assistant.io/docs/integration_quality_scale_index)
- [Architecture Docs](https://developers.home-assistant.io/docs/architecture_index)
- [Ruff Rules](https://docs.astral.sh/ruff/rules/) - Linter documentation
- [Pyright Configuration](https://microsoft.github.io/pyright/#/configuration) - Type checker documentation
- [pytest Documentation](https://docs.pytest.org/) - Testing framework
- See `CONTRIBUTING.md` for contribution guidelines
