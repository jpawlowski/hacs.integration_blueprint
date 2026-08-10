"""
Validate the agent skills under .agents/skills/.

Checks conformance with the Agent Skills open standard (https://agentskills.io/specification)
plus the conventions this repository adds on top of it:

- frontmatter parses and only uses spec-defined fields
- ``name`` matches the directory and the spec's naming rules
- ``description`` is present and within the 1024 character limit
- SKILL.md body stays within the recommended 500 lines
- reference files sit exactly one level below SKILL.md
- relative markdown links resolve
- no concrete project identifiers leak in (they must stay template-sync safe)
- evals/evals.json, when present, has the expected shape

Invoked by script/skills-check; not intended to be run directly.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
import json
from pathlib import Path
import re
import sys

SKILLS_DIR = Path(".agents/skills")
INSTRUCTIONS_DIR = Path(".agents/instructions")

# https://agentskills.io/specification#frontmatter
SPEC_FIELDS = {"name", "description", "license", "compatibility", "metadata", "allowed-tools"}
NAME_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
NAME_MAX_LENGTH = 64
DESCRIPTION_MAX_LENGTH = 1024
BODY_MAX_LINES = 500

# Identifiers that initialize.sh rewrites. Skills must use the <domain> and {ClassPrefix}
# placeholders instead, otherwise template sync would overwrite an initialized repository
# with the blueprint's own names.
FORBIDDEN_IDENTIFIERS = ("ha_integration_domain", "IntegrationBlueprint")

LINK_PATTERN = re.compile(r"\[[^\]]*\]\((?!https?:|mailto:|#)([^)]+)\)")

# Sections initialize.sh strips when a project is initialised from the template.
MARKER_START = "<!-- blueprint-only:start -->"
MARKER_END = "<!-- blueprint-only:end -->"


@dataclass
class Report:
    """Collected problems for a single skill."""

    skill: str
    errors: list[str] = field(default_factory=list)

    def error(self, message: str) -> None:
        """Record a problem."""
        self.errors.append(message)


def parse_frontmatter(text: str, report: Report) -> tuple[dict[str, object], int]:
    """
    Extract the YAML frontmatter as a mapping and the line where the body starts.

    Parsed with a real YAML parser on purpose. Descriptions contain colons, quotes and
    backticks, so a naive ``key: value`` split silently accepts frontmatter that agents
    would fail to load.
    """
    lines = text.split("\n")
    if not lines or lines[0].strip() != "---":
        report.error("SKILL.md must start with a '---' frontmatter delimiter")
        return {}, 0

    try:
        end = next(i for i, line in enumerate(lines[1:], start=1) if line.strip() == "---")
    except StopIteration:
        report.error("frontmatter is never closed with '---'")
        return {}, 0

    try:
        import yaml  # noqa: PLC0415  (optional; only needed here)
    except ImportError:
        report.error("PyYAML is unavailable — run script/setup/bootstrap so frontmatter can be validated")
        return {}, end + 1

    try:
        parsed = yaml.safe_load("\n".join(lines[1:end]))
    except yaml.YAMLError as err:
        report.error(f"frontmatter is not valid YAML: {err}")
        return {}, end + 1

    if not isinstance(parsed, dict):
        report.error("frontmatter must be a YAML mapping")
        return {}, end + 1

    return parsed, end + 1


def check_frontmatter(skill_dir: Path, fields: Mapping[str, object], report: Report) -> None:
    """Validate the frontmatter fields against the spec."""
    unknown = sorted(set(fields) - SPEC_FIELDS)
    if unknown:
        report.error(f"frontmatter has non-spec fields (reduces portability): {', '.join(unknown)}")

    name = fields.get("name") or ""
    if not isinstance(name, str):
        report.error(f"name must be a string, got {type(name).__name__}")
    elif not name:
        report.error("frontmatter is missing the required 'name' field")
    else:
        if len(name) > NAME_MAX_LENGTH:
            report.error(f"name is {len(name)} characters, the limit is {NAME_MAX_LENGTH}")
        if not NAME_PATTERN.match(name):
            report.error(f"name {name!r} must be lowercase alphanumeric with single hyphens between segments")
        if name != skill_dir.name:
            report.error(f"name {name!r} does not match the directory name {skill_dir.name!r}")

    description = fields.get("description") or ""
    if not isinstance(description, str):
        report.error(f"description must be a string, got {type(description).__name__}")
    elif not description:
        report.error("frontmatter is missing the required 'description' field")
    elif len(description) > DESCRIPTION_MAX_LENGTH:
        report.error(f"description is {len(description)} characters, the limit is {DESCRIPTION_MAX_LENGTH}")


def check_body(path: Path, body_start: int, report: Report) -> None:
    """Validate the markdown body length."""
    body_lines = len(path.read_text().split("\n")) - body_start
    if body_lines > BODY_MAX_LINES:
        report.error(f"SKILL.md body is {body_lines} lines, the recommended limit is {BODY_MAX_LINES} — split it")


def check_layout(skill_dir: Path, report: Report) -> None:
    """Validate that supporting files sit exactly one level below SKILL.md."""
    for sub in ("references", "scripts", "assets", "evals"):
        directory = skill_dir / sub
        if not directory.is_dir():
            continue
        for nested in directory.iterdir():
            if nested.is_dir():
                report.error(f"{sub}/{nested.name}/ is nested too deeply — keep reference files one level deep")


def check_identifiers(path: Path, report: Report) -> None:
    """Reject concrete project identifiers that template sync would clobber."""
    text = path.read_text()
    for identifier in FORBIDDEN_IDENTIFIERS:
        if identifier in text:
            placeholder = "<domain>" if identifier.islower() else "{ClassPrefix}"
            report.error(f"{path} contains {identifier!r} — use the {placeholder} placeholder instead")


def check_links(path: Path, report: Report) -> None:
    """Verify that every relative markdown link resolves to an existing file."""
    for target in LINK_PATTERN.findall(path.read_text()):
        resolved = (path.parent / target.split("#", 1)[0]).resolve()
        if not resolved.exists():
            report.error(f"{path} links to a missing file: {target}")


def check_evals(skill_dir: Path, report: Report) -> None:
    """
    Validate evals/evals.json against the canonical format.

    https://agentskills.io/skill-creation/evaluating-skills — assertions are plain
    strings, not objects, so Anthropic's skill-creator plugin can consume the file.
    """
    evals_file = skill_dir / "evals" / "evals.json"
    if not evals_file.is_file():
        return

    try:
        data = json.loads(evals_file.read_text())
    except json.JSONDecodeError as err:
        report.error(f"evals/evals.json is not valid JSON: {err}")
        return

    if data.get("skill_name") != skill_dir.name:
        report.error(f"evals/evals.json skill_name is {data.get('skill_name')!r}, expected {skill_dir.name!r}")

    evals = data.get("evals")
    if not isinstance(evals, list) or not evals:
        report.error("evals/evals.json must contain a non-empty 'evals' list")
        return

    seen_ids: set[object] = set()
    for index, item in enumerate(evals):
        where = f"evals[{index}]"
        for required in ("id", "prompt", "expected_output", "assertions"):
            if required not in item:
                report.error(f"{where} is missing '{required}'")
        if item.get("id") in seen_ids:
            report.error(f"{where} reuses id {item.get('id')!r}")
        seen_ids.add(item.get("id"))
        for extra in set(item) - {"id", "prompt", "expected_output", "assertions", "files"}:
            report.error(f"{where} has non-canonical field {extra!r} — skill-creator ignores it")
        assertions = item.get("assertions")
        if not isinstance(assertions, list) or not assertions:
            report.error(f"{where} must have a non-empty 'assertions' list")
            continue
        for assertion in assertions:
            if not isinstance(assertion, str) or not assertion.strip():
                report.error(f"{where} assertions must be non-empty strings, got {type(assertion).__name__}")


def check_skill(skill_dir: Path) -> Report:
    """Run every check against one skill directory."""
    report = Report(skill=skill_dir.name)
    skill_file = skill_dir / "SKILL.md"
    if not skill_file.is_file():
        report.error("directory has no SKILL.md")
        return report

    fields, body_start = parse_frontmatter(skill_file.read_text(), report)
    if fields:
        check_frontmatter(skill_dir, fields, report)
        check_body(skill_file, body_start, report)
    check_layout(skill_dir, report)
    check_evals(skill_dir, report)
    for markdown in sorted(skill_dir.rglob("*.md")):
        check_identifiers(markdown, report)
        check_links(markdown, report)
    return report


def check_blueprint_only_markers() -> list[Report]:
    """
    Verify that every blueprint-only marker is balanced and ordered.

    initialize.sh strips these blocks with a sed range. An unmatched start marker makes
    that range run to end of file and silently truncates the document in every repository
    initialised from the template.
    """
    reports: list[Report] = []
    for path in sorted(Path(".agents").rglob("*.md")):
        text = path.read_text()
        starts = text.count(MARKER_START)
        ends = text.count(MARKER_END)
        if not starts and not ends:
            continue
        report = Report(skill=str(path))
        if starts != ends:
            report.error(f"blueprint-only markers are unbalanced ({starts} start, {ends} end) — sed would over-delete")
        elif text.index(MARKER_START) > text.index(MARKER_END):
            report.error("blueprint-only end marker precedes its start marker")
        reports.append(report)
    return reports


def check_instruction_globs() -> list[Report]:
    """
    Verify that every instructions file declares the same globs twice.

    Copilot and VS Code read ``applyTo``; Claude Code reads ``globs`` through the
    .claude/rules/instructions symlink. Both take the same comma-separated string, so they
    must be byte-identical.

    ``globs`` rather than the officially documented ``paths``: community testing
    (anthropics/claude-code#17204) reports that ``paths`` as a quoted YAML list never
    matches, and that it fails silently — a rule that quietly stops scoping is worse than
    one that errors.
    """
    reports: list[Report] = []
    for path in sorted(INSTRUCTIONS_DIR.glob("*.instructions.md")):
        report = Report(skill=str(path))
        fields, _ = parse_frontmatter(path.read_text(), report)
        if not report.errors:
            apply_to = fields.get("applyTo")
            globs = fields.get("globs")
            if not isinstance(apply_to, str) or not apply_to.strip():
                report.error("frontmatter is missing 'applyTo' (Copilot and VS Code need it)")
            elif not isinstance(globs, str) or not globs.strip():
                report.error("frontmatter is missing 'globs' — Claude Code would load this file into every session")
            elif apply_to.strip() != globs.strip():
                report.error("'applyTo' and 'globs' differ — they must be the identical comma-separated string")
        reports.append(report)
    return reports


def main() -> int:
    """Validate every skill and print a summary."""
    if not SKILLS_DIR.is_dir():
        print(f"No {SKILLS_DIR}/ directory — nothing to validate.")
        return 0

    skill_dirs = sorted(d for d in SKILLS_DIR.iterdir() if d.is_dir() and not d.name.startswith("."))
    if not skill_dirs:
        print(f"No skills found in {SKILLS_DIR}/.")
        return 0

    reports = [check_skill(d) for d in skill_dirs]
    instruction_reports = check_instruction_globs()
    marker_reports = check_blueprint_only_markers()

    for report in reports:
        if report.errors:
            print(f"  ✗ {report.skill}")
            for error in report.errors:
                print(f"      {error}")
        else:
            print(f"  ✓ {report.skill}")

    broken_instructions = [r for r in instruction_reports if r.errors]
    if instruction_reports:
        print()
        for report in broken_instructions:
            print(f"  ✗ {report.skill}")
            for error in report.errors:
                print(f"      {error}")
        if not broken_instructions:
            print(f"  ✓ {len(instruction_reports)} instruction files: applyTo and globs agree")

    broken_markers = [r for r in marker_reports if r.errors]
    for report in broken_markers:
        print(f"  ✗ {report.skill}")
        for error in report.errors:
            print(f"      {error}")

    failed = [r for r in reports if r.errors] + broken_instructions + broken_markers
    print()
    if failed:
        print(f"{len(failed)} file(s) have problems.")
        return 1
    print(f"{len(reports)} skills and {len(instruction_reports)} instruction files validated.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
