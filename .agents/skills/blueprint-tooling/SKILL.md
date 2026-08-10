---
name: blueprint-tooling
description: >-
  Use this repository's development tooling correctly — the script/ validation and formatting commands, the
  fix-versus-check distinction, hassfest, adding a Python dependency in both manifest.json and requirements.txt,
  extending scripts with pre/post hook scripts, devcontainer environment variables, and template sync from the
  upstream blueprint. Use when asked to "run the checks", "fix the lint errors", "why is CI failing", "add a
  dependency", "add a package", "add a hook", "customize the setup", "exclude a file from template sync", or when
  a validation command fails and you need to know which script to reach for. SYMPTOMS — load this if you are about
  to: run `ruff`, `pyright`, `pytest`, or `hass` directly instead of the project script; run a `-check` script
  after a fix script; add a dependency to only one of `manifest.json` and `requirements.txt`; or edit a
  template-managed script instead of adding a hook.
---

# Repository tooling

## Rule zero: use the project scripts

Never craft your own `hass`, `pip`, `pytest`, `ruff`, or `pyright` invocation. The scripts activate the right virtual
environment, set `PYTHONPATH`, manage ports and processes, and run hooks. Agents that bypass them break in ways that
look like code bugs.

## Which script to run

Pick the narrowest one that covers what you changed:

| Changed files                            | Run                                   |
| ---------------------------------------- | ------------------------------------- |
| `*.py` only                              | `script/python` + `script/type-check` |
| `*.yaml` / `*.yml` only                  | `script/yaml-check`                   |
| `*.md` only                              | `script/markdown`                     |
| `script/` or `.devcontainer/*.sh` only   | `script/shell` + `script/shell-check` |
| Multiple types, or unsure                | `script/lint` + `script/type-check`   |
| Integration metadata, translations, YAML | `script/hassfest`                     |

### Fix mode vs. check mode

**Fix-mode scripts auto-heal files _and_ print what they could not fix.** Their output is the complete picture — there
is no need to run the matching `-check` script afterwards.

```bash
# Loop until both exit 0:
script/lint         # formats Python, shell, markdown; checks yaml + shellcheck; reports the rest
script/type-check   # pyright — never auto-fixes, always a manual loop
```

| Fix mode          | Check mode (read-only, for CI)                                                                                  |
| ----------------- | --------------------------------------------------------------------------------------------------------------- |
| `script/lint`     | `script/lint-check`                                                                                             |
| `script/python`   | `script/python-check`                                                                                           |
| `script/shell`    | `script/shell-check`                                                                                            |
| `script/markdown` | `script/markdown-check`                                                                                         |
| `script/spell`    | `script/spell-check`                                                                                            |
| —                 | `script/check` (type-check + lint-check + spell-check), `script/yaml-check`, `script/type-check`, `script/test` |

Agents should use fix mode. `script/check` is the gate to run before saying a task is complete.

### Other scripts

```bash
script/develop           # take over Home Assistant on :8123, debugpy on :5678 (see below)
script/ha                # query and control the running instance (see below)
script/setup/seed-auth   # mint the token script/ha uses — run by script/develop
script/hassfest          # official HA validation (first run downloads ~27 MB)
script/test              # pytest
script/skills-check      # validate .agents/skills/ (also part of lint / lint-check)
script/version           # read the canonical version from manifest.json
script/ha-version-sync   # align the pinned Home Assistant version across config files
script/clean             # remove caches, logs, build artifacts
script/help              # list every script with its description
```

`script/develop` **kills any Home Assistant already bound to `config/` and starts its own.** That is deliberate — the
log has to stream into the terminal that launched it — but it means running it is a takeover, not a "start if needed".
Whoever was watching the previous instance loses their live log. Check `script/ha status` first and use the instance
that is already there.

### Talking to the running instance

`script/ha` reads entity states, config entry status, diagnostics, and the error log from the instance
`script/develop` started, calls service actions, and drives config flows — so debugging does not require reading a log
file and asking a human to click through the UI.

```bash
script/ha entries                                  # config entry state and failure reason
script/ha states                                   # this integration's entities
script/ha diagnostics | jq .                       # no UI download step
script/ha logs --level error
script/ha loglevel custom_components.<domain>=debug   # immediate, no restart
```

Authentication is automatic: `script/develop` runs `script/setup/seed-auth`, which mints a long-lived access token
offline into `config/.storage/dev_access_token`. `script/ha` reads that file itself, so **the token never appears in a
command line or in output**. On a fresh environment the instance has to be onboarded in the browser once; the token
then appears on the next `script/develop`.

### When a check keeps failing

1. Fix the specific error the tool reported.
2. If it fails again, question your understanding rather than repeating the same edit.
3. After three attempts, stop and explain what you tried and what the tool said.

