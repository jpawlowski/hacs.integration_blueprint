---
name: ha-quality-review
description: >-
  Perform a structured quality review of this Home Assistant custom integration, either as a full audit or scoped
  to a diff. Use when asked to "review the integration", "audit the code", "check quality scale", "are we
  bronze/silver/gold", "is this ready to release", "review my changes", "what's missing before publishing", or
  before opening a pull request that touches integration code. Covers running the automated gates first, then
  auditing architecture, the Integration Quality Scale rules, error handling, security, performance, user
  experience, and documentation — and reporting findings ranked by severity with concrete fixes. SYMPTOMS — load
  this if you are about to: report a review that only restates linter output; claim real-device testing that did
  not happen; give a finding without a file path and a fix; or judge quality without running `script/hassfest` and
  the test suite first.
---

# Review the integration

A review that only restates the linter is worthless. Run the machines first, then spend your attention on what they
cannot see: layering, failure behaviour, and whether a user would understand what this integration does.

## 0. Scope the review

Ask, or infer from the request:

- **Full audit** of the integration, or **diff review** of the current branch?
- Is there a target tier (this project aims for Silver, ideally Gold)?

For a diff review: `git diff main...HEAD --stat`, then read the changed files in full — not just the hunks.

## 1. Automated gates (always first)

```bash
script/lint          # ruff format+fix, shfmt, prettier/markdownlint, yamllint, zizmor, shellcheck
script/type-check    # pyright — never auto-fixed
script/hassfest      # manifest, services.yaml, translations, integration structure
script/test --cov-html
```

Anything these report is a finding, not something to fix silently mid-review — but do note that `script/lint` already
auto-heals formatting, so only its **remaining** output counts.

## 2. Architecture

- Layering is Entity → Coordinator → source. Any entity importing `api/` directly, or any coordinator holding HTTP
  details, is a finding.
- Package structure matches the fixed set (`api/`, `coordinator/`, `config_flow_handler/`, `entity/`, `entity_utils/`,
  `<platform>/`, `service_actions/`, `utils/`). A `helpers/`, `common/`, `shared/`, or `lib/` package is a finding.
- Files are 200–400 lines, one entity class per file.
- Runtime state lives in `entry.runtime_data`, never `hass.data[DOMAIN]`.
- No circular imports; `TYPE_CHECKING` guards for type-only imports.

**Two upstream requirements this project deliberately does not meet.** Neither is a finding here, and both should be
stated as decisions rather than silently passed over:

- Core requires all device or service communication to be wrapped in a PyPI library. As a custom integration this
  project allows an in-repo client (`AGENTS.md` § Custom Integration Flexibility) — with the consequence that the
  client would have to be extracted before this could ever be submitted to Core.
- `creating_component_code_review.md` still recommends `hass.data[DOMAIN]`. That page is out of date and is
  contradicted by the Bronze `runtime-data` rule. Do not "correct" `entry.runtime_data` back to it.

## 3. Quality scale audit

| File                                                                     | When to read                                                                      |
| ------------------------------------------------------------------------ | --------------------------------------------------------------------------------- |
| [`references/quality-scale-rules.md`](references/quality-scale-rules.md) | Auditing a tier. All 54 rule identifiers with one-line criteria, grouped by tier. |

Walk the rules for the target tier and report each as **pass / fail / not applicable**. For every fail, name the file
and the fix.

The rules most often missed in this codebase's shape:

- `action-setup` — actions registered in `async_setup()`, not per entry.
- `parallel-updates` — every platform module re-exports `PARALLEL_UPDATES`.
- `entity-translations` / `icon-translations` — no hardcoded `name=` or `icon=` in `EntityDescription`.
- `exception-translations` — no English strings inside raised exceptions.
- `log-when-unavailable` — the coordinator must not log on every failed poll.
- `entity-category` / `entity-disabled-by-default` — diagnostics entities are marked and often disabled by default.
- `stale-devices` / `dynamic-devices` — devices appear and disappear with upstream reality.

## 4. Code quality

| File                                                               | When to read                                                                                                                            |
| ------------------------------------------------------------------ | --------------------------------------------------------------------------------------------------------------------------------------- |
| [`references/core-lint-checks.md`](references/core-lint-checks.md) | Any review of integration code. The integration-specific checks Home Assistant Core lints in its own CI and this repository cannot run. |

