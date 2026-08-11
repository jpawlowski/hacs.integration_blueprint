---
name: ha-modern-apis
description: >-
  Verify that Home Assistant APIs used in this custom integration are current, and replace deprecated ones. Use
  when a DeprecationWarning or "will be removed in HA Core X.Y" appears in logs or tests, when tests fail because
  warnings are errors, when asked to "modernize", "update to the latest HA version", "fix deprecations", "is this
  still the right API", "bump the HA version", or before copying a pattern from an older integration, blog post,
  or model memory. Covers checking the installed Home Assistant source instead of guessing, the device
  registry single-owner rules from 2026.8, runtime_data, config flow helpers, entity metadata, async I/O, and the
  version bump procedure. SYMPTOMS — load this if you are about to: write `hass.data[DOMAIN]` instead of
  `runtime_data`; call the unscoped `async_get_device()`; use `FlowResult`, `DEVICE_CLASS_*`, or `async_timeout`;
  create your own aiohttp session; add a warning filter to make a deprecation go away; or adopt an undocumented API
  or config key on an issue's say-so.
---

# Keep the integration on current Home Assistant APIs

Home Assistant changes fast enough that any pattern remembered from training data or copied from a blog post is suspect.
This skill exists because the most common failure mode is confidently writing a 2023 API.

## The rule: check the source, do not recall

The devcontainer has the exact Home Assistant version this integration is developed against. It is the authority.

```bash
# Which version are we on?
.venv/bin/python -c "from homeassistant.const import __version__; print(__version__)"

# Does this API still exist, and is it deprecated?
rg -n "def async_get_device_by_identifier" .venv/lib/python*/site-packages/homeassistant/helpers/device_registry.py
rg -n "deprecated|breaks_in_ha_version" .venv/lib/python*/site-packages/homeassistant/helpers/update_coordinator.py

# How do current core integrations do it?
rg -n "runtime_data" .venv/lib/python*/site-packages/homeassistant/components/<similar_integration>/
```

`breaks_in_ha_version=` in a `@deprecated_function` decorator tells you the actual removal deadline. Prefer that over
any secondary source.

When the installed source is not enough — a pattern that is new rather than deprecated — check
<https://developers.home-assistant.io/blog/> before implementing.

## The same rule, generalised: what counts as verified

This applies to any API, tool or configuration key you are about to commit to. Only a **primary** source settles a
question — the installed source you import, or the current documentation of the tool you are configuring. A GitHub
issue, a blog post, another tool's convention and your own recall are leads, never answers.

Two traps make a secondary source feel primary:

- **Silent failure.** Most configuration rejects nothing: an unknown key is ignored, and the resulting default often
  looks like success. Before believing "X works", ask what a broken X would look like — if the answer is "the same
  thing", the observation proved nothing. Test the case that can fail: the file that should _not_ match, the entry
  that should _not_ load.
- **A key that belongs to a neighbouring tool.** Copilot, Cursor and Claude Code each name the same idea differently
  (`applyTo`, `globs`, `paths`). That a key works in one tool is no evidence for the next, and the wrong one will not
  complain.

When you deviate from documented behaviour, the bar is: name the primary source you checked, and design an observation
that could have come out the other way. If neither is possible, follow the documentation and say you could not verify
it. When the answer matters enough to encode, put a check in `script/` rather than a comment.

## Reference files

| File                                                       | When to read                                                                                                                                                                                                                                         |
| ---------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [`references/deprecations.md`](references/deprecations.md) | Fixing a specific deprecation. Full "do not use → use instead" tables for the device registry (2026.8 single ownership), config entry runtime state, config flow helpers, entity metadata, async and I/O, diagnostics, and 2026 behavioural changes. |

Read it when you have a concrete symbol to replace — do not pull it into context speculatively.

## The three that matter most in this codebase

**1. Device registry single ownership (2026.8).** A device belongs to exactly one config entry and at most one
subentry. Identifiers are unique only within their owning entry. Always scope lookups:

```python
device = device_registry.async_get_device_by_identifier((DOMAIN, serial), entry.entry_id)
```

Never the unscoped `async_get_device()` — with two entries sharing an identifier it resolves ambiguously.

**2. Typed `runtime_data`.** State belongs on the entry, not in `hass.data`:

```python
type {ClassPrefix}ConfigEntry = ConfigEntry[{ClassPrefix}Data]
entry.runtime_data = {ClassPrefix}Data(client=client, coordinator=coordinator, integration=integration)
```

**3. Warnings are errors in tests.** `pyproject.toml` sets `filterwarnings = ["error"]`, so a `DeprecationWarning`
fails `script/test`. That is the intended early-warning system. Fix the deprecation; add an ignore only when an upstream
library gives you no alternative, and comment why.

## Fixing a deprecation warning

1. Read the warning — it names the symbol, and usually the replacement and the removal version.
2. Confirm the replacement's real signature in the installed source. Signatures shift between the announcement and the
   release.
3. Replace every occurrence, including tests, diagnostics, repairs, and migrations. A half-migrated codebase is worse
   than an un-migrated one.
4. `script/lint && script/type-check && script/test`, then restart Home Assistant and confirm the warning is gone from
   `config/home-assistant.log`.

## Bumping the Home Assistant version

```bash
script/ha-version-sync        # keeps hacs.json, .devcontainer/.env and friends aligned
```

Then rebuild the container (or re-run `script/setup/bootstrap`), and:

```bash
script/hassfest && script/test
rg -n "DeprecationWarning|will be removed" config/home-assistant.log
```

Bumping the minimum HA version in `hacs.json` / `manifest.json` drops support for older installs — that is a breaking
change for users. See [`ha-breaking-changes`](../ha-breaking-changes/SKILL.md).

## Do not

- Do not "fix" a deprecation by suppressing the warning.
- Do not adopt a brand-new API before the version in `hacs.json` supports it — users on the minimum version will break.
- Do not trust an example from an older Home Assistant release, a Stack Overflow answer, or your own recall without
  checking the installed source first.
