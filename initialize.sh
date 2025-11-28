#!/usr/bin/env bash
#
# initialize.sh - One-time setup script for HACS Integration Blueprint
#
# This script customizes the blueprint template with your integration details.
# It will automatically delete itself after successful completion.
#
# WARNING: This script can only be run ONCE. After execution, it will be removed.
#
# Usage:
#   ./initialize.sh                                    # Interactive mode
#   ./initialize.sh --dry-run                          # Simulate without changes
#   ./initialize.sh --domain DOMAIN --title TITLE --repo USER/REPO [--force]
#

# Use set -e but we'll handle errors explicitly in critical sections
set -e
set -o pipefail

# Configuration from parameters
DRY_RUN=false
UNATTENDED=false
FORCE=false
PARAM_DOMAIN=""
PARAM_TITLE=""
PARAM_REPO=""
PARAM_AUTHOR=""

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --dry-run|--simulate)
            DRY_RUN=true
            shift
            ;;
        --domain)
            PARAM_DOMAIN="$2"
            UNATTENDED=true
            shift 2
            ;;
        --title)
            PARAM_TITLE="$2"
            UNATTENDED=true
            shift 2
            ;;
        --repo|--repository)
            PARAM_REPO="$2"
            UNATTENDED=true
            shift 2
            ;;
        --author)
            PARAM_AUTHOR="$2"
            UNATTENDED=true
            shift 2
            ;;
        --force)
            FORCE=true
            shift
            ;;
        --help|-h)
            cat << EOF
HACS Integration Blueprint - Initialization Script

Usage:
  ./initialize.sh                                       Interactive mode
  ./initialize.sh --dry-run                             Simulate without changes
  ./initialize.sh [OPTIONS] --force                     Unattended mode

Options:
  --domain DOMAIN           Custom component domain (e.g., my_integration)
  --title TITLE             Integration display title (e.g., "My Integration")
  --repo USER/REPO          GitHub repository (e.g., username/repo-name)
  --author "NAME"            Author name for LICENSE (e.g., "John Doe")
  --force                   Skip confirmation prompts (required for unattended)
  --dry-run, --simulate     Test mode - no actual changes
  --help, -h                Show this help message

Examples:
  # Interactive setup
  ./initialize.sh

  # Dry-run to test
  ./initialize.sh --dry-run

  # Unattended mode (requires --force)
  ./initialize.sh \\
    --domain my_awesome_integration \\
    --title "My Awesome Integration" \\
    --repo myusername/my-hacs-integration \\
    --author "John Doe" \\
    --force

EOF
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Validate unattended mode
if $UNATTENDED && ! $FORCE && ! $DRY_RUN; then
    echo "ERROR: Unattended mode requires --force flag for safety"
    echo "Use --help for usage information"
    exit 1
fi

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Statistics tracking
declare -A file_stats
total_replacements=0

# Print colored output
print_color() {
    local color=$1
    shift
    echo -e "${color}$@${NC}" >&2
}

print_header() {
    echo ""
    print_color "$BLUE" "============================================"
    print_color "$BLUE" "$1"
    print_color "$BLUE" "============================================"
    echo ""
}

print_success() {
    print_color "$GREEN" "✓ $1"
}

print_warning() {
    print_color "$YELLOW" "⚠ $1"
}

print_error() {
    print_color "$RED" "✗ $1"
}

print_dryrun() {
    print_color "$MAGENTA" "🔮 [DRY-RUN] $1"
}

print_info() {
    print_color "$CYAN" "ℹ $1"
}

