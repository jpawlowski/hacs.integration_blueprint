# Customization & Extensibility

This document explains how to customize and extend the blueprint without modifying files that are managed by the upstream template.

## Template Sync

Repositories created from this blueprint can receive upstream improvements automatically via a weekly pull request created by the [template sync workflow](../../.github/workflows/template-sync.yml).

### How it works

Every Monday at 07:00 UTC, the workflow checks whether the upstream blueprint (`jpawlowski/hacs.integration_blueprint`) has new commits. If it does, it opens a pull request with the diff against your repository.

You review the PR and merge anything you want to adopt. Changes you don't want can simply be dismissed or partially merged.

### How conflicts are handled

The sync workflow uses `-X theirs` when preparing the PR branch — **the template version always wins** when both you and upstream changed the same file. The PR is always clean and mergeable; there are no conflict markers to resolve.

In practice:

- If a synced file changed both locally and upstream, the PR diff shows your changes being replaced by the template version.
- If you changed a synced file that upstream did not touch, the PR contains nothing for that file — your local changes are unaffected.

Review the PR diff before merging. If it would overwrite something you want to keep, close the PR and manually apply the changes you actually want.

### Modifying synced files locally

You can freely modify any synced file. Template sync only affects a file if it changed upstream since the last sync — a file you changed locally but that upstream did not touch is never overwritten.

When the same file changes on both sides, the sync PR replaces your version with the template version. Two strategies:

