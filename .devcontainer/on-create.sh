#!/usr/bin/env bash
#
# .devcontainer/on-create.sh - DevContainer On-Create Hook
#
# Runs once when the container is first created, before postCreateCommand.
# Fixes ownership of named Docker volume mount points that Docker initializes
# as root:root so that subsequent scripts (pipx, uv, bootstrap) can write to
# ~/.local and ~/.cache without permission errors.
#
# Customization:
#   Create .devcontainer/hooks/on-create.pre.sh  — runs before ownership fix
#   Create .devcontainer/hooks/on-create.post.sh — runs after ownership fix
#

set -e

CYAN='\033[0;36m'
NC='\033[0m'

print_info() {
    echo -e "${CYAN}ℹ $1${NC}" >&2
}

# Load DevContainer environment overrides (.env → .env.local, later wins).
# Makes HA_VERSION and other vars available in this script and user hooks.
# shellcheck source=.devcontainer/_load_env.sh
source "$(cd "$(dirname "$0")" && pwd)/_load_env.sh"

# Run pre-hook if present
_hook_file="$(cd "$(dirname "$0")" && pwd)/hooks/on-create.pre.sh"
if [[ -f "$_hook_file" ]]; then
    print_info "Running hook: .devcontainer/hooks/on-create.pre.sh"
    # shellcheck source=/dev/null
    source "$_hook_file"
fi
unset _hook_file

# Fix ownership of named volume mount points.
# Docker creates each volume mount point as root:root when the container starts.
# Volumes are now mounted directly under $HOME (ha-venv and uv-cache) so Docker
# does NOT create ~/.local or ~/.cache as root — VS Code server can write there freely.
print_info "Fixing ownership of Docker volume mount points..."
sudo chown vscode:vscode \
    /home/vscode/ha-venv \
    /home/vscode/uv-cache

# Disable Claude Code's built-in Bash sandbox inside the devcontainer.
# The devcontainer's own Docker/OrbStack runtime blocks unprivileged user
# namespace creation entirely (not just the fresh /proc mount bubblewrap's
# "weaker nested sandbox" mode works around), so bubblewrap cannot start
# here at all. The devcontainer itself is already the isolation boundary,
# which Anthropic documents as an equivalent alternative to the built-in
# sandbox — see https://code.claude.com/docs/en/sandbox-environments.
#
# Written to /etc/claude-code/managed-settings.json (not a repo file) so it
# only applies inside this container: that path lives on the container's own
# filesystem, not the bind-mounted workspace, so opening this repo outside
# the devcontainer never picks it up.
print_info "Disabling Claude Code's Bash sandbox (devcontainer is the isolation boundary)..."
sudo mkdir -p /etc/claude-code
sudo tee /etc/claude-code/managed-settings.json >/dev/null <<'EOF'
{
  "sandbox": {
    "enabled": false
  }
}
EOF

# Disable Codex CLI's built-in sandbox inside the devcontainer, for the same
# reason as Claude Code above: bubblewrap/seccomp can't create the namespaces
# it needs here, and the devcontainer itself is already the isolation boundary.
#
# Written to ~/.codex/config.toml (user scope, not a repo file) so it only
# applies inside this container's home directory, never on the bare host.
# A project-scoped .codex/config.toml (if one is ever added to the repo) can
# override this per-key, but only by explicitly setting sandbox_mode itself.
print_info "Disabling Codex CLI's sandbox (devcontainer is the isolation boundary)..."
mkdir -p /home/vscode/.codex
tee /home/vscode/.codex/config.toml >/dev/null <<'EOF'
sandbox_mode = "danger-full-access"
EOF

# Run post-hook if present
_hook_file="$(cd "$(dirname "$0")" && pwd)/hooks/on-create.post.sh"
if [[ -f "$_hook_file" ]]; then
    print_info "Running hook: .devcontainer/hooks/on-create.post.sh"
    # shellcheck source=/dev/null
    source "$_hook_file"
fi
unset _hook_file