# Check if this repository is already initialized (not the blueprint template)
check_if_already_initialized() {
    local current_domain
    local git_remote
    local remote_url
    local commit_count

    # Check 1: Is custom_components directory already customized?
    if [[ -d "custom_components" ]] && [[ ! -d "custom_components/ha_integration_domain" ]]; then
        # The template domain doesn't exist, so it's been renamed
        return 0  # Already initialized
    fi

    # Check 2: Does manifest.json have a different domain?
    if [[ -f "custom_components/ha_integration_domain/manifest.json" ]]; then
        current_domain=$(grep -o '"domain"[[:space:]]*:[[:space:]]*"[^"]*"' custom_components/ha_integration_domain/manifest.json | cut -d'"' -f4)
        if [[ -n "$current_domain" ]] && [[ "$current_domain" != "ha_integration_domain" ]]; then
            return 0  # Domain already changed
        fi
    fi

    # Check 3: Check git remote and history
    if git rev-parse --git-dir > /dev/null 2>&1; then
        # Check commit count - "Use this template" creates a repo with minimal history
        commit_count=$(git rev-list --count HEAD 2>/dev/null || echo "0")

        # Get the origin remote URL
        remote_url=$(git remote get-url origin 2>/dev/null || echo "")

        if [[ -z "$remote_url" ]]; then
            # NO REMOTE CONFIGURED!
            # This is suspicious - either:
            # 1. Developer removed .git for testing
            # 2. Someone manually cloned without remote
            # 3. Local development without git
            #
            # We CANNOT determine if this is the blueprint or user repo
            # Be conservative: assume it's already initialized (don't destroy data)
            return 0  # Treat as initialized (safe default)
        fi

        # Remote exists - now we can analyze it
        if [[ "$remote_url" =~ jpawlowski.*integration[_-]?blueprint ]]; then
            # This is the original jpawlowski blueprint repo
            return 1  # Needs initialization (or maintainer is working)
        elif [[ "$remote_url" =~ integration[_-]?blueprint ]]; then
            # This is someone else's fork of the blueprint
            # But if it has only 1-2 commits, it's likely "Use this template"
            if [[ "$commit_count" -le 2 ]]; then
                return 1  # Fresh from template, needs initialization
            fi
            # Otherwise it's a fork with history, probably initialized
            return 0
        else
            # Remote doesn't contain "integration_blueprint"
            # This is likely a user's own repository
            # But if it has only 1 commit, might be fresh from template
            if [[ "$commit_count" -eq 1 ]]; then
                return 1  # Might be fresh template, allow initialization
            fi
            # Otherwise assume it's an established repo
            return 0  # Already initialized
        fi
    else
        # No git repository at all
        # This is very unusual - be conservative
        return 0  # Treat as initialized (safe default)
    fi

    # Check 4: Has README.md been customized? (template has specific header)
    if [[ -f "README.md" ]]; then
        if ! grep -q "Home Assistant Integration Blueprint" README.md; then
            return 0  # README customized, likely initialized
        fi
    fi

    # Default: Assume not initialized (safe default for new users)
    return 1
}

# Display helpful message when repository is already initialized
show_already_initialized_message() {
    local reason="${1:-}"

    print_header "Repository Already Initialized"

    if [[ "$reason" == "no-remote" ]]; then
        print_warning "Cannot determine repository origin - no git remote configured!"
        echo ""
        print_info "This script requires a git remote to safely determine whether initialization is needed."
        echo ""
        print_info "Most likely, your git setup is incomplete. To fix this:"
        echo "   1. Add your repository as remote:"
        echo "      git remote add origin https://github.com/yourusername/your-repo.git"
        echo "   2. Then run: ./initialize.sh"
        echo ""
        print_info "If you're testing without git (developers only):"
        echo "   • Use: ./initialize.sh --dry-run  (to preview changes)"
        echo "   • Use: ./initialize.sh --force    (to run anyway, ⚠️ DESTRUCTIVE)"
    else
        print_info "This repository appears to be already initialized!"
        echo ""
        print_info "This script is only meant to run once in the original blueprint template."
        print_info "If you're working on your own integration repository, you don't need to run this."
    fi

    echo ""

    if [[ -n "${CODESPACES:-}" ]]; then
        print_info "💡 You're in GitHub Codespaces - great! You can now:"
        echo "   • Run 'script/develop' to start Home Assistant"
        echo "   • Run 'script/test' to run tests"
        echo "   • Run 'script/help' to see all available commands"
    else
        print_info "💡 Development commands:"
        echo "   • Run './script/develop' to start Home Assistant"
        echo "   • Run './script/test' to run tests"
        echo "   • Run './script/help' to see all available commands"
    fi

    echo ""
    print_warning "If you really want to re-initialize (⚠️ DESTRUCTIVE), use: ./initialize.sh --force"
    echo ""
}

