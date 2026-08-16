# Working with AI coding agents

This repository is set up for several coding agents at once — GitHub Copilot (VS Code and CLI), Claude Code, and
Codex CLI. Their shared instructions live in `AGENTS.md`; what follows is the workflow around them and where each
agent's own configuration is kept.

## Human Review and Transparency

An agent prepares a draft; that does not establish that the integration is understood, tested, or ready to
publish. Before merging, review the diff and accurately record which checks, automated tests, and real-device tests were
performed. If review is partial or some behavior could not be tested, document that limitation instead of implying full
verification.

Extensive AI assistance is acceptable for a community custom integration. See [`AI_POLICY.md`](../../AI_POLICY.md) for
the project's approach to AI use, transparency, and informed user choice. Do not use this workflow for autonomous
contributions to an Open Home Foundation repository, where the official OHF AI Policy applies.

## Reviewing an agent's changes

After an agent opens a draft pull request — the workflow below is written for the GitHub Copilot Coding Agent, which runs in GitHub Actions, but the review steps apply to any agent that hands you a branch:

1. **Open the PR branch in Codespaces**
   - Navigate to the pull request on GitHub
   - Click "Code" → "Create codespace on `branch-name`"
   - Codespace starts with all dependencies pre-installed (see [CODESPACES.md](CODESPACES.md))

2. **Start Home Assistant**
   - Run `./script/develop` in the terminal
   - Port 8123 forwards automatically (forwarded URL appears in notification)
   - Click the forwarded port URL to open HA in browser

3. **Test the integration**
   - Run the relevant automated tests using `script/test`
   - Add the integration via Home Assistant UI
   - Verify entities appear correctly
   - Test functionality with your actual device/service
   - Check logs: `config/home-assistant.log` or live in terminal

4. **Iterate if needed**
   - Comment on the PR with `@copilot` to request changes
   - Or make manual adjustments and commit to the PR branch
   - Stop Codespace when done to save free hours

> [!NOTE]
> Copilot Agent runs in GitHub Actions (ephemeral environment), so it cannot provide live web access to Home Assistant during development. Manual testing in Codespaces is required.

For detailed Codespaces usage, troubleshooting, and resource management, see [CODESPACES.md](CODESPACES.md).

## Tips

- Start simple - get a working prototype first
- Use `@copilot` in PR comments to iterate
- Review every iteration before merging and keep the PR's verification context accurate
- Break large changes into multiple PRs

## Agent Configuration Matrix (Vendor-Supported)

Use this matrix to keep security/approval behavior in real, vendor-supported
configuration files rather than in instruction prose.

| Agent                   | Policy and hook configuration                                                                                 | Shared hook implementation             | Notes                                                                                                           |
| ----------------------- | ------------------------------------------------------------------------------------------------------------- | -------------------------------------- | --------------------------------------------------------------------------------------------------------------- |
| Copilot / VS Code agent | VS Code approval settings plus [.claude/settings.json](../../.claude/settings.json) for local lifecycle hooks | [.agents/hooks/](../../.agents/hooks/) | VS Code currently ignores hook matchers, so every shared hook must safely ignore unrelated calls.               |
| Copilot CLI             | CLI defaults plus [.claude/settings.json](../../.claude/settings.json)                                        | [.agents/hooks/](../../.agents/hooks/) | The GitHub-hosted coding agent only reads `.github/hooks/`; this repository does not duplicate its local hooks. |
| Claude Code             | Managed policy plus project hooks in [.claude/settings.json](../../.claude/settings.json)                     | [.agents/hooks/](../../.agents/hooks/) | Project hooks are version-controlled; managed settings are copied into the container.                           |
| Codex CLI               | Sandbox defaults plus project hooks in [.codex/hooks.json](../../.codex/hooks.json)                           | [.agents/hooks/](../../.agents/hooks/) | Codex asks the user to trust changed project hooks before executing them.                                       |
| Gemini                  | Not configured                                                                                                | —                                      | Not part of the default devcontainer experience.                                                                |

### Practical rule

- Put policy and defaults in vendor config files first.
- Keep markdown instruction files for workflow guidance only.

Claude Code, Codex, VS Code, and Copilot CLI all support lifecycle hooks. The configuration paths differ, but the
commands here converge on `.agents/hooks/` so security behavior is implemented and tested once. Claude slash commands
under `.claude/commands/` remain Claude-specific; the corresponding reusable workflow is the vendor-neutral
[`ha-issue-triage`](../../.agents/skills/ha-issue-triage/SKILL.md), with `.github/prompts/` providing Copilot dispatch.
These agent lifecycle hooks are unrelated to `script/hooks/`, which customizes the repository's validation scripts.

### Branch/PR-based work is available, not mandatory

Most of this repository's own history is direct commits to `main` — that stays a perfectly normal way to work here,
especially for a single request handled live with a developer watching each change. `ha-issue-triage` adds the other
option as opt-in tooling: working a backlog of issues through a feature branch, a pull request, and green CI before
merging — useful specifically because nobody is reviewing each individual commit in real time when an agent works
through several issues in a row. See `RELEASE.md`'s branch-protection section if you want to require PRs on `main`
at the repository-settings level too; that's independent of whether you use this skill.

## Resources

- [GitHub Copilot Best Practices](https://docs.github.com/en/copilot/tutorials/coding-agent/get-the-best-results)
- [GitHub Copilot hooks reference](https://docs.github.com/en/copilot/reference/hooks-reference)
- [VS Code hooks reference](https://code.visualstudio.com/docs/agents/reference/hooks-reference)
- [Codex hooks](https://learn.chatgpt.com/docs/hooks)
- `AGENTS.md` - Read automatically by Copilot; the single always-loaded instruction file for every agent
- [`.agents/skills/`](../../.agents/skills/README.md) - Task-triggered agent skills. Copilot reads this location
  directly; Claude Code reaches the same files through the `.claude/skills/` symlink
