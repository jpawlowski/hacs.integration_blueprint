"""Guard the files that initialize.sh must not rewrite.

initialize.sh replaces the blueprint's names in every file. A file that template sync keeps shipping and that names
the blueprint on purpose would be rewritten, then reverted by the next sync pull request.
"""

from pathlib import Path
import re
import subprocess

import pytest

REPO_ROOT = Path(__file__).parents[2]
INITIALIZE = REPO_ROOT / "initialize.sh"
BLUEPRINT_NAMES = re.compile(
    r"ha_integration_domain|IntegrationBlueprint|Integration [Bb]lueprint|hacs\.integration_blueprint"
    r"|jpawlowski|Julian Pawlowski"
)


def _array(name: str) -> list[str]:
    """Return the quoted entries of a bash array declared as `local <name>=( ... )`."""
    body = re.search(rf"local {name}=\((.*?)\n\s*\)", INITIALIZE.read_text(encoding="utf-8"), re.DOTALL)
    assert body, f"{name} not found in initialize.sh"
    return re.findall(r'^\s*"([^"]+)"', body.group(1), re.MULTILINE)


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
    candidates = [
        path
        for path in _tracked_files()
        if (REPO_ROOT / path).is_file() and BLUEPRINT_NAMES.search((REPO_ROOT / path).read_text("utf-8", "ignore"))
    ]
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
def test_excluded_paths_exist() -> None:
    """A stale exclusion silently stops protecting anything."""
    missing = [path for path in _array("exclude_paths") if not (REPO_ROOT / path).is_file()]

    assert not missing, f"exclude_paths in initialize.sh points at files that do not exist: {missing}"