**Option A — Exclude the file permanently:** Add it to [`.templatesyncignore`](../../.templatesyncignore). The sync workflow then skips it entirely. Use this when you fully own the file's content and don't want upstream changes (for example `requirements.txt` for your integration's dependencies).

**Option B — Handle conflicts case by case:** Review the PR diff before merging. If the PR would overwrite a local change you want to keep, edit the file on the PR branch first — then merge.

**Via GitHub web UI (no command line needed):** Open the PR → _Files changed_ → click `…` next to the file → _Edit file_. The online editor opens on the PR branch. Blend in the upstream changes you want, keep what you want to preserve, and commit directly to the PR branch. Then merge the PR as normal.

**Via VS Code:** Check out the PR branch with `gh pr checkout <number>`, open the file in VS Code, edit to blend the changes, commit, and merge.

**After an accidental merge (recovery):** If you merged before reviewing and lost a local change, you can restore it from the commit before the merge:

```bash
git show HEAD~1:path/to/your-file.ext > path/to/your-file.ext
git commit -m "chore: restore local changes after template sync"
```

> [!TIP]
> If you find yourself editing the same file after every sync PR, switch to Option A and add it to `.templatesyncignore`.

### Excluding files from sync

Files listed in [`.templatesyncignore`](../../.templatesyncignore) are never touched by the sync PR, even if they changed upstream.

The syntax follows `.gitignore` glob patterns. To exclude an additional file or directory, add a line:

```text
# My integration-specific overrides
config/
path/to/my-file.json
```

Files already excluded by default:

| Path                                                                           | Reason                                                                   |
| ------------------------------------------------------------------------------ | ------------------------------------------------------------------------ |
| `custom_components/`                                                           | Your integration code                                                    |
| `tests/`                                                                       | Test files reference your domain (set by `initialize.sh`)                |
| `pyproject.toml`                                                               | Contains your domain in package metadata                                 |
| `.yamllint.yml`                                                                | Contains your domain in configuration comment                            |
| `.pre-commit-config.yaml`                                                      | Contains your domain in file-match patterns                              |
| `requirements.txt`                                                             | Your integration's PyPI dependencies (managed alongside `manifest.json`) |
| `.vscode/launch.json`, `.vscode/tasks.json`                                    | Contain your domain in debugger/task arguments                           |
| `README.md`, `LICENSE`, etc.                                                   | Replaced by `initialize.sh`                                              |
| `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`, `.github/copilot-instructions.md`       | Contain domain-specific references                                       |
| `.github/CODEOWNERS`, `.github/FUNDING.yml`, `.github/COPILOT_CODING_AGENT.md` | Per-project GitHub settings                                              |
| `config/`                                                                      | Local HA instance (credentials, test data)                               |
| `docs/`                                                                        | Your project documentation                                               |
| `script/hooks/`, `.devcontainer/hooks/`                                        | Your hook scripts                                                        |
| `.devcontainer/.env`                                                           | Your HA_VERSION pin and DevContainer settings                            |
| `release-please-config.json`, `.release-please-manifest.json`                  | Release management                                                       |
| `.github/workflows/template-sync.yml`                                          | Sync workflow itself                                                     |
| `uv.lock`                                                                      | Your pinned dependency lockfile                                          |

> [!TIP]
> If a file keeps causing conflicts in every sync PR, add it to `.templatesyncignore` instead of resolving the conflict every week.

### Opting out of template sync entirely

If you don't want automatic update PRs at all, simply delete the two files:

```bash
rm .github/workflows/template-sync.yml
rm .templatesyncignore
```

That's it. No workflow runs, no PRs, no noise. You can still pull upstream changes manually at any time by comparing your repository against `jpawlowski/hacs.integration_blueprint`.

---

## Hook Scripts

Every development script supports **pre** and **post** hook scripts. Hooks are plain shell scripts that are sourced into the calling script's environment, so they can read and set variables, call functions already defined in the script, and produce output using the same formatting helpers.

### Where hooks live

```text
script/hooks/          # Hooks for scripts in script/
├── lint.pre.sh        # Runs before script/lint
├── lint.post.sh       # Runs after script/lint
├── test.pre.sh        # Runs before script/test
├── test.post.sh       # Runs after script/test
├── setup/
│   ├── bootstrap.pre.sh
│   ├── bootstrap.post.sh
│   └── ...
└── ...

.devcontainer/hooks/   # Hooks for .devcontainer/ scripts
├── setup-shell.pre.sh
├── setup-shell.post.sh
├── setup-git.pre.sh
├── setup-git.post.sh
└── post-attach.post.sh
```

Both directories are listed in `.templatesyncignore` and are never touched by template sync.

### Naming convention

```text
script/hooks/<script-name>.<phase>.sh
```

- `<script-name>` mirrors the script path relative to `script/` (e.g. `setup/bootstrap` for `script/setup/bootstrap`)
- `<phase>` is either `pre` or `post`

For `.devcontainer/` scripts the same pattern applies under `.devcontainer/hooks/`.

### Available hooks

| Script                            | pre hook                                    | post hook                                    |
| --------------------------------- | ------------------------------------------- | -------------------------------------------- |
| `script/check`                    | `script/hooks/check.pre.sh`                 | `script/hooks/check.post.sh`                 |
| `script/clean`                    | `script/hooks/clean.pre.sh`                 | `script/hooks/clean.post.sh`                 |
| `script/develop`                  | `script/hooks/develop.pre.sh`               | — (long-running process)                     |
| `script/hassfest`                 | `script/hooks/hassfest.pre.sh`              | `script/hooks/hassfest.post.sh`              |
| `script/help`                     | `script/hooks/help.pre.sh`                  | `script/hooks/help.post.sh`                  |
| `script/lint`                     | `script/hooks/lint.pre.sh`                  | `script/hooks/lint.post.sh`                  |
| `script/lint-check`               | `script/hooks/lint-check.pre.sh`            | `script/hooks/lint-check.post.sh`            |
| `script/markdown`                 | `script/hooks/markdown.pre.sh`              | `script/hooks/markdown.post.sh`              |
| `script/markdown-check`           | `script/hooks/markdown-check.pre.sh`        | `script/hooks/markdown-check.post.sh`        |
| `script/python`                   | `script/hooks/python.pre.sh`                | `script/hooks/python.post.sh`                |
| `script/python-check`             | `script/hooks/python-check.pre.sh`          | `script/hooks/python-check.post.sh`          |
| `script/release-notes`            | `script/hooks/release-notes.pre.sh`         | `script/hooks/release-notes.post.sh`         |
| `script/shell`                    | `script/hooks/shell.pre.sh`                 | `script/hooks/shell.post.sh`                 |
| `script/shell-check`              | `script/hooks/shell-check.pre.sh`           | `script/hooks/shell-check.post.sh`           |
| `script/spell`                    | `script/hooks/spell.pre.sh`                 | `script/hooks/spell.post.sh`                 |
| `script/spell-check`              | `script/hooks/spell-check.pre.sh`           | `script/hooks/spell-check.post.sh`           |
| `script/test`                     | `script/hooks/test.pre.sh`                  | `script/hooks/test.post.sh`                  |
| `script/type-check`               | `script/hooks/type-check.pre.sh`            | `script/hooks/type-check.post.sh`            |
| `script/version`                  | `script/hooks/version.pre.sh`               | `script/hooks/version.post.sh`               |
| `script/yaml-check`               | `script/hooks/yaml-check.pre.sh`            | `script/hooks/yaml-check.post.sh`            |
| `script/setup/bootstrap`          | `script/hooks/setup/bootstrap.pre.sh`       | `script/hooks/setup/bootstrap.post.sh`       |
| `script/setup/reset`              | `script/hooks/setup/reset.pre.sh`           | `script/hooks/setup/reset.post.sh`           |
| `script/setup/setup`              | — (calls bootstrap)                         | `script/hooks/setup/setup.post.sh`           |
| `script/setup/sync-hacs`          | `script/hooks/setup/sync-hacs.pre.sh`       | `script/hooks/setup/sync-hacs.post.sh`       |
| `.devcontainer/on-create.sh`      | `.devcontainer/hooks/on-create.pre.sh`      | `.devcontainer/hooks/on-create.post.sh`      |
| `.devcontainer/update-content.sh` | `.devcontainer/hooks/update-content.pre.sh` | `.devcontainer/hooks/update-content.post.sh` |
| `.devcontainer/post-create.sh`    | `.devcontainer/hooks/post-create.pre.sh`    | `.devcontainer/hooks/post-create.post.sh`    |
| `.devcontainer/post-start.sh`     | `.devcontainer/hooks/post-start.pre.sh`     | `.devcontainer/hooks/post-start.post.sh`     |
| `.devcontainer/setup-shell.sh`    | `.devcontainer/hooks/setup-shell.pre.sh`    | `.devcontainer/hooks/setup-shell.post.sh`    |
| `.devcontainer/setup-git.sh`      | `.devcontainer/hooks/setup-git.pre.sh`      | `.devcontainer/hooks/setup-git.post.sh`      |
| `.devcontainer/post-attach.sh`    | `.devcontainer/hooks/post-attach.pre.sh`    | `.devcontainer/hooks/post-attach.post.sh`    |

### Example: install extra tools after bootstrap

```bash
# script/hooks/setup/bootstrap.post.sh
log_header "Installing project-specific tools"
uv pip install -q some-extra-tool
log_success "Extra tools installed"
```

### Example: run a custom linter after lint

```bash
# script/hooks/lint.post.sh
if command -v my-custom-linter >/dev/null 2>&1; then
    log_header "Running custom linter"
    my-custom-linter custom_components/
fi
```

### Example: set environment variables before tests

```bash
# script/hooks/test.pre.sh
export MY_DEVICE_API_KEY="test-key-123"
export MY_DEVICE_HOST="localhost"
```

### Notes

- Hooks are sourced (not executed), so `exit` would terminate the calling script — use `return` instead
- Hooks have access to all variables and functions defined in the calling script at that point
- A missing hook file is silently ignored — no error
- Hook scripts in `.devcontainer/hooks/` are not validated by `script/shell-check`; write them with care

---

## Environment Variables

The devcontainer setup can be customized through environment variable files without modifying `devcontainer.json`.

### Two-layer system

| File                       | Committed          | Purpose                                              |
| -------------------------- | ------------------ | ---------------------------------------------------- |
| `.devcontainer/.env`       | ✅ Yes             | Project-level defaults, shared with all contributors |
| `.devcontainer/.env.local` | ❌ No (gitignored) | Personal overrides, never affects others             |

Values in `.env.local` always win over `.env`. Both files use standard shell variable syntax:

```bash
HA_VERSION=2026.4
HA_INSTALL_HACS=1
APT_UPDATE=0
```

After changing either file, run **Dev Containers: Rebuild Container** to apply.

### Available variables

| Variable          | Default                  | Description                                                                                                     |
| ----------------- | ------------------------ | --------------------------------------------------------------------------------------------------------------- |
| `HA_VERSION`      | version from `hacs.json` | Home Assistant version to install. Accepts `latest`, `beta`, `YEAR.MONTH`, or an exact version like `2026.4.2`. |
| `HA_INSTALL_HACS` | `1`                      | Set to `0` to skip HACS installation (speeds up first-time setup).                                              |
| `APT_UPDATE`      | `0`                      | Set to `1` to run `apt-get update && apt-get upgrade` during setup.                                             |

### Scope limitations

These files are sourced by lifecycle hook scripts (`onCreateCommand`, `postCreateCommand`, etc.) and written into the shell RC files so interactive terminals also see the values. They are **not** available to:

- **DevContainer features** — features are installed during image build, before the container starts
- **`containerEnv`** — set independently by the Docker runtime

For feature versions (Python, Node.js) or Python runtime flags (`PYTHONASYNCIODEBUG` etc.), edit `devcontainer.json` directly.

### Personal overrides

Copy the example file and uncomment what you need:

```bash
cp .devcontainer/.env.local.example .devcontainer/.env.local
```

`.env.local` is gitignored and listed in `.templatesyncignore` — it is never committed and never touched by template sync.

---

## Python Dependencies

### Integration runtime dependencies (`requirements.txt`)

`manifest.json → requirements` is the authoritative list — Home Assistant reads it at runtime and installs those packages automatically. `requirements.txt` exists solely as a development mirror of the same packages, so tools like type-checkers, pytest, and your IDE can resolve imports without running Home Assistant.

Both files must be kept in sync by hand. This is by HA design and is unavoidable.

When you add a new dependency to your integration:

1. Add the package to `manifest.json` → `requirements`
2. Add the same package (with version pin) to `requirements.txt`
3. Run `script/setup/bootstrap` (or rebuild the container) to install it

`requirements.txt` is **excluded from template sync** because it is integration-specific content.

```text
# requirements.txt
my-device-library>=1.2.0
aiohttp>=3.9.0
```

> [!NOTE]
> `requirements_dev.txt` and `requirements_test.txt` **are** synced from the blueprint — they contain shared tooling dependencies. Add only integration runtime packages to `requirements.txt`.

### Personal extra packages (`requirements.local.txt`)

For personal or machine-specific packages that should not be committed, create a `requirements.local.txt` in the project root. It is gitignored and never committed. Common uses: debugging tools (`ipdb`, `icecream`), profilers, private packages, or additional dev/test packages beyond what `requirements_dev.txt` and `requirements_test.txt` provide.

```text
# requirements.local.txt — gitignored, never committed
ipdb
pytest-sugar
my-private-package @ git+https://github.com/me/my-package.git
```

`script/setup/bootstrap` automatically installs it after `requirements.txt` if the file exists.

| File                     | Template sync  | Purpose                                        |
| ------------------------ | -------------- | ---------------------------------------------- |
| `requirements.txt`       | ❌ Excluded    | Your integration's runtime dependencies        |
| `requirements_dev.txt`   | ✅ Synced      | Development tool dependencies (shared)         |
| `requirements_test.txt`  | ✅ Synced      | Test dependencies (shared)                     |
| `requirements.local.txt` | — (gitignored) | Your personal extra packages (never committed) |
