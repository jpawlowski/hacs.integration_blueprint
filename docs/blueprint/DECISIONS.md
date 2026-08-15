# Blueprint Design Decisions

Architectural decisions about **the template itself** — its tooling, its scripts, its conventions. Decisions about an
integration built from the blueprint belong in [`docs/development/DECISIONS.md`](../development/DECISIONS.md) instead;
the boundary is described in [`README.md`](README.md).

Each entry records the context that forced the decision, what was decided, why that option won, and what it costs. An
entry that cannot state a cost is usually not a decision worth recording.

---

## Decision Log

### Mint the Development Access Token Offline, Through Home Assistant's Own AuthManager

**Date:** 2026-08-10

**Context:** Anything that wants to read the development instance — `script/ha`, an AI coding agent, a throwaway script — needs an access token. Creating one by hand in _Settings → Security → Long-lived access tokens_ makes every fresh environment depend on a human, and `script/setup/reset` wipes it again.

**Decision:** `script/setup/seed-auth` boots Home Assistant's own `AuthManager` against the **stopped** config directory, the way `homeassistant/scripts/auth.py` does, and lets it write `config/.storage/auth`. The token lands in `config/.storage/dev_access_token` (mode `0600`), rotating automatically once fewer than 7 days of its 30-day life remain.

**Rationale:**

- Works on an already-onboarded instance without knowing the password, unlike the live `/api/onboarding/users` → `/auth/token` route.
- Home Assistant writes the store, so the schema, the JWT claim set, atomicity, and file mode stay its responsibility across version bumps. This deliberately diverges from `script/setup/seed-http-config`, which hand-crafts its store only because the `http` store has no equivalent API.
- The token file is read by `script/ha` itself, so no credential enters a command line, an environment variable, or an agent's context.

**Consequences:**

- **Home Assistant must be stopped.** `AuthStore.async_load()` schedules an unconditional save 300 s after boot that rewrites the whole store from memory, so a token injected into a running instance is silently discarded. `seed-auth` takes Home Assistant's own `.ha_run.lock` for the whole operation, which makes the race impossible in both directions.
- `hass.async_stop(force=True)` is required to flush: a freshly constructed `HomeAssistant` sits in `CoreState.not_running`, where the unforced `async_stop()` returns early without firing `EVENT_HOMEASSISTANT_FINAL_WRITE`.
- A Home Assistant **admin** credential exists in the devcontainer, which is effectively code execution inside it. Mitigated by the short lifespan, `0600`, a gitignored and sync-excluded location, redacted CLI output, and read-deny rules for Claude Code.
- On a fresh environment the browser onboarding still has to happen once; the token appears on the **second** `script/develop`.

---

### Own Development CLI Instead of `homeassistant-cli`

**Date:** 2026-08-10

**Context:** `script/ha` overlaps with [`homeassistant-cli`](https://github.com/home-assistant-ecosystem/home-assistant-cli) (`hass-cli`), which reached 1.0.0 in April 2026 and covers states, services, templates, config entries, and a `raw` escape hatch.

**Decision:** Keep an in-repo CLI with no third-party dependency; `aiohttp` is already in the Home Assistant venv.

**Rationale:** Evaluated against this devcontainer at HA 2026.8 / Python 3.14:

- Every WebSocket-backed `hass-cli` command (`entity list`, `device list`, `area list`, `event watch`, `raw ws`) fails with `RuntimeError: There is no current event loop` — `asyncio.get_event_loop()` at `remote.py:152`, removed behaviour in Python 3.12+.
- Its bounds `packaging<26.0` and `regex<2025.0.0` conflict with the venv's 26.3 and 2026.7.19, so installing it **downgrades two packages in the venv Home Assistant itself runs from**. It would need its own venv and a wrapper.
- It has no diagnostics download, no config/options/reconfigure flow driving, no `reason` on a config entry, no structured `system_log/list`, and no scoping to this repository's domain — the things integration development specifically needs.
- It solves none of the token problem, so `script/setup/seed-auth` is required either way.

**Consequences:** This repository owns the CLI's maintenance, including tracking Home Assistant API changes. The endpoints it uses are the ones the frontend uses, which makes them unlikely to move quietly. Should `hass-cli` fix the Python 3.14 bug and relax its pins, this is worth revisiting.

---

### Synchronize Static Architecture Guardrails with the Tooling

**Date:** 2026-08-15

**Context:** Some project rules describe recognizable source patterns rather than runtime behaviour: an
`EntityDescription` with a hardcoded `name=` or `icon=`, a frozen device-automation platform file, or an unscoped
device-registry lookup. The integration tests under `tests/` cannot carry these checks forward: that directory is
excluded by `.templatesyncignore` because initialization makes its imports domain-specific.

**Decision:** Keep a conservative AST-based checker in `script/.lib/architecture_check.py`, expose it through
`script/architecture-check`, and run it from `script/lint` and `script/lint-check`. Discover tracked and untracked,
non-ignored integration sources with `git ls-files --cached --others --exclude-standard -z --
custom_components/*.py`. Keep the checker's regression tests in synchronized `script/tests/`, which `script/test`
also collects.

**Rationale:**

- `script/` is template-managed except for `script/hooks/`, so checker fixes and their tests are proposed together in
  downstream template-sync pull requests.
- AST inspection is more precise than text matching while requiring neither Home Assistant startup nor a domain- or
  class-prefix-specific test.
- The checker follows import aliases, local subclasses, literal dictionary unpacking, and known `DeviceRegistry`
  provenance. It does not reject an unrelated API client merely because it also defines `async_get_device()`.
- Ruff has no supported repository-local custom-rule interface; adding another lint framework would cost more than
  this small, dependency-free checker.

**Consequences:**

- The checker is a guardrail, not proof of the architecture. General `**kwargs`, factories, and values assembled by
  arbitrary data flow remain review concerns.
- Runtime behaviour still belongs in the domain-specific `tests/` suite; `script/tests/` is only for synchronized
  development tooling.
- Downstream repositories receive these changes only after their template-sync workflow opens a pull request and a
  maintainer merges it.
- New rules belong here only when they can be expressed conservatively with a low false-positive rate.

---
