# Manual steps

What an integration repository has to do by hand because template sync cannot do it, newest first. Each step has an id
for the `skipped` list in `.agents/blueprint-update.json`, the date it entered the blueprint, and a check that passes
once it is done. Run the check from the repository root.

## `squash-pull-requests` — 2026-11-01

**Check:** `gh api "repos/{owner}/{repo}" --jq '.allow_merge_commit == false' | grep -q true`

The blueprint's `main` ruleset now takes every change through a pull request, admins included — squash by default,
rebase for a pull request whose commits each pass the commit rules — and a new workflow `pr-title.yml` checks the
title, which becomes the squash commit, and reports whether each commit would survive a rebase.
Ask the developer whether they want that: if so, copy the workflow (`script/blueprint-update` lists it) and run
`script/setup/github`; if not, follow _Want it less strict?_ in `docs/development/REPOSITORY_SETUP.md` of the
blueprint and record the step as skipped.

## `lint-and-test-check` — 2026-11-01

**Check:** `! gh api "repos/{owner}/{repo}/rules/branches/main" --jq '.[].parameters.required_status_checks[]?.context' 2>/dev/null | grep -qx Ruff`

The lint workflow's job is now called _Lint and test_ and also runs `script/type-check` and `script/test`. A ruleset
or branch protection that still requires the old `Ruff` check waits for it forever and blocks every pull request:
replace it with `Lint and test` — `script/setup/github` does that for the `main` ruleset it manages.

## `repository-settings` — 2026-11-01

**Check:** `gh api "repos/{owner}/{repo}/rulesets" --jq 'map(.name) | index("main") != null' | grep -q true`

Run `script/setup/github --dry-run`, show the developer what it would change, and run it without the flag once they
agree. It turns on Dependabot alerts and, on a public repository, secret scanning and push protection, and imports the
`main` ruleset; `docs/development/REPOSITORY_SETUP.md` in the blueprint explains each setting and what it costs on a
private repository. The new workflows `codeql.yml` and `secret-history-scan.yml` arrive through the sync only with a
`TEMPLATE_SYNC_TARGET_PAT`; otherwise `script/blueprint-update` lists them as new files to copy.

## `blueprint-identity` — 2026-11-01

**Check:** `grep -q '"identity"' .agents/blueprint-update.json`

Record this repository's names in `.agents/blueprint-update.json`, as `initialize.sh` now does for a new one:
`"identity": {"domain": …, "title": …, "prefix": …, "owner": …, "repository": …, "author": …}` beside `reviewed`.
Without it `script/blueprint-update` infers them from the manifest, the coordinator class and `LICENSE`, and a renamed
class lets the blueprint's own class prefix through into the diff. The values are what `initialize.sh` asked for:
the domain, the title, the class prefix, the GitHub owner and repository name, and the author.

## `template-sync-guard` — 2026-11-01

**Check:** `grep -q template-sync-guard .github/workflows/template-sync.yml`

Copy the step _Keep this repository's newer versions_ from the blueprint's `template-sync.yml` to the end of this
repository's; `script/blueprint-update` shows it in context. Without it, a sync lowers every version this repository's
Dependabot or Renovate raised further than the blueprint has. The script it calls, `script/template-sync-guard`,
already arrives through the sync — only the workflow is excluded.

## `mise-project-tools` — 2026-11-01

**Check:** `grep -qxF '.config/mise/conf.d/project.toml' .templatesyncignore`

Add `.config/mise/conf.d/project.toml` to `.templatesyncignore`, in the section for project-owned files. It is where
this repository's own command-line tools go; `mise.toml` holds the blueprint's and is overwritten by the sync.
Create the file from the blueprint's copy if the project wants a tool of its own now.

## `agents-md-outside-container` — 2026-11-01

**Check:** `grep -q '^## Outside the dev container' AGENTS.md && grep -q 'never wait for an answer' AGENTS.md`

Carry over three changes to `AGENTS.md`: the CLI tools paragraph now names `mise.toml` instead of the dev container,
_Commands you run yourself never wait for an answer_ joined the validation section, and _Outside the dev container_
is new. They tell agents how the repository works in a cloud session or on a machine without the dev container.
`script/blueprint-update` shows all three as hunks.
