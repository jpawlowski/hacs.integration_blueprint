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

# Run post-hook if present
_hook_file="$(cd "$(dirname "$0")" && pwd)/hooks/on-create.post.sh"
if [[ -f "$_hook_file" ]]; then
    print_info "Running hook: .devcontainer/hooks/on-create.post.sh"
    # shellcheck source=/dev/null
    source "$_hook_file"
fi
unset _hook_file
