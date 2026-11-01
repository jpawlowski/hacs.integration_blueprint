"""
Keep the protected-path lists of every agent configuration in step.

The Claude Code managed settings are the canonical list. The OpenCode managed configuration must deny exactly the
same reads and edits, and both copies of the VS Code ``chat.tools.edits.autoApprove`` setting must be identical and
require approval for every protected edit. VS Code may list broader patterns of its own, such as ``**/.env``.

Invoked by script/skills-check; not intended to be run directly.
"""

from dataclasses import dataclass
import glob
import json
from pathlib import Path
import re
import sys
from typing import Any

CLAUDE_SETTINGS = Path(".devcontainer/claude-code/managed-settings.json")
OPENCODE_CONFIG = Path(".devcontainer/opencode/opencode.json")
DEVCONTAINER_JSON = Path(".devcontainer/devcontainer.json")
VSCODE_DEFAULT_SETTINGS = Path(".vscode/settings.default.jsonc")
AUTO_APPROVE_KEY = "chat.tools.edits.autoApprove"
CLAUDE_RULE = re.compile(r"(Read|Edit)\((.+)\)")
TRAILING_COMMA = re.compile(r'"(?:\\.|[^"\\])*"|,(\s*[}\]])')

SHAPES = {
    "any depth": {"claude": ("**/", ""), "opencode": ("*", ""), "vscode": ("**/", "")},
    "directory": {"claude": ("./", "/**"), "opencode": ("", "/*"), "vscode": ("", "/**")},
    "exact": {"claude": ("./", ""), "opencode": ("", ""), "vscode": ("", "")},
}


@dataclass(frozen=True, order=True, slots=True)
class Rule:
    """One protected path, independent of the syntax a tool writes it in."""

    action: str
    shape: str
    path: str


def strip_jsonc(text: str) -> str:
    """Remove comments and trailing commas so ``json`` can parse a JSONC document."""
    result = []
    index = 0
    in_string = False
    while index < len(text):
        char = text[index]
        if in_string:
            result.append(char)
            if char == "\\":
                result.append(text[index + 1 : index + 2])
                index += 1
            elif char == '"':
                in_string = False
        elif char == '"':
            in_string = True
            result.append(char)
        elif text.startswith("//", index):
            end = text.find("\n", index)
            index = len(text) if end < 0 else end
            continue
        elif text.startswith("/*", index):
            end = text.find("*/", index)
            if end < 0:
                raise ValueError("unclosed block comment")
            index = end + 2
            continue
        else:
            result.append(char)
        index += 1
    return TRAILING_COMMA.sub(lambda match: match.group(1) or match.group(0), "".join(result))


def load(path: Path) -> dict[str, Any]:
    """Parse a JSON or JSONC file."""
    try:
        return json.loads(strip_jsonc(path.read_text(encoding="utf-8")))
    except ValueError as err:
        raise ValueError(f"{path}: cannot parse ({err})") from err


def parse(pattern: str, tool: str) -> tuple[str, str] | None:
    """Return the shape and path of a pattern, trying the most specific shape first."""
    for shape in ("directory", "any depth", "exact"):
        prefix, suffix = SHAPES[shape][tool]
        if pattern.startswith(prefix) and pattern.endswith(suffix) and len(pattern) > len(prefix) + len(suffix):
            return shape, pattern[len(prefix) : len(pattern) - len(suffix)]
    return None


def render(rule: Rule, tool: str) -> str:
    """Write a rule's path in the pattern syntax of one tool."""
    prefix, suffix = SHAPES[rule.shape][tool]
    return f"{prefix}{rule.path}{suffix}"


def opencode_entry(rule: Rule) -> str:
    """Write a rule as an OpenCode ``permissions`` entry."""
    return json.dumps({"action": rule.action, "resource": render(rule, "opencode"), "effect": "deny"})


def claude_rules(settings: dict[str, Any], errors: list[str]) -> set[Rule]:
    """Return the rules of the Claude Code ``permissions.deny`` list."""
    rules = set()
    for entry in settings.get("permissions", {}).get("deny", []):
        match = CLAUDE_RULE.fullmatch(entry)
        parsed = parse(match.group(2), "claude") if match else None
        if match and parsed:
            rules.add(Rule(match.group(1).lower(), *parsed))
        else:
            errors.append(f"{CLAUDE_SETTINGS}: {entry!r} must be Read(**/…), Edit(**/…) or Edit(./…)")
    return rules