# Ask yes/no question with default
ask_yes_no() {
    local prompt=$1
    local default=${2:-n}  # Default to 'n' if not specified
    local response

    if [[ "$default" == "y" ]]; then
        prompt="$prompt (Y/n) "
    else
        prompt="$prompt (y/N) "
    fi

    while true; do
        read -p "$prompt" -r response
        response=${response,,}  # Convert to lowercase

        # If empty, use default
        if [[ -z "$response" ]]; then
            response=$default
        fi

        case "$response" in
            y|yes)
                return 0
                ;;
            n|no)
                return 1
                ;;
            *)
                print_warning "Please answer 'y' or 'n'"
                ;;
        esac
    done
}

# Ask for input with validation
ask_input() {
    local prompt=$1
    local allow_empty=${2:-false}
    local response

    while true; do
        read -p "$prompt " -r response

        # Trim leading and trailing whitespace using xargs (most reliable method)
        response=$(echo "$response" | xargs)

        if [[ -n "$response" ]]; then
            printf "%s" "$response"
            return 0
        elif $allow_empty; then
            printf ""
            return 0
        else
            print_warning "Input cannot be empty. Please try again."
        fi
    done
}

# Check requirements
check_requirements() {
    local missing_critical=false
    local missing_optional=()

    print_header "Checking Requirements"

    # Critical: curl or wget
    if ! command -v curl &> /dev/null && ! command -v wget &> /dev/null; then
        print_error "Neither curl nor wget found - required for online checks"
        missing_critical=true
    else
        if command -v curl &> /dev/null; then
            print_success "curl found"
        else
            print_success "wget found"
        fi
    fi

    # Optional but recommended: jq
    if ! command -v jq &> /dev/null; then
        print_warning "jq not found - HACS validation will be limited"
        missing_optional+=("jq")
        echo "   Install with: apt-get install jq  (or brew install jq on macOS)"
    else
        print_success "jq found"
    fi

    # Optional: git
    if ! command -v git &> /dev/null; then
        print_warning "git not found - cannot auto-detect repository"
        missing_optional+=("git")
    else
        print_success "git found"
    fi

    # Check if we're in a git repository
    if command -v git &> /dev/null && [[ -d .git ]]; then
        print_success "Git repository detected"

        # Check for uncommitted changes
        if ! git diff-index --quiet HEAD -- 2>/dev/null; then
            print_warning "You have uncommitted changes in your repository"
            echo "   Consider committing or stashing them before running this script"
            if ! $FORCE && ! $DRY_RUN; then
                if ! ask_yes_no "Continue anyway?"; then
                    print_error "Setup cancelled"
                    exit 1
                fi
            fi
        fi
    fi

    echo ""

    if $missing_critical; then
        print_error "Critical requirements missing - cannot continue"
        exit 1
    fi

    if [[ ${#missing_optional[@]} -gt 0 ]]; then
        print_color "$YELLOW" "Some optional tools are missing. The script will work but with reduced functionality."
        if ! $FORCE && ! $DRY_RUN; then
            if ! ask_yes_no "Continue anyway?"; then
                print_error "Setup cancelled"
                exit 1
            fi
        fi
        echo ""
    fi
}

# Validate domain name format
validate_domain() {
    local domain=$1

    # Check if domain is empty
    if [[ -z "$domain" ]]; then
        print_error "Domain cannot be empty"
        return 1
    fi

    # Check format: lowercase, numbers, underscores only
    if ! [[ "$domain" =~ ^[a-z0-9_]+$ ]]; then
        print_error "Domain must contain only lowercase letters, numbers, and underscores"
        return 1
    fi

    # Check if it starts with a letter
    if ! [[ "$domain" =~ ^[a-z] ]]; then
        print_error "Domain must start with a letter"
        return 1
    fi

    # Check length (Home Assistant recommendation: max 50 chars)
    if [[ ${#domain} -gt 50 ]]; then
        print_error "Domain is too long (max 50 characters)"
        return 1
    fi

    return 0
}

# Check if domain exists online
check_domain_availability() {
    local domain=$1
    local has_curl=false
    local has_wget=false
    local has_jq=false
    local found_conflicts=false

    # Check which tools are available
    if command -v curl &> /dev/null; then
        has_curl=true
    elif command -v wget &> /dev/null; then
        has_wget=true
    else
        print_warning "Neither curl nor wget found - skipping online availability check"
        return 0
    fi

    # Check if jq is available (for JSON parsing)
    if command -v jq &> /dev/null; then
        has_jq=true
    fi

    echo ""
    print_color "$BLUE" "Checking if domain is already in use..."
    echo ""

    # 1. Check Home Assistant Core integrations
    print_color "$BLUE" "→ Checking Home Assistant Core..."
    local core_url="https://raw.githubusercontent.com/home-assistant/core/dev/homeassistant/components/${domain}/manifest.json"

    set +e  # Don't exit on curl/wget errors
    if $has_curl; then
        if curl -s -f -o /dev/null "$core_url" 2>/dev/null; then
            print_error "Domain '$domain' is already used by Home Assistant Core!"
            echo "   See: https://github.com/home-assistant/core/tree/dev/homeassistant/components/${domain}"
            found_conflicts=true
        else
            print_success "Not in Home Assistant Core"
        fi
    elif $has_wget; then
        if wget -q --spider "$core_url" 2>/dev/null; then
            print_error "Domain '$domain' is already used by Home Assistant Core!"
            echo "   See: https://github.com/home-assistant/core/tree/dev/homeassistant/components/${domain}"
            found_conflicts=true
        else
            print_success "Not in Home Assistant Core"
        fi
    fi
    set -e

    # 2. Check HACS integrations via data API
    print_color "$BLUE" "→ Checking HACS Integrations..."
    if $has_jq; then
        local hacs_data_url="https://data-v2.hacs.xyz/integration/data.json"
        local hacs_domains=""

        # Disable exit on error for this section
        set +e
        if $has_curl; then
            hacs_domains=$(curl -s -f "$hacs_data_url" 2>/dev/null | jq -r '.[].domain' 2>/dev/null)
        elif $has_wget; then
            hacs_domains=$(wget -q -O - "$hacs_data_url" 2>/dev/null | jq -r '.[].domain' 2>/dev/null)
        fi
        set -e

        if [[ -n "$hacs_domains" ]]; then
            if echo "$hacs_domains" | grep -q "^${domain}$"; then
                print_error "Domain '$domain' is already used by a HACS integration!"
                echo "   Search HACS: https://hacs.xyz/search/?q=${domain}"
                found_conflicts=true
            else
                print_success "Not in HACS Integrations"
            fi
        else
            print_warning "Could not fetch HACS data (API might be down)"
            echo "   Manual check: https://hacs.xyz/search/?q=${domain}"
        fi
    else
        # Fallback without jq: check repository list only
        print_warning "jq not available - using fallback HACS check"
        local hacs_repo_url="https://raw.githubusercontent.com/hacs/default/master/integration"

        set +e
        if $has_curl; then
            local repos=$(curl -s -f "$hacs_repo_url" 2>/dev/null)
        elif $has_wget; then
            local repos=$(wget -q -O - "$hacs_repo_url" 2>/dev/null)
        fi
        set -e

        if [[ -n "$repos" ]]; then
            # This is a weak check - just searches for domain string in repo list
            # It might give false positives but better than nothing
            if echo "$repos" | grep -qi "$domain"; then
                print_warning "Domain string found in HACS repository list (might be false positive)"
                echo "   Manual verification recommended: https://hacs.xyz/search/?q=${domain}"
            else
                print_success "Not obviously in HACS (limited check without jq)"
            fi
        else
            print_warning "Could not fetch HACS repository list"
            echo "   Manual check: https://hacs.xyz/search/?q=${domain}"
        fi
    fi    # 3. Check GitHub Code Search (best effort - searches for manifest.json with this domain)
    print_color "$BLUE" "→ GitHub Code Search (manual verification recommended):"
    local search_url="https://github.com/search?q=%22domain%22%3A+%22${domain}%22+path%3Amanifest.json+language%3AJSON&type=code"
    echo "   $search_url"

    # 4. Check PyPI (only if it matches the common pattern)
    print_color "$BLUE" "→ Checking PyPI for common package names..."
    local found_pypi=false

    set +e  # Don't exit on curl/wget errors
    for package_name in "homeassistant-${domain}" "hass-${domain}" "${domain}"; do
        local pypi_url="https://pypi.org/pypi/${package_name}/json"
        if $has_curl; then
            if curl -s -f -o /dev/null "$pypi_url" 2>/dev/null; then
                print_warning "Package '${package_name}' exists on PyPI"
                echo "   See: https://pypi.org/project/${package_name}/"
                found_pypi=true
            fi
        elif $has_wget; then
            if wget -q --spider "$pypi_url" 2>/dev/null; then
                print_warning "Package '${package_name}' exists on PyPI"
                echo "   See: https://pypi.org/project/${package_name}/"
                found_pypi=true
            fi
        fi
    done
    set -e

    if ! $found_pypi; then
        print_success "No package name conflicts on PyPI"
    fi

    echo ""
    if $found_conflicts; then
        print_color "$RED" "❌ CONFLICTS DETECTED! This domain is already taken."
        print_color "$YELLOW" "   Please choose a different domain."
        echo ""
        return 1  # Return error code on conflicts
    else
        print_success "✅ No conflicts found - domain appears to be available!"
        echo ""
        return 0  # Return success code
    fi
}

# Detect GitHub repository information
detect_github_info() {
    local git_remote=""

    # Try to get remote URL from git
    if command -v git &> /dev/null && [[ -d .git ]]; then
        git_remote=$(git remote get-url origin 2>/dev/null || echo "")
    fi

    if [[ -n "$git_remote" ]]; then
        # Parse GitHub URL (supports both HTTPS and SSH)
        if [[ "$git_remote" =~ github.com[:/]([^/]+)/([^/]+)(\.git)?$ ]]; then
            echo "${BASH_REMATCH[1]}/${BASH_REMATCH[2]%.git}"
            return 0
        fi
    fi

    return 1
}

# Replace text in files
replace_in_files() {
    local search=$1
    local replace=$2
    local description=$3
    local script_name=$(basename "${BASH_SOURCE[0]}")

    print_color "$BLUE" "Replacing '$search' with '$replace'..."

    # Read .gitignore patterns
    local gitignore_patterns=()
    if [[ -f .gitignore ]]; then
        while IFS= read -r line; do
            # Skip empty lines and comments
            [[ -z "$line" || "$line" =~ ^# ]] && continue
            # Remove leading/trailing whitespace
            line=$(echo "$line" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')
            # Skip negation patterns (!)
            [[ "$line" =~ ^! ]] && continue
            gitignore_patterns+=("$line")
        done < .gitignore
    fi

    # Build find exclude arguments
    local find_args=(-type f)
    for pattern in "${gitignore_patterns[@]}"; do
        # Convert gitignore pattern to find pattern
        # Remove trailing slashes
        pattern="${pattern%/}"
        find_args+=(-not -path "./${pattern}/*" -not -path "./${pattern}")
    done

    # Always exclude .git directory
    find_args+=(-not -path "./.git/*")

    # Exclude this script itself
    find_args+=(-not -name "$script_name")

    # Find and process files
    local files_found=()
    while IFS= read -r -d '' file; do
        # Skip binary files
        if file "$file" | grep -q "text"; then
            files_found+=("$file")
        fi
    done < <(find . "${find_args[@]}" -print0)

    # Replace in each file
    for file in "${files_found[@]}"; do
        if grep -q "$search" "$file" 2>/dev/null; then
            local count=$(grep -o "$search" "$file" | wc -l)

            if $DRY_RUN; then
                print_dryrun "Would replace in $file ($count occurrences)"
            else
                # Perform replacement (macOS and Linux compatible)
                if [[ "$OSTYPE" == "darwin"* ]]; then
                    sed -i '' "s|$search|$replace|g" "$file"
                else
                    sed -i "s|$search|$replace|g" "$file"
                fi
                print_success "  $file ($count occurrences)"
            fi

            # Track statistics
            file_stats["$file"]=$((${file_stats["$file"]:-0} + count))
            total_replacements=$((total_replacements + count))
        fi
    done
}

# Rename directory
rename_directory() {
    local old_path=$1
    local new_path=$2

    if [[ -d "$old_path" ]]; then
        if $DRY_RUN; then
            print_dryrun "Would rename directory: $old_path → $new_path"
        else
            print_color "$BLUE" "Renaming directory: $old_path → $new_path"
            mv "$old_path" "$new_path"
            print_success "Directory renamed"
        fi
    else
        print_warning "Directory $old_path not found, skipping rename"
    fi
}

# Replace README.md with README.template.md
replace_readme_with_template() {
    if [[ ! -f "README.template.md" ]]; then
        print_warning "README.template.md not found, skipping README replacement"
        return
    fi

    if $DRY_RUN; then
        print_dryrun "Would replace README.md with README.template.md"
        print_dryrun "Would remove README.template.md and USING_README_TEMPLATE.md"
    else
        print_color "$BLUE" "Replacing README.md with customized template..."

        # Copy template to README
        cp README.template.md README.md
        print_success "README.md replaced with template"

        # Remove template files
        if [[ -f "README.template.md" ]]; then
            rm -f README.template.md
            print_success "Removed README.template.md"
        fi

        if [[ -f "USING_README_TEMPLATE.md" ]]; then
            rm -f USING_README_TEMPLATE.md
            print_success "Removed USING_README_TEMPLATE.md"
        fi
    fi
}

# Remove post-attach script and devcontainer.json entry
remove_post_attach_script() {
    if $DRY_RUN; then
        print_dryrun "Would remove .devcontainer/post-attach.sh"
        print_dryrun "Would remove postAttachCommand from .devcontainer/devcontainer.json"
    else
        print_color "$BLUE" "Cleaning up initialization scripts..."

        # Remove post-attach.sh
        if [[ -f ".devcontainer/post-attach.sh" ]]; then
            rm -f .devcontainer/post-attach.sh
            print_success "Removed .devcontainer/post-attach.sh"
        fi

        # Remove postAttachCommand from devcontainer.json
        if [[ -f ".devcontainer/devcontainer.json" ]]; then
            local temp_file=$(mktemp)

            # Remove the postAttachCommand line (including trailing comma if present)
            if [[ "$OSTYPE" == "darwin"* ]]; then
                sed -i '' '/^[[:space:]]*"postAttachCommand":/d' .devcontainer/devcontainer.json
            else
                sed -i '/^[[:space:]]*"postAttachCommand":/d' .devcontainer/devcontainer.json
            fi

            print_success "Removed postAttachCommand from devcontainer.json"
        fi
    fi
}

# Display statistics
show_statistics() {
    local header_text="Customization Complete - Statistics"
    if $DRY_RUN; then
        header_text="Dry-Run Complete - Statistics (No Changes Made)"
    fi

    print_header "$header_text"

    echo "Total replacements made: $total_replacements"
    echo ""
    echo "Files modified:"
    echo ""

    # Sort files by number of replacements (descending)
    for file in "${!file_stats[@]}"; do
        echo "${file_stats[$file]} $file"
    done | sort -rn | while read -r count file; do
        printf "  %3d  %s\n" "$count" "$file"
    done

    echo ""

    if $DRY_RUN; then
        print_color "$MAGENTA" "🔮 DRY-RUN MODE: No files were actually modified."
        echo ""
        print_color "$YELLOW" "To apply these changes for real, run without --dry-run flag:"
        echo "  ./initialize.sh"
    else
        print_success "Your integration has been customized successfully!"
        echo ""
        print_color "$YELLOW" "Next steps:"
        echo "  1. Review the changes: git diff"
        echo "  2. Commit your customized integration: git add . && git commit -m 'Initial customization'"
        echo "  3. Start developing your integration!"
    fi
    echo ""
}

# Main execution
main() {
    local header_text="HACS Integration Blueprint - One-Time Setup"
    if $DRY_RUN; then
        header_text="HACS Integration Blueprint - Dry-Run Mode 🔮"
    elif $UNATTENDED; then
        header_text="HACS Integration Blueprint - Unattended Setup"
    fi

    print_header "$header_text"

    # Early exit: Check if repository is already initialized (unless --force)
    if ! $FORCE && ! $DRY_RUN; then
        if check_if_already_initialized; then
            # Check if there's no git remote (special case)
            if git rev-parse --git-dir > /dev/null 2>&1; then
                remote_url=$(git remote get-url origin 2>/dev/null || echo "")
                if [[ -z "$remote_url" ]]; then
                    show_already_initialized_message "no-remote"
                else
                    show_already_initialized_message
                fi
            else
                show_already_initialized_message
            fi
            exit 0
        fi
    fi

    if $DRY_RUN; then
        print_color "$MAGENTA" "🔮 DRY-RUN MODE ACTIVE"
        print_color "$MAGENTA" "   No files will be modified, and this script will not be deleted."
        echo ""
    fi

    # Check requirements before proceeding
    check_requirements

    if ! $UNATTENDED; then
        print_color "$YELLOW" "⚠ WARNING: This script will modify files and delete itself after completion."
        print_color "$YELLOW" "           Make sure you have committed or backed up any changes."
        echo ""

        if ! $DRY_RUN; then
            if ! ask_yes_no "Continue?"; then
                print_error "Setup cancelled"
                exit 1
            fi
        fi
    fi

    local domain=""
    local title=""
    local github_repo=""

    # Handle unattended mode with parameters
    if $UNATTENDED; then
        print_header "Validating Parameters"

        # Validate domain
        if [[ -z "$PARAM_DOMAIN" ]]; then
            print_error "Missing required parameter: --domain"
            exit 1
        fi
        if ! validate_domain "$PARAM_DOMAIN"; then
            exit 1
        fi
        domain="$PARAM_DOMAIN"
        print_success "Domain: $domain"

        # Validate title
        if [[ -z "$PARAM_TITLE" ]]; then
            print_error "Missing required parameter: --title"
            exit 1
        fi
        title="$PARAM_TITLE"
        print_success "Title: $title"

        # Validate repository
        if [[ -z "$PARAM_REPO" ]]; then
            # Try to detect from git
            local detected_repo=$(detect_github_info)
            if [[ -n "$detected_repo" ]]; then
                github_repo="$detected_repo"
                print_success "Repository: $github_repo (auto-detected)"
            else
                print_error "Missing required parameter: --repo (and could not auto-detect)"
                exit 1
            fi
        else
            if [[ ! "$PARAM_REPO" =~ ^[a-zA-Z0-9_-]+/[a-zA-Z0-9_.-]+$ ]]; then
                print_error "Invalid repository format: $PARAM_REPO (use: username/repository)"
                exit 1
            fi
            github_repo="$PARAM_REPO"
            print_success "Repository: $github_repo"
        fi

        # Validate author
        local author_name=""
        local github_username="${github_repo%%/*}"
        if [[ -z "$PARAM_AUTHOR" ]]; then
            print_warning "No author name provided, using GitHub username as fallback"
            author_name="$github_username"
        else
            author_name="$PARAM_AUTHOR"
        fi
        print_success "Author: $author_name @$github_username"

        # Check domain availability (abort on conflicts in unattended mode)
        if ! check_domain_availability "$domain"; then
            print_error "Domain conflicts detected. Unattended mode requires conflict-free domain."
            print_error "Use interactive mode to override conflicts, or choose a different domain."
            exit 1
        fi

        # Show summary and confirm (unless --force)
        print_header "Configuration Summary"
        echo "Domain:     $domain"
        echo "Title:      $title"
        echo "Repository: $github_repo"
        echo "Author:     $author_name @$github_username"
        echo ""

        if ! $FORCE && ! $DRY_RUN; then
            print_color "$YELLOW" "Ready to apply changes. This will modify files and delete this script."
            if ! ask_yes_no "Proceed?"; then
                print_error "Setup cancelled"
                exit 1
            fi
        elif $FORCE && ! $DRY_RUN; then
            print_color "$GREEN" "FORCE mode enabled - proceeding without confirmation"
            sleep 1  # Brief pause for visibility
        fi
    else
        # Interactive mode - original flow
        # Step 1: Get custom component domain
        print_header "Step 1: Custom Component Domain"
        echo "Enter your unique Home Assistant custom component domain."
        echo "Format: lowercase letters, numbers, and underscores only"
        echo "Example: my_awesome_integration"
        echo ""

        while true; do
            domain=$(ask_input "Domain:")
            if validate_domain "$domain"; then
                if check_domain_availability "$domain"; then
                    # No conflicts - accept domain automatically
                    break
                else
                    # Conflicts found - ask if user wants to use it anyway
                    if ask_yes_no "Use this domain anyway?"; then
                        print_warning "Proceeding with conflicting domain - this may cause issues!"
                        break
                    else
                        print_error "Domain selection cancelled. Please restart the script."
                        exit 1
                    fi
                fi
            fi
        done

        # Step 2: Get integration title
        print_header "Step 2: Integration Title"
        echo "Enter the display name for your integration (can contain spaces and special characters)."
        echo "Example: My Awesome Integration"
        echo ""

        title=$(ask_input "Title:")

        # Step 3: Get GitHub repository info
        print_header "Step 3: GitHub Repository"

        local detected_repo=$(detect_github_info)

        if [[ -n "$detected_repo" ]]; then
            print_success "Detected repository: $detected_repo"
            if ask_yes_no "Use this repository?" "y"; then
                github_repo="$detected_repo"
            fi
        fi

        if [[ -z "$github_repo" ]]; then
            echo "Enter your GitHub repository in format: username/repository"
            echo "Example: myusername/my-hacs-integration"
            echo ""

            while true; do
                github_repo=$(ask_input "GitHub Repository:")
                if [[ "$github_repo" =~ ^[a-zA-Z0-9_-]+/[a-zA-Z0-9_.-]+$ ]]; then
                    break
                else
                    print_error "Invalid format. Use: username/repository"
                fi
            done
        fi

        # Step 4: Get author information
        print_header "Step 4: Author Information"
        echo "This information will be used in the LICENSE file."
        echo "You can use your real name or an alias."
        echo ""

        # Extract GitHub username from repository
        local github_username="${github_repo%%/*}"
        print_success "GitHub username: $github_username"
        echo ""

        local author_name=$(ask_input "Your name (or alias):")

        # Step 5: Confirmation
        print_header "Step 5: Confirm Settings"
        echo "Domain:     $domain"
        echo "Title:      $title"
        echo "Repository: $github_repo"
        echo "Author:     $author_name @$github_username"
        echo ""
        if ! ask_yes_no "Proceed with these settings?"; then
            print_error "Setup cancelled"
            exit 1
        fi
    fi

    # Perform replacements
    local step_prefix=""
    if ! $UNATTENDED; then
        step_prefix="Step 5: "
    fi
    print_header "${step_prefix}Applying Changes"

    # Replace domain
    replace_in_files "ha_integration_domain" "$domain" "domain name"

    # Replace title (handle both cases)
    replace_in_files "Integration Blueprint" "$title" "integration title"
    replace_in_files "Integration blueprint" "$title" "integration title (lowercase)"

    # Replace GitHub repository
    replace_in_files "jpawlowski/hacs.integration_blueprint" "$github_repo" "GitHub repository"

    # Extract GitHub username and replace it separately (for badges and URLs)
    local github_username="${github_repo%%/*}"
    replace_in_files "@jpawlowski" "@$github_username" "GitHub username"
    replace_in_files "%40jpawlowski" "%40$github_username" "GitHub username (URL-encoded)"

    # Replace LICENSE author
    replace_in_files "Julian Pawlowski @jpawlowski" "$author_name @$github_username" "LICENSE author"

    # Replace year in LICENSE with current year
    local current_year=$(date +%Y)
    replace_in_files "2025" "$current_year" "LICENSE year"

    # Rename directory
    rename_directory "custom_components/ha_integration_domain" "custom_components/$domain"

    # Replace README with template
    replace_readme_with_template

    # Remove post-attach script and devcontainer.json entry
    remove_post_attach_script

    # Step 6: Show statistics
    show_statistics

    # Step 7: Self-destruct
    if $DRY_RUN; then
        print_color "$MAGENTA" "🔮 Dry-run complete - script NOT deleted"
        print_color "$GREEN" "Simulation complete! 🎭"
    else
        print_color "$YELLOW" "Removing initialization script..."
        local script_path="${BASH_SOURCE[0]}"

        # Create a small self-deleting wrapper
        (
            sleep 1
            rm -f "$script_path"
            print_success "Initialization script removed"
        ) &

        print_color "$GREEN" "Setup complete! 🎉"
    fi
    exit 0
}

# Run main function
main "$@"
