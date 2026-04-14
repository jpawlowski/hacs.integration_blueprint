# Release Management

This document describes the release process for this integration, including automated versioning, changelog generation, and AI-enhanced release notes.

## Overview

Releases are managed with [release-please](https://github.com/googleapis/release-please), which automates version bumping and changelog generation based on [Conventional Commits](https://www.conventionalcommits.org/). An optional local script enhances release notes using GitHub Copilot CLI.

**Version source of truth:** `custom_components/ha_integration_domain/manifest.json`

## How It Works

### The Release Cycle

```text
1. Developer commits to main (Conventional Commits format)
        ↓
2. release-please opens/updates a release PR automatically
        ↓
3. Developer reviews and optionally enhances release notes
        ↓
4. Developer merges the PR (intentionally, when ready)
        ↓
5. release-please creates the GitHub Release + Git tag
   manifest.json version is already updated in the merged PR
```

### The Release PR

After any `feat`, `fix`, or `perf` commit reaches `main`, release-please opens a pull request titled:

```text
chore(main): release X.Y.Z
```

The PR:

- Has the label `autorelease: pending`
- Contains an updated `CHANGELOG.md` (prepended section for the new version)
- Contains the version bump in `manifest.json`
- Is updated automatically as more commits land on `main`

**You decide when to release** by merging the PR. There is no automatic merge.

### Version Bumping Rules

This project is pre-1.0.0. Version bumps follow these rules:

| Commit type                   | Version change                      |
| ----------------------------- | ----------------------------------- |
| `feat`                        | patch bump (e.g. `0.1.0` → `0.1.1`) |
| `fix`, `perf`                 | patch bump                          |
| `feat!` or `BREAKING CHANGE:` | minor bump (e.g. `0.1.0` → `0.2.0`) |

Once the project reaches `1.0.0`, standard SemVer applies (`feat` → minor, `fix` → patch, breaking → major).

### What Appears in the Changelog

Only user-facing changes appear in the public CHANGELOG:

| Type                                      | Visible        |
| ----------------------------------------- | -------------- |
| `feat`                                    | ✅ Features    |
| `fix`                                     | ✅ Bug Fixes   |
| `perf`                                    | ✅ Performance |
| `refactor`, `chore`, `docs`, `test`, `ci` | hidden         |

## Developer Scripts

### `script/version`

Reads the canonical version from `manifest.json`.

```bash
./script/version              # Print: 0.1.0
./script/version --tag        # Print: v0.1.0
./script/version --check      # Verify manifest.json matches .release-please-manifest.json
```

### `script/release-notes`

Generates AI-enhanced release notes using [GitHub Copilot CLI](https://docs.github.com/en/copilot/concepts/agents/about-copilot-cli). Requires an active Copilot subscription and `gh auth login`.

```bash
# Preview enhanced notes on stdout
./script/release-notes

# Update the open release-please PR body with enhanced notes
./script/release-notes --apply

# Launch Copilot CLI interactively with context pre-loaded
./script/release-notes --interactive
```

**How it works:**

1. Finds the open release-please PR (`autorelease: pending` label)
2. Collects rich context since the last tag:
   - Full commit details (subject, body, per-commit file stats)
   - Compact code diff for user-facing paths (sensors, config flow, services, translations)
   - Net file change list as source of truth
   - Revert commit list as chronology hints
3. Builds a detailed prompt with audience definition, jargon rules, and file impact guidance
4. Sends everything to Copilot CLI via stdin (avoids shell-escaping issues with large prompts)
5. Outputs the result to stdout, or updates the PR body with `--apply`

**`--interactive` mode** writes the full prompt and context to `.ai-scratch/release-notes-context.md` and launches a Copilot CLI session so you can iterate manually.

**Skip a commit from release notes** by adding a trailer to the commit body:

```text
Release-Notes: skip
```

or:

```text
User-Impact: none
```

**Environment variables:**

| Variable                 | Default             | Description                     |
| ------------------------ | ------------------- | ------------------------------- |
| `COPILOT_MODEL`          | `claude-sonnet-4.6` | AI model to use                 |
| `RELEASE_NOTES_DIFF_MAX` | `8000`              | Max bytes for code diff context |

## Typical Release Workflow

### Minimal (automated only)

```bash
# 1. Work on features, commit using Conventional Commits
git commit -m "feat(sensor): add air quality index sensor"

# 2. Push to main — release-please opens/updates PR automatically

# 3. When ready to release: review the PR on GitHub, then merge it
```

### With enhanced release notes

```bash
# 1. Check the current version and open PR
./script/version

# 2. Generate Copilot-enhanced release notes and review
./script/release-notes

# 3. If satisfied, update the PR body
./script/release-notes --apply

# 4. Merge the PR on GitHub
```

## GitHub Repository Setup (One-Time)

> [!NOTE]
> These settings cannot be stored in the repository — configure them once on GitHub.com.

### Required: GitHub Actions Permissions

In **Settings → Actions → General → Workflow permissions**, set:

- **Read and write permissions** — release-please needs to create PRs and tags

### Recommended: Branch Protection for `main`

In **Settings → Branches → Add branch ruleset** (or classic protection rule for `main`):

- **Require a pull request before merging** — prevents direct pushes
- **Require status checks to pass** — add `Ruff`, `Hassfest validation`, `HACS validation` as required checks
- This ensures the release PR can only be merged when CI is green, giving you a reliable safety net

With required status checks in place, a release PR with failing CI simply cannot be merged accidentally.

### Optional: Protect the Release PR from Accidental Merge

release-please labels its PR with `autorelease: pending`, which visually distinguishes it from feature PRs. With branch protection and required checks active, the risk of accidental merges is already very low.

If you want an additional manual gate, you can add a required label (`release: approved`) that must be set before the PR can be merged — configure this via a custom branch ruleset in GitHub.

## Files

| File                                   | Purpose                                                          |
| -------------------------------------- | ---------------------------------------------------------------- |
| `.github/workflows/release-please.yml` | GitHub Actions workflow, triggers on push to `main`              |
| `release-please-config.json`           | Changelog sections, version bump rules, extra-files              |
| `.release-please-manifest.json`        | Current version tracked by release-please                        |
| `CHANGELOG.md`                         | Auto-generated, committed in the same commit as the version bump |
| `script/version`                       | Local version utility                                            |
| `script/release-notes`                 | Local Copilot CLI release notes enhancement                      |
