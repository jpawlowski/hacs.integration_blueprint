# GitHub Codespaces Notes

This integration blueprint is fully compatible with GitHub Codespaces!

## What works automatically

✅ **Git configuration** - Your GitHub account is automatically configured
✅ **Port forwarding** - Port 8123 (Home Assistant) forwards automatically with notifications
✅ **Extensions** - All VS Code extensions install automatically
✅ **Python environment** - Python 3.13 with all dependencies pre-installed
✅ **Home Assistant** - Full HA installation with HACS ready to use
✅ **Scripts** - All development scripts work identically to local development

## Quick Start in Codespaces

1. Click "Code" → "Codespaces" → "Create codespace on main"
2. Wait 2-3 minutes for setup to complete
3. Run `./initialize.sh` when the terminal is ready
4. Review changes and commit

## Differences from Local Development

### Git Configuration

- **Local**: Uses your host machine's `.gitconfig`
- **Codespaces**: Automatically configured with your GitHub account
- Both work seamlessly!

### Port Access

When you run `script/develop`, Home Assistant starts on port 8123:

- **Codespaces**: You'll get a notification with a forwarded URL (e.g., `https://username-repo-12345.github.dev`)
- **Local**: Access directly at `http://localhost:8123`

### Performance

- Codespaces runs on GitHub's servers (usually fast!)
- 2-4 core machines available (60 hours/month free on personal accounts)
- For intensive testing, consider upgrading to 4-core or developing locally

## Tips for Codespaces Users

### Save Your Free Hours

- **Stop** your Codespace when not actively developing (Settings → Stop Codespace)
- Codespaces auto-stop after 30 minutes of inactivity by default
- Your work is saved even when stopped!

### Persistent Storage

- Your workspace files persist between Codespace stops/starts
- Git changes are preserved
- The HA config and HACS installation persist too

### Working with Multiple Integrations

Each repository gets its own Codespace, so you can work on multiple integrations simultaneously without conflicts.

## Troubleshooting

### Codespace won't start

- Check your GitHub account has Codespaces enabled
- Verify you have available hours (Settings → Billing)

### Port 8123 not forwarding

- Check the "Ports" tab in the VS Code terminal panel
- Manually forward if needed: Right-click → "Forward Port"

### Git push requires authentication

- Codespaces uses GitHub's authentication automatically
- If prompted, choose "GitHub" as authentication method

## More Information

- [Codespaces Documentation](https://docs.github.com/en/codespaces)
- [Codespaces Pricing](https://docs.github.com/en/billing/managing-billing-for-github-codespaces/about-billing-for-github-codespaces)
