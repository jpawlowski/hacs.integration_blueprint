#!/usr/bin/env bash
# shellcheck shell=bash
# Smart merge functions for structured files (JSON, YAML, TOML)
set -euo pipefail

# Source output library if not already sourced
if ! declare -F log_error &>/dev/null; then
    MERGE_LIB_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    # shellcheck source=script/.lib/output.sh
    source "$MERGE_LIB_DIR/output.sh"
fi

# ============================================================================
# ADDITIVE MERGE STRATEGY (User + Blueprint, User wins on conflicts)
# ============================================================================
# This is the preferred strategy for files that users customize.
# - User's values always take priority
# - Blueprint adds new keys that user doesn't have
# - User's comments are preserved (in YAML)
# - User's custom keys are never deleted
# ============================================================================

# Merge JSON with additive strategy (user priority)
# Usage: merge_json_additive SOURCE_FILE TARGET_FILE > MERGED_FILE
merge_json_additive() {
    local source_file="$1"
    local target_file="$2"

    if [[ ! -f "${source_file}" ]]; then
        log_error "Source file not found: ${source_file}"
        return 1
    fi

    if [[ ! -f "${target_file}" ]]; then
        log_warning "Target file not found, using source: ${target_file}"
        cat "${source_file}"
        return 0
    fi

    # Additive merge: source * target (target wins)
    # Uses yq for better deep merge support
    yq eval-all 'select(fileIndex == 0) * select(fileIndex == 1)' \
        "${source_file}" "${target_file}"
}

# Merge YAML with additive strategy (user priority, preserves comments)
# Usage: merge_yaml_additive SOURCE_FILE TARGET_FILE > MERGED_FILE
merge_yaml_additive() {
    local source_file="$1"
    local target_file="$2"

    if [[ ! -f "${source_file}" ]]; then
        log_error "Source file not found: ${source_file}"
        return 1
    fi

    if [[ ! -f "${target_file}" ]]; then
        log_warning "Target file not found, using source: ${target_file}"
        cat "${source_file}"
        return 0
    fi

    # Check if yq is available
    if ! command -v yq &> /dev/null; then
        log_error "yq is required for YAML merging but not installed"
        log_info "Install: Add yq-go feature in devcontainer"
        return 1
    fi

    # Additive merge: source * target (target wins, comments preserved)
    yq eval-all 'select(fileIndex == 0) * select(fileIndex == 1)' \
        "${source_file}" "${target_file}"
}

# ============================================================================
# SELECTIVE MERGE STRATEGY (Preserve specific keys from target)
# ============================================================================
# Legacy strategy - use additive merge instead where possible
# ============================================================================