Look for the failure modes linters miss:

- **Typing** — full annotations, `-> None` on procedures, no bare `Any` where a `TypedDict` or dataclass is meant,
  no `from __future__ import annotations` (banned on Python 3.14).
- **Async** — no blocking I/O in the event loop (`requests`, `open()`, `time.sleep`, sync SDK calls); every network call
  has a timeout; `asyncio.timeout` rather than a deprecated helper.
- **Exceptions** — specific types, never bare `except:`; `raise ... from err` to preserve the chain; the coordinator
  translates client exceptions into `UpdateFailed` / `ConfigEntryAuthFailed` correctly.
- **Properties** — no I/O, no raising, no side effects.
- **Constants** — no magic numbers or duplicated strings; reuse `homeassistant.const` names.
- **Logging** — lazy `%s` formatting, `debug` for the normal path, no secrets in any log line at any level.

## 5. Security

- Credentials only in `entry.data`, never in `entry.options`, the entry title, logs, or diagnostics. Separately from
  that security rule, `config-flow` requires the whole split to be right: everything needed to establish the
  connection belongs in `entry.data`, everything else in `entry.options`. A host stored in `options` passes the
  credential check and still fails the rule.
- `diagnostics.py` runs everything through `async_redact_data()` with a `TO_REDACT` set that actually covers the
  payload — re-check it whenever the API response shape changes.
- TLS verification is never disabled, and no secret has a default value in a schema.
- Dependencies are pinned in both `manifest.json` and `requirements.txt`, and the two agree.

## 6. Performance

- One coordinator poll serves all entities; no per-entity API calls.
- Interval appropriate for the source (local ~30 s, cloud ~5–15 min) and user-configurable.
- No unnecessary `async_write_ha_state()`; no work in `__init__`.
- Data structures let entities read by key rather than scanning lists.

## 7. User experience

- Config flow validates before creating the entry and shows recoverable, translated errors.
- Entity names read well in the UI with `has_entity_name` (no repeated device name).
- Units, device classes, and state classes are set so history and statistics work.
- Failures surface as repair issues or reauth flows rather than silent unavailability.
- For an integration that depends on a remote endpoint, consider `system_health.py`: a `@callback async_register`
  that calls `register.async_register_info(...)`, whose info callback returns a dict whose values may be coroutines
  (the frontend shows a spinner and resolves them). `system_health.async_check_can_reach_url(hass, ENDPOINT)` covers
  the common case, and every key needs a `system_health.info.<key>` translation. It turns "it is broken" into
  "the API is unreachable" on the user's own system page.

## 8. Documentation and release hygiene

- `README.md`, `docs/user/` describe what actually exists — not the blueprint's placeholder text.
- `manifest.json`: correct `integration_type`, `iot_class`, `documentation`, `issue_tracker`, `codeowners`, `version`.
- Architectural choices worth remembering are in `docs/development/DECISIONS.md`
  ([`ha-planning`](../ha-planning/SKILL.md)).
- Breaking changes carry a migration path ([`ha-breaking-changes`](../ha-breaking-changes/SKILL.md)).

## Report format

Rank by severity and be specific. A finding without a file path and a fix is noise.

```markdown
## Summary

<2–3 sentences: overall state, current effective tier, biggest risk.>

## Critical — must fix before release

### 1. <Title>

- **Where:** `custom_components/<domain>/coordinator/base.py:82`
- **Problem:** <what is wrong and what it breaks for a user>
- **Fix:** <concrete change>

## Warnings — should fix

## Suggestions — nice to have

## Quality scale

| Tier | Status | Failing rules |
| ---- | ------ | ------------- |

## Verified

<What you actually ran, and what you could not verify — e.g. no real device available.>
```

Be honest in the last section. Do not describe checks you did not run, and do not imply real-device testing happened
when it did not — that is an explicit rule of this project's [`AI_POLICY.md`](../../../AI_POLICY.md).

## After the review

Report findings; do not silently fix them unless the developer asked for fixes. If they did, fix in severity order, run
`script/lint && script/type-check && script/test` after each group, and state what you changed.