`# noqa: CODE` and `# type: ignore[code]` are allowed for genuine false positives or third-party gaps — always with a
specific code, never bare, and sparingly.

## Adding a Python dependency

The integration's runtime dependencies live in **two** places that must be kept in sync by hand. This is a Home
Assistant design constraint, not a repository quirk.

1. `custom_components/<domain>/manifest.json` → `requirements` — the authoritative list. Home Assistant
   reads it and installs the packages for end users.
2. `requirements.txt` at the repository root — the development mirror, so pytest, pyright, and your editor resolve the
   same imports.
3. `script/setup/bootstrap` (or a container rebuild) to install it.

Pin versions in both, and keep them identical.

| File                     | Template sync  | Contents                                         |
| ------------------------ | -------------- | ------------------------------------------------ |
| `requirements.txt`       | ❌ excluded    | your integration's runtime dependencies          |
| `requirements_dev.txt`   | ✅ synced      | shared development tooling — do not add app deps |
| `requirements_test.txt`  | ✅ synced      | shared test dependencies                         |
| `requirements.local.txt` | — (gitignored) | your personal extras (`ipdb`, profilers, …)      |

Before adding a dependency at all, decide whether you want it: the criteria are in
[`blueprint.api.instructions.md`](../../instructions/blueprint.api.instructions.md), and the choice belongs
in `docs/development/DECISIONS.md` ([`ha-planning`](../ha-planning/SKILL.md)).

## Extending the scripts with hooks

Every script supports sourced `pre` and `post` hook scripts under `script/hooks/` and `.devcontainer/hooks/`. Use them
instead of editing the template-managed scripts themselves — hook directories are excluded from template sync, the
scripts are not.

| File                                           | When to read                                                                                                                                                    |
| ---------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [`references/hooks.md`](references/hooks.md)   | Adding or debugging a hook. Naming convention, the complete pre/post hook table for every script, worked examples, and the rules that apply to sourced scripts. |
| [`references/ha-cli.md`](references/ha-cli.md) | Using `script/ha`. Every command with its options, the token lifecycle, exit codes, and driving config flows from the terminal.                                 |

## Devcontainer environment

Two layers, both sourced by the lifecycle scripts:

| File                       | Committed          | Purpose                        |
| -------------------------- | ------------------ | ------------------------------ |
| `.devcontainer/.env`       | ✅ yes             | project defaults for everyone  |
| `.devcontainer/.env.local` | ❌ no (gitignored) | personal overrides, always win |

| Variable          | Default                  | Effect                                                    |
| ----------------- | ------------------------ | --------------------------------------------------------- |
| `HA_VERSION`      | version from `hacs.json` | `latest`, `beta`, `YEAR.MONTH`, or an exact version       |
| `HA_INSTALL_HACS` | `1`                      | `0` skips the HACS install and speeds up first-time setup |
| `APT_UPDATE`      | `0`                      | `1` runs `apt-get update && upgrade` during setup         |

Changes require **Dev Containers: Rebuild Container**. These files are not visible to devcontainer _features_ or
`containerEnv` — those are set at image build time and must be edited in `devcontainer.json`.

Scripts under `script/` read the **process** environment and do not source these files. Variables that steer them are
therefore set in a hook — `script/hooks/develop.pre.sh` for anything `script/develop` runs:

| Variable            | Default                 | Effect                                              |
| ------------------- | ----------------------- | --------------------------------------------------- |
| `HA_DEV_TOKEN`      | `1`                     | `0` skips minting the `script/ha` token entirely    |
| `HA_DEV_TOKEN_DAYS` | `30`                    | token lifetime; it rotates once under 7 days remain |
| `HA_URL`            | `http://127.0.0.1:8123` | which instance `script/ha` talks to                 |
| `HA_TOKEN`          | the seeded token file   | authenticate `script/ha` as someone else            |

## Template sync

A weekly workflow opens a pull request with upstream blueprint changes. It uses `-X theirs`, so **the template version
wins** on any file both sides changed — the PR is always mergeable, and the diff shows your version being replaced.
Review before merging.

- To permanently own a file, add it to `.templatesyncignore` (gitignore glob syntax). Do that rather than resolving the
  same conflict every week.
- Do not add generated or personal files — untracked files are never touched by sync anyway.
- Workflow files under `.github/workflows/` only sync when a `TEMPLATE_SYNC_TARGET_PAT` secret with `workflows: write`
  exists; otherwise those updates are skipped with a notice in the run summary.

Background, recovery procedures, and the default exclusion list are in
[`docs/development/CUSTOMIZATION.md`](../../../docs/development/CUSTOMIZATION.md).
