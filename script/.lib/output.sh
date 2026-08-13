#!/bin/bash
# Output formatting library for consistent script styling
# Source this file in your scripts with: source "$(dirname "$0")/../.lib/output.sh"
# shellcheck disable=SC2034  # All variables in this library are used by sourcing scripts

readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly BLUE='\033[0;34m'
readonly MAGENTA='\033[0;35m'
readonly CYAN='\033[0;36m'
readonly BOLD='\033[1m'
readonly DIM='\033[2m'
readonly NC='\033[0m' # No Color

readonly CHECK='✓'
readonly CROSS='✗'
readonly ARROW='→'
readonly INFO='ℹ'
readonly WARNING='⚠'
# shellcheck disable=SC2034  # These symbols are available to sourcing scripts
readonly ROCKET='🚀'
readonly PACKAGE='📦'
readonly WRENCH='🔧'
readonly SPARKLES='✨'
readonly BUG='🐛'
readonly BOOKS='📚'

log_header() {
    printf "\n%b==> %b%b\n" "$BOLD$BLUE" "$1" "$NC"
}

log_success() {
    printf "%b%s %b%b\n" "$GREEN" "$CHECK" "$1" "$NC"
}

log_error() {
    printf "%b%s %b%b\n" "$RED" "$CROSS" "$1" "$NC" >&2
}

log_warning() {
    printf "%b%s %b%b\n" "$YELLOW" "$WARNING" "$1" "$NC"
}

log_info() {
    printf "%b%s %b%b\n" "$CYAN" "$INFO" "$1" "$NC"
}

log_step() {
    printf "    %b%s%b %b\n" "$DIM" "$ARROW" "$NC" "$1"
}

log_result() {
    local status=$1
    shift
    if [[ $status -eq 0 ]]; then
        printf "    %b%s %s%b\n" "$GREEN" "$CHECK" "$*" "$NC"
    else
        printf "    %b%s %s%b\n" "$RED" "$CROSS" "$*" "$NC"
    fi
}

log_separator() {
    printf "%b%s%b\n" "$DIM" "────────────────────────────────────────────────────────────" "$NC"
}

die() {
    log_error "$1"
    exit "${2:-1}"
}

require_command() {
    local cmd=$1
    local install_hint=${2:-""}

    if ! command -v "$cmd" >/dev/null 2>&1; then
        log_error "Required command not found: $cmd"
        if [[ -n $install_hint ]]; then
            log_info "Install with: $install_hint"
        fi
        exit 1
    fi
}

# Print the path of the virtual environment this environment should use.
# Returns 1 and prints nothing when none exists.
#
# The location must agree with script/setup/bootstrap, which creates and
# maintains it: DevContainer and Codespaces keep the venv in $HOME (a named
# volume), GitHub Actions and local development keep it in the workspace.
# Preferring $HOME/ha-venv unconditionally fails quietly in the one case that
# matters: a leftover $HOME/ha-venv from an earlier DevContainer session
# outranks the workspace venv that bootstrap actually updates, so every script
# keeps running against a stale Home Assistant version while looking perfectly
# healthy. Fall back to the other locations, but say so.
resolve_venv_path() {
    local preferred candidate
    if [[ -n ${REMOTE_CONTAINERS:-} || -n ${CODESPACES:-} ]]; then
        preferred="$HOME/ha-venv"
    elif [[ -n ${GITHUB_ACTIONS:-} ]]; then
        preferred="${GITHUB_WORKSPACE:-.}/.local/ha-venv"
    else
        preferred="$PWD/.local/ha-venv"
    fi

    if [[ -f "$preferred/bin/activate" ]]; then
        printf '%s' "$preferred"
        return 0
    fi

    for candidate in "$HOME/ha-venv" "$PWD/.local/ha-venv" "$HOME/.local/ha-venv"; do
        if [[ "$candidate" != "$preferred" && -f "$candidate/bin/activate" ]]; then
            # To stderr: this function's stdout is the resolved path.
            log_warning "Expected the virtual environment at $preferred, using $candidate instead — run script/setup/bootstrap to rebuild it where this environment looks for it" >&2
            printf '%s' "$candidate"
            return 0
        fi
    done

    return 1
}

# Activate the Home Assistant virtual environment if not already active.
# Silently skips when VIRTUAL_ENV is already set (e.g. in CI or nested calls).
activate_venv() {
    if [[ -n ${VIRTUAL_ENV:-} ]]; then
        return 0
    fi
    local venv_path
    if ! venv_path="$(resolve_venv_path)"; then
        log_error "Virtual environment not found. Run: script/setup/bootstrap"
        exit 1
    fi
    log_header "Activating virtual environment"
    # shellcheck source=/dev/null
    source "$venv_path/bin/activate"
}

# Run a user-defined hook script if it exists.
# Hooks live in script/user/<name>.<phase>.sh and are sourced (not executed),
# so they can read and set variables in the calling script's environment.
#
# Usage:  run_hook <script-name> <phase>
# Phases: pre | post
#
# Example — in script/develop:
#   run_hook "develop" "pre"
#
# The user creates script/user/develop.pre.sh to customize behavior.
# SCRIPT_DIR must be set in the calling script before sourcing output.sh.
run_hook() {
    local script_name="$1"
    local phase="$2"
    local hook_file="script/hooks/${script_name}.${phase}.sh"
    if [[ -f "$hook_file" ]]; then
        log_info "Running hook: script/hooks/${script_name}.${phase}.sh"
        # shellcheck source=/dev/null
        source "$hook_file"
    fi
}
