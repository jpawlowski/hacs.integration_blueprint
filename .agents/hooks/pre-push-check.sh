#!/bin/bash

# .agents/hooks/pre-push-check.sh: Validate the exact clean worktree before git push
#
# Reads a PreToolUse payload on stdin. Non-push calls pass through; pushes from
# ambiguous commands, dirty worktrees, or a ref other than the current HEAD are blocked.
#
# Usage:
#   .agents/hooks/pre-push-check.sh
#   .agents/hooks/pre-push-check.sh --explain < payload.json

set -euo pipefail

explain=0
if [[ ${1:-} == "--explain" ]]; then
    explain=1
fi

block() {
    if [[ $explain -eq 1 ]]; then
        echo "BLOCK $1"
        exit 0
    fi
    echo "BLOCKED: $1" >&2
    exit 2
}

allow() {
    if [[ $explain -eq 1 ]]; then
        echo "ALLOW"
    fi
    exit 0
}

payload=$(cat)
if ! command -v jq >/dev/null 2>&1 || ! command -v python3 >/dev/null 2>&1; then
    if [[ $payload == *git*push* ]]; then
        block "jq and python3 are required to vet this push"
    fi
    allow
fi

parsed=$(
    HOOK_PAYLOAD="$payload" python3 <<'PY'
import json
import os
import re
import shlex

try:
    payload = json.loads(os.environ["HOOK_PAYLOAD"])
except (KeyError, json.JSONDecodeError):
    print(json.dumps({"status": "block", "reason": "the hook payload is not valid JSON"}))
    raise SystemExit

tool_input = payload.get("tool_input", {})
if isinstance(tool_input, str):
    command = tool_input
    input_cwd = ""
elif isinstance(tool_input, dict):
    command = tool_input.get("command") or tool_input.get("cmd") or ""
    input_cwd = tool_input.get("cwd") or tool_input.get("workdir") or ""
else:
    command = ""
    input_cwd = ""

if isinstance(command, list):
    command = shlex.join(str(part) for part in command)
if not isinstance(command, str):
    command = str(command)

cwd = payload.get("cwd") or input_cwd or os.getcwd()


def tokenize(command):
    lexer = shlex.shlex(command, posix=True, punctuation_chars=";&|")
    lexer.whitespace_split = True
    return list(lexer)


def split_segments(tokens):
    segments = []
    segment = []
    for token in tokens:
        if token and all(char in ";&|" for char in token):
            if segment:
                segments.append(segment)
                segment = []
        else:
            segment.append(token)
    if segment:
        segments.append(segment)
    return segments


def find_shell_command(words, index):
    options_with_values = {"-O", "-o", "--init-file", "--rcfile"}
    index += 1
    while index < len(words):
        word = words[index]
        if word == "--":
            return None
        if word == "-c" or (word.startswith("-") and not word.startswith("--") and "c" in word[1:]):
            return words[index + 1] if index + 1 < len(words) else ""
        if word in options_with_values:
            index += 2
            continue
        if not word.startswith("-"):
            return None
        index += 1
    return None


def inspect(command, cwd, depth=0):
    try:
        segments = split_segments(tokenize(command))
    except ValueError as err:
        return {"status": "block", "reason": f"cannot parse shell quoting: {err}"}

    chain_dir = ""
    for words in segments:
        index = 0
        while index < len(words) and re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*=.*", words[index]):
            index += 1
        if index >= len(words):
            continue

        executable = os.path.basename(words[index])
        if executable == "cd":
            target_index = index + 1
            if target_index < len(words) and words[target_index] == "--":
                target_index += 1
            if target_index < len(words):
                chain_dir = words[target_index]
            continue

        if executable in {"bash", "sh", "zsh"}:
            wrapped = find_shell_command(words, index)
            if wrapped is None:
                continue
            if not wrapped:
                return {"status": "block", "reason": f"{executable} -c has no command to inspect"}
            if depth >= 4:
                return {"status": "block", "reason": "shell wrapper nesting exceeds the inspection limit"}
            result = inspect(wrapped, chain_dir or cwd, depth + 1)
            if result["status"] != "allow":
                return result
            continue

        if executable != "git":
            continue

        git_dir = ""
        subcommand = ""
        subcommand_index = -1
        index += 1
        options_with_values = {"-c", "--config-env", "--exec-path", "--git-dir", "--namespace", "--work-tree"}
        while index < len(words):
            word = words[index]
            if word == "-C":
                index += 1
                if index < len(words):
                    git_dir = words[index]
            elif word.startswith("-C") and word != "-C":
                git_dir = word[2:]
            elif word in options_with_values:
                index += 1
            elif word.startswith("-"):
                pass
            else:
                subcommand = word
                subcommand_index = index
                break
            index += 1

        if subcommand != "push":
            continue

        base_dir = chain_dir or cwd
        push_dir = git_dir or base_dir
        if git_dir and not os.path.isabs(git_dir):
            push_dir = os.path.join(base_dir, git_dir)
        return {
            "status": "push",
            "directory": push_dir,
            "arguments": words[subcommand_index + 1 :],
        }

    return {"status": "allow"}


print(json.dumps(inspect(command, cwd)))
PY
)

