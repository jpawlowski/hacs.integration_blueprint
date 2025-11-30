# GitHub Codespaces Development Guide

Integration blueprint is fully compatible with GitHub Codespaces for cloud-based development.

## Quick Start

### Initial Setup (Template Users)

1. Click "Code" → "Codespaces" → "Create codespace on main"
2. Wait 2-3 minutes for automated setup
3. **Run `./initialize.sh`** in the terminal to configure your integration
4. Follow the prompts to customize your integration
5. Start developing!

### Testing Copilot Agent Changes

When testing a pull request created by GitHub Copilot Coding Agent:

1. Open the PR on GitHub
2. Click "Code" → "Create codespace on `branch-name`"
3. Run `./script/develop` to start Home Assistant
4. Test the integration in the browser (port 8123 forwards automatically)

For the complete Copilot Agent workflow, see [COPILOT_AGENT.md](COPILOT_AGENT.md).

## What Works Automatically

- ✅ Git configuration with your GitHub account
- ✅ Port forwarding for Home Assistant (port 8123)
- ✅ All VS Code extensions pre-installed
- ✅ Python 3.13 environment with dependencies
- ✅ Home Assistant + HACS ready to use
- ✅ All development scripts work identically

## Key Differences from Local Development

### Port Access

When running `script/develop`, Home Assistant starts on port 8123:

- **Codespaces**: Forwarded URL with notification (e.g., `https://username-repo-xyz.github.dev`)
- **Local**: Direct access at `http://localhost:8123`

### Git Configuration

- **Codespaces**: Automatically configured with your GitHub account
- **Local**: Uses your host machine's `.gitconfig`

### Performance

- Runs on GitHub's cloud servers (usually fast)
- 2-4 core machines available
- 60 hours/month free for personal accounts
- For intensive testing, consider upgrading or local development

## Managing Resources

### Save Your Free Hours

- **Stop** your Codespace when not developing (Settings → Stop Codespace)
- Auto-stops after 30 minutes of inactivity (default)
- All work is saved when stopped!

### Persistent Storage

- Workspace files persist between stops/starts
- Git changes are preserved
- Home Assistant config and HACS persist

### Multiple Projects

Each repository gets its own Codespace - work on multiple integrations simultaneously without conflicts.

## Troubleshooting

### Codespace Won't Start

- Verify Codespaces is enabled for your account
- Check available hours (Settings → Billing)

### Port 8123 Not Forwarding

- Check "Ports" tab in VS Code terminal panel
- Manually forward if needed: Right-click → "Forward Port"

### Git Push Authentication

- Codespaces uses GitHub authentication automatically
- If prompted, choose "GitHub" as method

## Resources

- [GitHub Codespaces Documentation](https://docs.github.com/en/codespaces)
- [Codespaces Pricing](https://docs.github.com/en/billing/managing-billing-for-github-codespaces/about-billing-for-github-codespaces)