def opencode_rules(config: dict[str, Any], errors: list[str]) -> set[Rule]:
    """Return the deny rules of the OpenCode ``permissions`` list."""
    rules = set()
    for entry in config.get("permissions", []):
        if entry.get("effect") != "deny":
            errors.append(f"{OPENCODE_CONFIG}: {json.dumps(entry)} can lift a protection; the last matching rule wins")
            continue
        action = entry.get("action", "")
        parsed = parse(entry.get("resource", ""), "opencode")
        if action in {"read", "edit"} and parsed:
            rules.add(Rule(action, *parsed))
        else:
            errors.append(f"{OPENCODE_CONFIG}: unsupported deny rule {json.dumps(entry)}")
    return rules


def covered(rule: Rule, expressions: list[re.Pattern[str]]) -> bool:
    """Return whether every path the rule protects also matches one of the VS Code globs."""
    path = rule.path.replace("*", "x")
    samples = {"any depth": [path, f"x/{path}"], "directory": [f"{path}/x"], "exact": [path]}[rule.shape]
    return all(any(expression.fullmatch(sample) for expression in expressions) for sample in samples)


def compare(expected: set[Rule], actual: set[Rule]) -> list[str]:
    """Report every rule that the OpenCode list lacks or has on its own."""
    return [
        f"{OPENCODE_CONFIG}: missing {opencode_entry(rule)} (from {CLAUDE_SETTINGS})"
        for rule in sorted(expected - actual)
    ] + [
        f"{OPENCODE_CONFIG}: {opencode_entry(rule)} has no counterpart in {CLAUDE_SETTINGS}"
        for rule in sorted(actual - expected)
    ]


def vscode_lists() -> dict[Path, dict[str, Any]]:
    """Return every VS Code ``chat.tools.edits.autoApprove`` mapping in the repository."""
    lists = {}
    if DEVCONTAINER_JSON.is_file():
        settings = load(DEVCONTAINER_JSON).get("customizations", {}).get("vscode", {}).get("settings", {})
        lists[DEVCONTAINER_JSON] = settings.get(AUTO_APPROVE_KEY, {})
    if VSCODE_DEFAULT_SETTINGS.is_file():
        lists[VSCODE_DEFAULT_SETTINGS] = load(VSCODE_DEFAULT_SETTINGS).get(AUTO_APPROVE_KEY, {})
    return lists


def check() -> list[str]:
    """Return every disagreement between the protected-path lists that exist in this repository."""
    if not CLAUDE_SETTINGS.is_file():
        return []
    errors: list[str] = []
    canonical = claude_rules(load(CLAUDE_SETTINGS), errors)

    if OPENCODE_CONFIG.is_file():
        errors += compare(canonical, opencode_rules(load(OPENCODE_CONFIG), errors))

    lists = vscode_lists()
    if len(lists) == 2:
        first, second = lists.values()
        errors += [
            f"{VSCODE_DEFAULT_SETTINGS}: {AUTO_APPROVE_KEY} differs from {DEVCONTAINER_JSON} at {key!r}"
            for key in sorted(first.keys() | second.keys())
            if first.get(key) != second.get(key)
        ]
    for path, auto_approve in lists.items():
        expressions = [
            re.compile(glob.translate(pattern, recursive=True, include_hidden=True))
            for pattern, approve in auto_approve.items()
            if approve is False
        ]
        errors += [
            f"{path}: {AUTO_APPROVE_KEY} needs {render(rule, 'vscode')!r}: false (from {CLAUDE_SETTINGS})"
            for rule in sorted(canonical)
            if rule.action == "edit" and not covered(rule, expressions)
        ]
    return errors


def main() -> int:
    """Print every disagreement and fail when there is one."""
    try:
        errors = check()
    except ValueError as err:
        errors = [str(err)]
    for error in errors:
        print(f"  ✗ {error}")
    if errors:
        print(f"\n{len(errors)} protected-path disagreement(s) between the agent configurations.")
        return 1
    print("  ✓ agent configurations protect the same paths")
    return 0


if __name__ == "__main__":
    sys.exit(main())