status=$(jq -r '.status // "block"' <<<"$parsed")
case $status in
allow) allow ;;
block) block "$(jq -r '.reason // "the push command could not be vetted"' <<<"$parsed")" ;;
push) ;;
*) block "the push parser returned an unknown decision" ;;
esac

directory=$(jq -r '.directory // ""' <<<"$parsed")
if ! toplevel=$(git -C "$directory" rev-parse --show-toplevel 2>/dev/null) || [[ ! -f $toplevel/AGENTS.md ]]; then
    block "cannot identify this project's worktree for the push (looked in: ${directory:-<empty>})"
fi

dirty=$(git -C "$toplevel" status --porcelain --untracked-files=all)
if [[ -n $dirty ]]; then
    block "the worktree is dirty; commit or isolate every change before validating a push"
fi

if ! current_branch=$(git -C "$toplevel" symbolic-ref --quiet --short HEAD 2>/dev/null); then
    block "HEAD is detached, so the hook cannot prove which branch the push updates"
fi

mapfile -t push_arguments < <(jq -r '.arguments[]?' <<<"$parsed")
positionals=()
skip_next=0
for argument in "${push_arguments[@]}"; do
    if [[ $skip_next -eq 1 ]]; then
        skip_next=0
        continue
    fi
    case $argument in
    --all | --delete | --mirror | --tags)
        block "$argument can push refs other than the checked-out HEAD"
        ;;
    --repo | --repo=*)
        block "--repo makes the refspec position ambiguous to this gate"
        ;;
    --exec | --receive-pack | --push-option | -o)
        skip_next=1
        ;;
    --exec=* | --receive-pack=* | --push-option=* | -*) ;;
    *) positionals+=("$argument") ;;
    esac
done

if [[ ${#positionals[@]} -gt 1 ]]; then
    for refspec in "${positionals[@]:1}"; do
        source_ref=${refspec#+}
        source_ref=${source_ref%%:*}
        case $source_ref in
        HEAD | "$current_branch" | "refs/heads/$current_branch") ;;
        *) block "refspec '$refspec' does not push the checked-out HEAD ($current_branch)" ;;
        esac
    done
fi

if [[ $explain -eq 1 ]]; then
    echo "PUSH $toplevel"
    exit 0
fi

log=$(mktemp)
trap 'rm -f "$log"' EXIT

echo "Running script/lint-check and script/type-check in $toplevel …" >&2
if "$toplevel/script/lint-check" >"$log" 2>&1 && "$toplevel/script/type-check" >>"$log" 2>&1; then
    exit 0
fi

block "script/lint-check or script/type-check failed in $toplevel:
$(tail -n 40 "$log")"
