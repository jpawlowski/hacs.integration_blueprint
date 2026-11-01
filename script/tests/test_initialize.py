"""Guard the files that initialize.sh must not rewrite, and the files that must not name the domain at all.

initialize.sh replaces the blueprint's names in every file. A file that template sync keeps shipping and that names
the blueprint on purpose would be rewritten, then reverted by the next sync pull request. A synced file that names the
domain only survives by leaving the sync, and then never receives an upstream change again.
"""

from pathlib import Path
import re
import subprocess

import pytest

REPO_ROOT = Path(__file__).parents[2]
INITIALIZE = REPO_ROOT / "initialize.sh"
PRUNE_BLUEPRINT = REPO_ROOT / "script" / "prune-blueprint"
SUBSTITUTED_IDENTIFIERS = re.compile(r"ha_integration_domain|IntegrationBlueprint")
BLUEPRINT_NAMES = re.compile(
    SUBSTITUTED_IDENTIFIERS.pattern
    + r"|Integration [Bb]lueprint|hacs\.integration_blueprint|jpawlowski|Julian Pawlowski"
)

# Owned by the integration after initialization, so they may carry its domain; each must stay out of template sync.
DOMAIN_OWNED = (
    "AGENTS.md",
    "DEPENDENCIES.md",
    "README.md",
    "README.template.md",
    "config/",
    "custom_components/",
    "docs/",
    "pyproject.toml",
    "requirements.txt",
    "tests/",
)

# Synced files that name the placeholder itself, to detect or explain it. Kept apart from exclude_paths on purpose:
# exempting a file from rewriting must not also exempt it from this guard.
PLACEHOLDER_REFERENCES = (
    ".agents/README.md",
    ".devcontainer/post-attach.sh",
    ".templatesyncignore",
    "script/.lib/skills_check.py",
)

# Initialised repositories have no initialize.sh; skip rather than fail if template sync reinstates this file.
pytestmark = pytest.mark.skipif(not INITIALIZE.exists(), reason="initialize.sh only exists before initialization")


def _array(name: str, script: Path = INITIALIZE) -> list[str]:
    """Return the quoted entries of a bash array declared as `[local ]<name>=( ... )`."""
    body = re.search(
        rf"^\s*(?:local )?{name}=\((.*?)\n\s*\)", script.read_text(encoding="utf-8"), re.DOTALL | re.MULTILINE
    )
    assert body, f"{name} not found in {script.name}"
    return re.findall(r'^\s*"([^"]+)"', body.group(1), re.MULTILINE)


def _under(path: str, prefixes: tuple[str, ...] | list[str]) -> bool:
    """Whether path is one of prefixes or lies beneath one of them."""
    return any(path == prefix.rstrip("/") or path.startswith(prefix.rstrip("/") + "/") for prefix in prefixes)


def _files_naming(pattern: re.Pattern[str]) -> list[str]:
    """Tracked files whose content matches pattern."""
    return [
        path
        for path in _tracked_files()
        if (REPO_ROOT / path).is_file() and pattern.search((REPO_ROOT / path).read_text("utf-8", "ignore"))
    ]


def _tracked_files() -> list[str]:
    """Tracked regular files, leaving out symlinks and anything beneath a symlinked directory."""
    listing = subprocess.run(
        ["git", "ls-files", "-s", "-z"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=True,
    ).stdout
    entries = [entry.split("\t", 1) for entry in listing.split("\0") if entry]
    symlinks = {path for meta, path in entries if meta.startswith("120000")}
    return [
        path
        for meta, path in entries
        if not meta.startswith("120000") and not any(path.startswith(link + "/") for link in symlinks)
    ]


def _template_sync_ignored(tmp_path: Path, paths: list[str]) -> set[str]:
    """Return the paths .templatesyncignore keeps out of the sync, matching only from the repository root."""
    patterns = []
    for raw in (REPO_ROOT / ".templatesyncignore").read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith(("#", "!")):
            continue
        patterns.append(line if "/" in line.rstrip("/") else "/" + line)
    subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True)
    (tmp_path / ".gitignore").write_text("\n".join(patterns) + "\n", encoding="utf-8")
    result = subprocess.run(
        ["git", "check-ignore", "--no-index", "--stdin", "-z"],
        cwd=tmp_path,
        input="\0".join(paths),
        capture_output=True,
        text=True,
        check=False,
    )
    return {path for path in result.stdout.split("\0") if path}


@pytest.mark.unit
def test_synced_files_naming_the_blueprint_are_excluded_from_rewriting(tmp_path: Path) -> None:
    """Every synced file that contains a blueprint name needs an exclusion in initialize.sh."""
    excluded_names = set(_array("exclude_files"))
    excluded_paths = {path.removeprefix("./") for path in _array("exclude_paths")}
    candidates = _files_naming(BLUEPRINT_NAMES)
    ignored = _template_sync_ignored(tmp_path, candidates)

    unprotected = sorted(
        path
        for path in candidates
        if path not in ignored and path not in excluded_paths and Path(path).name not in excluded_names
    )

    assert not unprotected, (
        "Template sync ships these files, they name the blueprint, and initialize.sh would rewrite them. "
        f"Add them to exclude_paths in initialize.sh or to .templatesyncignore: {unprotected}"
    )


@pytest.mark.unit
def test_only_domain_owned_files_name_the_domain() -> None:
    """A file template sync ships must find the domain at runtime instead of naming it."""
    blueprint_only = [INITIALIZE.name, *_array("PRUNE_PATHS", PRUNE_BLUEPRINT)]
    offenders = sorted(
        path
        for path in _files_naming(SUBSTITUTED_IDENTIFIERS)
        if not _under(path, DOMAIN_OWNED) and path not in PLACEHOLDER_REFERENCES and not _under(path, blueprint_only)
    )

    assert not offenders, (
        "Make these domain-agnostic (glob custom_components/*, or source script/.lib/integration.sh); only a file the "
        f"integration owns outright belongs in DOMAIN_OWNED: {offenders}"
    )


@pytest.mark.unit
def test_excluded_paths_exist() -> None:
    """A stale exclusion silently stops protecting anything."""
    missing = [path for path in _array("exclude_paths") if not (REPO_ROOT / path).is_file()]

    assert not missing, f"exclude_paths in initialize.sh points at files that do not exist: {missing}"
