---
name: ha-release
description: >-
  Cut a release of this Home Assistant custom integration, or prepare the commits that feed it. Use when asked to
  "release", "cut a version", "bump the version", "prepare release notes", "what will the next version be", "write
  a commit message", "why didn't release-please pick this up", or when reviewing whether a change is user-facing.
  Covers the Conventional Commits rules commitlint enforces here, how release-please derives the version and
  changelog, the pre-1.0 bump rules, script/version and script/release-notes, skipping a commit from the notes,
  and the commit rules this project enforces for agents. SYMPTOMS — load this if you are about to: commit without
  an explicit request; offer to `git push`; label a user-facing fix as `chore` (chore, like every hidden type, never
  reaches the changelog and never triggers a release); write a commit subject over 72 characters or in sentence case;
  or edit the version in `manifest.json` by hand.
---

# Releases and commit messages

Releases are driven entirely by commit messages. A sloppy commit subject is not a cosmetic issue here — it decides the
version number and what users read in the changelog.

## Commit rules for agents (non-negotiable)

- **Never commit automatically.** Only commit when the developer explicitly asks, in that message.
- A previous commit request is **not** standing permission. Each commit needs a fresh instruction.
- **Never push, and never offer to.** The developer handles `git push`.
- Always run `git diff` (and `git status`) before writing a message. Describe what is actually staged, not what you
  remember doing.

## Commit message format

The format, the allowed types and scopes, the rules commitlint enforces, and the scope-versus-type trap are all in
[`blueprint.commit-message.instructions.md`](../../instructions/blueprint.commit-message.instructions.md),
which Copilot loads for every file. Read it before writing a message.

What that file does not tell you is what your choice costs at release time: **a user-facing change committed under a
hidden type (`refactor`, `chore`, `docs`, `test`, `ci`) never reaches the changelog and never triggers a release** —
only `feat`, `fix`, `perf`, and breaking changes do. If a change matters to a user, pick one of those honestly instead
of reaching for `chore`.

When you tell someone which type to use, say this consequence out loud — "X, because Y is hidden from the changelog
and never ships a release" — don't just name the type and cite the instructions file's definition of it.

## What each type does to the release

| Type                                      | Changelog section | Version effect (pre-1.0)           |
| ----------------------------------------- | ----------------- | ---------------------------------- |
| `feat`                                    | Features          | patch bump (`0.1.0` → `0.1.1`)     |
| `fix`                                     | Bug Fixes         | patch bump                         |
| `perf`                                    | Performance       | patch bump                         |
| `feat!` / `BREAKING CHANGE:`              | Features + notice | **minor** bump (`0.1.0` → `0.2.0`) |
| `refactor`, `chore`, `docs`, `test`, `ci` | hidden            | no release                         |

After `1.0.0`, standard SemVer applies: `feat` → minor, `fix` → patch, breaking → major.

Breaking changes need both markers, and the footer text is what users read:

```text
feat(config_flow)!: require an API key instead of username and password

BREAKING CHANGE: Existing entries are migrated automatically, but users who
authenticated with a username must generate an API key in the vendor portal and
re-authenticate when prompted.
```

See [`ha-breaking-changes`](../ha-breaking-changes/SKILL.md) before writing one.

## How a release happens

```text
commits on main → release-please opens/updates "chore(main): release X.Y.Z"
               → developer reviews, optionally enhances the notes
               → developer merges the PR
               → release-please tags and publishes the GitHub Release
```

`manifest.json` → `version` is the source of truth and is bumped inside the release PR by release-please
(`release-please-config.json` → `extra-files`). Never edit it by hand.

There is no automatic merge. The developer decides when to release.

## Commands

```bash
script/version              # 0.1.0
script/version --tag        # v0.1.0
script/version --check      # manifest.json vs .release-please-manifest.json

script/release-notes              # preview AI-enhanced notes on stdout
script/release-notes --apply      # write them into the open release PR body
script/release-notes --interactive # write context to .agents/scratch/ and open a session
```

`script/release-notes` needs GitHub Copilot CLI and `gh auth login`. It finds the PR labelled
`autorelease: pending`, collects commits and a compact diff since the last tag, and rewrites the notes for a
user-facing audience. Tunable via `COPILOT_MODEL` and `RELEASE_NOTES_DIFF_MAX`.

**The generated notes are a draft.** Whoever publishes the release is accountable for their technical accuracy, so
they get read before the release PR is merged — not after ([`AI_POLICY.md`](../../../AI_POLICY.md)).

To keep an internal commit out of the notes, add a trailer to its body:

```text
Release-Notes: skip
```

or `User-Impact: none`.

## Pre-release checklist

Before suggesting the release PR be merged:

```bash
script/check          # type-check + lint-check + spell-check
script/hassfest
script/test
script/version --check
```

Also confirm:

- The changelog entries read as user-facing statements, not commit titles.
- Every breaking change has a `BREAKING CHANGE:` footer and a migration note.
- `docs/user/` and the README match the released behaviour.
- The minimum Home Assistant version in `hacs.json` and `manifest.json` is still accurate.

## Troubleshooting

| Symptom                                | Cause                                                                    |
| -------------------------------------- | ------------------------------------------------------------------------ |
| No release PR appeared                 | Only hidden types (`chore`, `docs`, …) landed — nothing to release       |
| A change is missing from the changelog | It was committed under a hidden type, or carries `Release-Notes: skip`   |
| Version bumped in the wrong direction  | `bump-patch-for-minor-pre-major` is on until 1.0.0 — this is intentional |
| `script/version --check` fails         | `manifest.json` was edited by hand; let release-please own it            |
| release-please cannot open a PR        | Repository Actions permissions — see `docs/development/RELEASE.md`       |

One-time GitHub repository setup (Actions permissions, branch protection, required checks) is documented in
[`docs/development/RELEASE.md`](../../../docs/development/RELEASE.md); it cannot be configured from the repository.