# Merge JSON files preserving specified keys from target
# Usage: merge_json SOURCE_FILE TARGET_FILE KEEP_KEYS... > MERGED_FILE
merge_json() {
    local source_file="$1"
    local target_file="$2"
    shift 2
    local keep_keys=("$@")

    if [[ ! -f "${source_file}" ]]; then
        log_error "Source file not found: ${source_file}"
        return 1
    fi

    if [[ ! -f "${target_file}" ]]; then
        log_warning "Target file not found, using source: ${target_file}"
        cat "${source_file}"
        return 0
    fi

    # Build jq filter to preserve keys
    local jq_filter='.'
    if [[ ${#keep_keys[@]} -gt 0 ]]; then
        # Save values from target
        local save_filter='{'
        for key in "${keep_keys[@]}"; do
            save_filter="${save_filter}\"${key}\": .${key},"
        done
        save_filter="${save_filter%,}}"

        # Merge: source + saved target values
        jq_filter="input as \$target | . * (\$target | ${save_filter})"
    fi

    jq "${jq_filter}" "${source_file}" "${target_file}"
}

# Merge YAML files preserving specified keys from target
# Usage: merge_yaml SOURCE_FILE TARGET_FILE KEEP_KEYS... > MERGED_FILE
merge_yaml() {
    local source_file="$1"
    local target_file="$2"
    shift 2
    local keep_keys=("$@")

    if [[ ! -f "${source_file}" ]]; then
        log_error "Source file not found: ${source_file}"
        return 1
    fi

    if [[ ! -f "${target_file}" ]]; then
        log_warning "Target file not found, using source: ${target_file}"
        cat "${source_file}"
        return 0
    fi

    # Check if yq is available
    if ! command -v yq &> /dev/null; then
        log_error "yq is required for YAML merging but not installed"
        log_info "Install: pip install yq"
        return 1
    fi

    # Build yq filter to preserve keys
    local yq_filter='.'
    if [[ ${#keep_keys[@]} -gt 0 ]]; then
        # Save values from target
        local save_expressions=()
        for key in "${keep_keys[@]}"; do
            save_expressions+=(".[\"${key}\"] = \$target.${key}")
        done

        # Merge: source + saved target values
        local save_filter=$(IFS=' | '; echo "${save_expressions[*]}")
        yq_filter=". * \$target | ${save_filter}"
    fi

    yq --yaml-output "${yq_filter}" --slurpfile target "${target_file}" "${source_file}"
}

# Smart merge dispatcher based on file extension and strategy
# Usage: smart_merge SOURCE_FILE TARGET_FILE [STRATEGY] [KEEP_KEYS...]
smart_merge() {
    local source_file="$1"
    local target_file="$2"
    local strategy="${3:-additive}"  # Default to additive

    # Shift arguments safely
    if [[ $# -ge 3 ]]; then
        shift 3
    else
        shift 2
    fi
    local keep_keys=("$@")

    local extension="${target_file##*.}"

    # Use additive strategy by default (user priority)
    if [[ "${strategy}" == "additive" || -z "${strategy}" ]]; then
        case "${extension}" in
            json)
                merge_json_additive "${source_file}" "${target_file}"
                ;;
            yaml|yml)
                merge_yaml_additive "${source_file}" "${target_file}"
                ;;
            *)
                log_error "Unsupported file type for smart merge: ${extension}"
                log_info "Supported: json, yaml, yml"
                return 1
                ;;
        esac
    # Fallback to selective merge (legacy, needs keep_keys)
    elif [[ "${strategy}" == "selective" ]]; then
        case "${extension}" in
            json)
                merge_json "${source_file}" "${target_file}" "${keep_keys[@]}"
                ;;
            yaml|yml)
                merge_yaml "${source_file}" "${target_file}" "${keep_keys[@]}"
                ;;
            *)
                log_error "Unsupported file type for smart merge: ${extension}"
                return 1
                ;;
        esac
    else
        log_error "Unknown merge strategy: ${strategy}"
        log_info "Supported strategies: additive (default), selective"
        return 1
    fi
}

# Merge JSON with deep merge (nested objects)
# Usage: merge_json_deep SOURCE_FILE TARGET_FILE KEEP_PATHS... > MERGED_FILE
# KEEP_PATHS can be nested like "project.name" or "tool.ruff.line-length"
merge_json_deep() {
    local source_file="$1"
    local target_file="$2"
    shift 2
    local keep_paths=("$@")

    if [[ ! -f "${source_file}" ]]; then
        log_error "Source file not found: ${source_file}"
        return 1
    fi

    if [[ ! -f "${target_file}" ]]; then
        log_warning "Target file not found, using source: ${target_file}"
        cat "${source_file}"
        return 0
    fi

    # Build jq filter for deep merge with preserved paths
    if [[ ${#keep_paths[@]} -eq 0 ]]; then
        # Simple merge without preservation
        jq -s '.[0] * .[1]' "${source_file}" "${target_file}"
        return 0
    fi

    # Build path preservation logic
    local preserve_filter='input as $target | '
    local first=true

    for path in "${keep_paths[@]}"; do
        if [[ "${first}" == "true" ]]; then
            preserve_filter="${preserve_filter}. * {}"
            first=false
        fi

        # Convert "a.b.c" to nested object: {a: {b: {c: $target.a.b.c}}}
        local jq_path=".${path}"
        preserve_filter="${preserve_filter} | setpath([\"${path//./\",\"}\"]; \$target${jq_path})"
    done

    jq "${preserve_filter}" "${source_file}" "${target_file}"
}

# Extract value from JSON at path
# Usage: json_get_path FILE PATH
json_get_path() {
    local file="$1"
    local path="$2"

    if [[ ! -f "${file}" ]]; then
        return 1
    fi

    jq -r ".${path} // empty" "${file}" 2>/dev/null || true
}

# Set value in JSON at path
# Usage: json_set_path FILE PATH VALUE > NEWFILE
json_set_path() {
    local file="$1"
    local path="$2"
    local value="$3"

    if [[ ! -f "${file}" ]]; then
        log_error "File not found: ${file}"
        return 1
    fi

    # Handle different value types
    local jq_value
    if [[ "${value}" =~ ^[0-9]+$ ]]; then
        # Number
        jq_value="${value}"
    elif [[ "${value}" == "true" || "${value}" == "false" ]]; then
        # Boolean
        jq_value="${value}"
    elif [[ "${value}" =~ ^\[.*\]$ || "${value}" =~ ^\{.*\}$ ]]; then
        # Array or Object (already JSON)
        jq_value="${value}"
    else
        # String
        jq_value="\"${value}\""
    fi

    jq ".${path} = ${jq_value}" "${file}"
}
