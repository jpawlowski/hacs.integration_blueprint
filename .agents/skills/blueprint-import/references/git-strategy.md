# Repository and git strategy

Read this during phase 1, before running `initialize.sh`.

## Keep the existing repository

Issues, pull requests, stars, release tags and the HACS listing are tied to the repository **URL**, not to the commit
history inside it. Creating a new repository from the template and abandoning the old one throws all of that away, and
HACS users end up on a repository that no longer receives updates.

Both strategies below work inside the existing repository.

## Option A — Clean history, force-push (recommended)

Least painful when the commit history is not worth preserving.

1. Clone the blueprint locally:
   `git clone https://github.com/jpawlowski/hacs.integration_blueprint.git`
2. Point the remote at the existing repository **before** initialising:
   `git remote set-url origin https://github.com/<you>/<your-repo>.git`
   Doing this first also avoids `initialize.sh` refusing to run against the blueprint's own remote.
3. `./initialize.sh --force` with the **existing** domain, title and — ideally — the existing class prefix.
   `--force` is needed because a direct clone carries the blueprint's full history rather than the single commit a
   "Use this template" repository has.
4. Copy `custom_components/<domain>/` from the old code in, replacing the generated one.
5. `git push --force origin main`.

Issues and pull requests survive; the commit history starts fresh.

> Force-pushing rewrites public history. Anyone with a local clone must re-clone or hard-reset. Say so before doing
> it, and never do it without an explicit instruction.

## Option B — Merge unrelated histories

Only worth it when a continuous `git log` genuinely matters.

1. `git remote add blueprint https://github.com/jpawlowski/hacs.integration_blueprint.git`
2. `git fetch blueprint`
3. `git merge blueprint/main --allow-unrelated-histories`
4. Resolve the conflicts — expect nearly every file to conflict, since the blueprint touches the whole tree.
5. `./initialize.sh --force` to finalise the identifiers.

## Before running `initialize.sh`

Always do a `--dry-run` pass first, and confirm:

- `--domain` is the **existing** domain, character for character.
- `--namespace` is the class prefix the code already uses, unless a rename is deliberate.
- The working tree is committed or stashed, so the run is revertable.

## Repository settings to re-check afterwards

- **Actions permissions** — _Settings → Actions → General_ → allow GitHub Actions to create and approve pull
  requests, or the release and template-sync workflows cannot open their pull requests.
- **Branch protection** — the workflows assume a `main` branch.
- **Secrets** — anything the old workflows used has to exist in this repository too.
- **`hacs.json`** — `initialize.sh` sets `name` and `homeassistant`, but does not preserve other fields the old
  repository may have had, such as `render_readme`, `hide_default_branch` or `filename`. Restore them by hand.
- **`manifest.json`** — `documentation` and `issue_tracker` must point at this repository.
