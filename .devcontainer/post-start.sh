#!/usr/bin/env bash
#
# .devcontainer/post-start.sh - DevContainer Post-Start Hook
#
# Runs every time the container starts (including after a stop/restart),
# but NOT on every client attach. Use this for actions that should happen
# once per container start: activating services, checking for stale state, etc.
#
# Execution order: onCreateCommand → postCreateCommand → postStartCommand → postAttachCommand
#
# Customization:
#   Create .devcontainer/hooks/post-start.pre.sh  — runs at start of this script
#   Create .devcontainer/hooks/post-start.post.sh — runs at end of this script
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
_hook_file="$(cd "$(dirname "$0")" && pwd)/hooks/post-start.pre.sh"
if [[ -f "$_hook_file" ]]; then
    print_info "Running hook: .devcontainer/hooks/post-start.pre.sh"
    # shellcheck source=/dev/null
    source "$_hook_file"
fi
unset _hook_file

# Run post-hook if present
_hook_file="$(cd "$(dirname "$0")" && pwd)/hooks/post-start.post.sh"
if [[ -f "$_hook_file" ]]; then
    print_info "Running hook: .devcontainer/hooks/post-start.post.sh"
    # shellcheck source=/dev/null
    source "$_hook_file"
fi
unset _hook_file
