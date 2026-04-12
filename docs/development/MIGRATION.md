# Migrating an Existing HACS Integration to This Blueprint

This guide is for developers who already have a HACS integration and want to adopt this
blueprint's project structure, DevContainer environment, and tooling.

> [!NOTE]
> This file is part of the blueprint template and is removed automatically when you run
> `./initialize.sh`. If you need it later, the original lives at
> [jpawlowski/hacs.integration_blueprint](https://github.com/jpawlowski/hacs.integration_blueprint/blob/main/docs/development/MIGRATION.md).

## The Core Idea

The only thing that really needs to come from your existing repository is the contents of
`custom_components/<your_domain>/`. Everything else — DevContainer, scripts, workflows,
configuration — comes from the blueprint and stays as-is (or is extended via hooks).

This makes the migration straightforward in principle:

1. Get the blueprint code into your existing repository (see strategies below)
2. Run `./initialize.sh` to set the domain, title, and class prefix
3. Replace the generated `custom_components/<your_domain>/` with your existing code
4. Adapt your code to the blueprint's structure where needed

## Deciding on a Git Strategy

> [!IMPORTANT]
> **Keep your existing GitHub repository.** Issues, pull requests, stars, and the HACS
> listing are all tied to the repository URL — not the git history inside it. Creating a
> new repository from the template and abandoning the old one means losing all of that.
> Both strategies below work inside your existing repository.

### Option A: Force-push a clean history (recommended)

If you don't need to preserve your commit history, this is the least painful path:

1. Clone this blueprint locally: `git clone https://github.com/jpawlowski/hacs.integration_blueprint.git`
2. Change the remote to your existing repository **before** running the setup script:
   `git remote set-url origin https://github.com/<you>/<your-repo>.git`
3. Run `./initialize.sh --force` to set your domain, title, and class prefix.
   `--force` is required here because `initialize.sh` normally only runs on fresh
   template clones (single commit), and a direct clone has the full commit history.
   It would also block on the original blueprint remote — changing the remote in step 2
   first avoids that check, but `--force` is still needed for the commit count check.
4. Copy your `custom_components/<your_domain>/` into the result
5. Force-push: `git push --force origin main`

Your existing issues and PRs remain intact. The commit history starts fresh from this point.

> [!WARNING]
> `git push --force` rewrites public history. Anyone with a local clone of your repository
> will need to re-clone or hard-reset. Communicate this to collaborators if any exist.

### Option B: Merge the blueprint into your existing repository

If you want to keep your existing commit history, merge the blueprint into your repo:

1. Add the blueprint as a remote: `git remote add blueprint https://github.com/jpawlowski/hacs.integration_blueprint.git`
2. Fetch it: `git fetch blueprint`
3. Merge with unrelated histories: `git merge blueprint/main --allow-unrelated-histories`
4. Resolve conflicts (expect many — practically every file will conflict)
5. Run `./initialize.sh` to finalize the rename

This is significantly more work. Conflicts will be dense because the blueprint touches
almost every file. Only worth it if a continuous git log really matters to you.

## What to Watch Out For

### Namespace / class prefix

The blueprint uses a consistent class prefix (`IntegrationBlueprint` by default, replaced by
`initialize.sh`). If your existing code uses a different naming convention, you will need
to rename your classes — or just run `./initialize.sh` with `--namespace YourPrefix` and
it handles the renaming for you across the codebase.

### Package structure

The blueprint organizes code into sub-packages (`coordinator/`, `api/`, `entity/`, etc.).
If your integration is a flat set of files, you can start by dropping them into
`custom_components/<your_domain>/` as-is — Home Assistant doesn't care about the internal
structure. You can then refactor gradually into the blueprint's layout.

See [ARCHITECTURE.md](ARCHITECTURE.md) for the expected package layout.

### Config flow location

The blueprint places the config flow in `config_flow_handler/` (a sub-package), but keeps a
thin `config_flow.py` shim at the top level for Home Assistant's discovery. If your
integration has `config_flow.py` at the root already, that works fine — just be aware if
you use the blueprint's scaffolding or `script/check`.

### Permissions and repository settings

When creating the new repository from the template, double-check:

- **Branch protection rules** — the template's default workflows expect a `main` branch
- **GitHub Actions permissions** — workflows need `contents: write` for the release and
  template-sync workflows to function; set this under _Settings → Actions → General_
- **Repository secrets** — if your integration tests against a real device or API, you may
  need to re-add any secrets the old repository had

### Python dependencies

If your integration depends on extra Python packages, they are declared in two places
that must stay in sync:

- **`custom_components/<domain>/manifest.json` → `requirements`** — the authoritative list.
  Home Assistant reads this and auto-installs the packages when the integration loads.
  This is what end users get.
- **`requirements.txt`** (repository root) — dev environment only. Needed so local tests,
  type checking, and the devcontainer HA instance can resolve the same packages. Keep this
  in sync with `manifest.json`.

When you copy your integration code in, make sure `manifest.json` still has the `requirements`
field with the correct pinned versions. `requirements.txt` is excluded from template sync, so
additions you make there are safe and won't be overwritten by upstream updates.

### hacs.json

`hacs.json` lives at the repository root and is required for HACS discovery. `initialize.sh`
sets the `name` and `homeassistant` fields automatically, but it does not preserve any other
fields your old integration may have had. Check and restore manually if you used fields like
`render_readme`, `hide_default_branch`, or `filename`.

### HACS validation

After migration, run `script/hassfest` to verify the manifest and translation files are
still valid. Common issues after moving to a new repository:

- `manifest.json` still points to the old repository URL
- `hacs.json` has a `name` or `filename` that no longer matches
- Translation files reference strings that don't exist yet in the new flow

Running `./initialize.sh` takes care of the manifest and `hacs.json` automatically, but
verify manually if you copied your own files back in afterwards.

### Template sync

Once you have the blueprint set up, a weekly pull request will offer upstream improvements.
Files you do not want synced can be excluded via `.templatesyncignore`.

See [CUSTOMIZATION.md](CUSTOMIZATION.md) for details on template sync and hook scripts.
