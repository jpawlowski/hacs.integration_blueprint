# Customization & Extensibility

This document explains how to customize and extend the blueprint without modifying files that are managed by the upstream template.

## Template Sync

Repositories created from this blueprint can receive upstream improvements automatically via a weekly pull request created by the [template sync workflow](.github/workflows/template-sync.yml).

### How it works

Every Monday at 07:00 UTC, the workflow checks whether the upstream blueprint (`jpawlowski/hacs.integration_blueprint`) has new commits. If it does, it opens a pull request with the diff against your repository.

You review the PR and merge anything you want to adopt. Changes you don't want can simply be dismissed or partially merged.

### Merge conflicts

Conflicts happen when both you and the upstream changed the same file. GitHub marks the conflicting file in the PR diff. Options:

- **Accept upstream**: Take the whole upstream version and re-apply your local changes on top
- **Accept yours**: Close the PR for that file (or revert individual hunks) and keep your version
- **Manual merge**: Edit the file locally, resolve the conflict markers, and push to the PR branch

There is no automated conflict resolution. Template sync PRs are ordinary PRs — review them like any other code change.

### Excluding files from sync

Files listed in [`.templatesyncignore`](../../.templatesyncignore) are never touched by the sync PR, even if they changed upstream.

The syntax follows `.gitignore` glob patterns. To exclude an additional file or directory, add a line:

```text
# My integration-specific overrides
config/
path/to/my-file.json
```

Files already excluded by default:

| Path                                                                     | Reason                                                         |
| ------------------------------------------------------------------------ | -------------------------------------------------------------- |
| `custom_components/`                                                     | Your integration code                                          |
| `tests/`                                                                 | Test files reference your domain (replaced by `initialize.sh`) |
| `pyproject.toml`                                                         | Contains your domain in package metadata                       |
| `.yamllint.yml`                                                          | Contains your domain in configuration comment                  |
| `.pre-commit-config.yaml`                                                | Contains your domain in file-match patterns                    |
| `.vscode/launch.json`, `.vscode/tasks.json`                              | Contain your domain in debugger/task arguments                 |
| `README.md`, `LICENSE`, etc.                                             | Replaced by `initialize.sh`                                    |
| `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`, `.github/copilot-instructions.md` | Contain domain-specific references                             |
| `config/`                                                                | Local HA instance (credentials, test data)                     |
| `docs/`                                                                  | Your project documentation                                     |
| `script/hooks/`, `.devcontainer/hooks/`                                  | Your hook scripts                                              |
| `release-please-config.json`, `.release-please-manifest.json`            | Release management                                             |
| `.github/workflows/template-sync.yml`                                    | Sync workflow itself                                           |
| `uv.lock`                                                                | Your pinned dependency lockfile                                |

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

| Script                         | pre hook                                 | post hook                                 |
| ------------------------------ | ---------------------------------------- | ----------------------------------------- |
| `script/check`                 | `script/hooks/check.pre.sh`              | `script/hooks/check.post.sh`              |
| `script/clean`                 | `script/hooks/clean.pre.sh`              | `script/hooks/clean.post.sh`              |
| `script/develop`               | `script/hooks/develop.pre.sh`            | — (long-running process)                  |
| `script/hassfest`              | `script/hooks/hassfest.pre.sh`           | `script/hooks/hassfest.post.sh`           |
| `script/help`                  | `script/hooks/help.pre.sh`               | `script/hooks/help.post.sh`               |
| `script/lint`                  | `script/hooks/lint.pre.sh`               | `script/hooks/lint.post.sh`               |
| `script/lint-check`            | `script/hooks/lint-check.pre.sh`         | `script/hooks/lint-check.post.sh`         |
| `script/markdown`              | `script/hooks/markdown.pre.sh`           | `script/hooks/markdown.post.sh`           |
| `script/markdown-check`        | `script/hooks/markdown-check.pre.sh`     | `script/hooks/markdown-check.post.sh`     |
| `script/python`                | `script/hooks/python.pre.sh`             | `script/hooks/python.post.sh`             |
| `script/python-check`          | `script/hooks/python-check.pre.sh`       | `script/hooks/python-check.post.sh`       |
| `script/release-notes`         | `script/hooks/release-notes.pre.sh`      | `script/hooks/release-notes.post.sh`      |
| `script/shell`                 | `script/hooks/shell.pre.sh`              | `script/hooks/shell.post.sh`              |
| `script/shell-check`           | `script/hooks/shell-check.pre.sh`        | `script/hooks/shell-check.post.sh`        |
| `script/spell`                 | `script/hooks/spell.pre.sh`              | `script/hooks/spell.post.sh`              |
| `script/spell-check`           | `script/hooks/spell-check.pre.sh`        | `script/hooks/spell-check.post.sh`        |
| `script/test`                  | `script/hooks/test.pre.sh`               | `script/hooks/test.post.sh`               |
| `script/type-check`            | `script/hooks/type-check.pre.sh`         | `script/hooks/type-check.post.sh`         |
| `script/version`               | `script/hooks/version.pre.sh`            | `script/hooks/version.post.sh`            |
| `script/yaml-check`            | `script/hooks/yaml-check.pre.sh`         | `script/hooks/yaml-check.post.sh`         |
| `script/setup/bootstrap`       | `script/hooks/setup/bootstrap.pre.sh`    | `script/hooks/setup/bootstrap.post.sh`    |
| `script/setup/reset`           | `script/hooks/setup/reset.pre.sh`        | `script/hooks/setup/reset.post.sh`        |
| `script/setup/setup`           | — (calls bootstrap)                      | `script/hooks/setup/setup.post.sh`        |
| `script/setup/sync-hacs`       | `script/hooks/setup/sync-hacs.pre.sh`    | `script/hooks/setup/sync-hacs.post.sh`    |
| `.devcontainer/setup-shell.sh` | `.devcontainer/hooks/setup-shell.pre.sh` | `.devcontainer/hooks/setup-shell.post.sh` |
| `.devcontainer/setup-git.sh`   | `.devcontainer/hooks/setup-git.pre.sh`   | `.devcontainer/hooks/setup-git.post.sh`   |
| `.devcontainer/post-attach.sh` | —                                        | `.devcontainer/hooks/post-attach.post.sh` |

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
