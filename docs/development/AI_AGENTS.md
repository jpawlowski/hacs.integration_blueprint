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

| Agent                     | Supported config surface                                | Repo source of truth                                                                                                                                                                                                                                                                                                                               | Runtime target                                              | Notes                                                                                                                                       |
| ------------------------- | ------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------- |
| Copilot (VS Code agent)   | VS Code settings (`chat.*`, `github.copilot.*`)         | [.vscode/settings.default.jsonc](../../.vscode/settings.default.jsonc), [.devcontainer/devcontainer.json](../../.devcontainer/devcontainer.json)                                                                                                                                                                                                   | VS Code workspace + devcontainer customization settings     | Use `chat.tools.edits.autoApprove` for sensitive-path protection.                                                                           |
| Copilot CLI (terminal)    | Copilot CLI flags + CLI config home (`~/.copilot`)      | [.devcontainer/copilot/default-flags.txt](../../.devcontainer/copilot/default-flags.txt), [.devcontainer/copilot/copilot-safe](../../.devcontainer/copilot/copilot-safe), [.devcontainer/on-create.sh](../../.devcontainer/on-create.sh), [.devcontainer/.bashrc](../../.devcontainer/.bashrc), [.devcontainer/.zshrc](../../.devcontainer/.zshrc) | `~/.copilot/default-flags.txt`, `~/.local/bin/copilot-safe` | Uses the standard `copilot` command via shell alias to the wrapper. Opt out per call with `COPILOT_CLI_NO_DEFAULT_FLAGS=1`.                 |
| Claude Code (VS Code/CLI) | Claude managed settings JSON (`permissions`, `sandbox`) | [.devcontainer/claude-code/managed-settings.json](../../.devcontainer/claude-code/managed-settings.json)                                                                                                                                                                                                                                           | `/etc/claude-code/managed-settings.json`                    | Copied during container setup by [.devcontainer/on-create.sh](../../.devcontainer/on-create.sh); authors can adjust the repo file directly. |
| Codex CLI                 | Codex TOML config (`sandbox_mode`)                      | [.devcontainer/codex/config.toml](../../.devcontainer/codex/config.toml)                                                                                                                                                                                                                                                                           | `~/.codex/config.toml`                                      | Copied during container setup by [.devcontainer/on-create.sh](../../.devcontainer/on-create.sh); authors can adjust the repo file directly. |
| Gemini                    | Not recommended for this project setup                  | No default VS Code integration configured for this repository                                                                                                                                                                                                                                                                                      | N/A                                                         | Not part of the default devcontainer experience.                                                                                            |

### Practical rule

- Put policy and defaults in vendor config files first.
- Keep markdown instruction files for workflow guidance only.

## Resources

- [GitHub Copilot Best Practices](https://docs.github.com/en/copilot/tutorials/coding-agent/get-the-best-results)
- `AGENTS.md` - Read automatically by Copilot; the single always-loaded instruction file for every agent
- [`.agents/skills/`](../../.agents/skills/README.md) - Task-triggered agent skills. Copilot reads this location
  directly; Claude Code reaches the same files through the `.claude/skills/` symlink
