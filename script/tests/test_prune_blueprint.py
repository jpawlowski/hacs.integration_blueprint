"""Tests for script/prune-blueprint."""

from pathlib import Path
import shutil
import subprocess

import pytest

SCRIPT_DIR = Path(__file__).parents[1]
SECTION_FILE = ".agents/skills/README.md"
README = "keep\n<!-- blueprint-only:start -->\ndrop\n<!-- blueprint-only:end -->\nkeep too\n"
PRUNED = (".github/FUNDING.yml", "docs/blueprint/MIGRATION.md", ".agents/skills/blueprint-skill-maintenance/SKILL.md")


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    """An initialised-looking repository holding the blueprint leftovers and one file that must survive."""
    (tmp_path / "script" / ".lib").mkdir(parents=True)
    shutil.copy(SCRIPT_DIR / "prune-blueprint", tmp_path / "script" / "prune-blueprint")
    shutil.copy(SCRIPT_DIR / ".lib" / "output.sh", tmp_path / "script" / ".lib" / "output.sh")
    for name in (*PRUNED, "docs/user/GUIDE.md"):
        (tmp_path / name).parent.mkdir(parents=True, exist_ok=True)
        (tmp_path / name).write_text("x\n", encoding="utf-8")
    (tmp_path / SECTION_FILE).write_text(README, encoding="utf-8")
    return tmp_path


def _run(repo: Path, *args: str) -> subprocess.CompletedProcess[str]:
    """Run the copied script inside the temporary repository."""
    return subprocess.run(
        [str(repo / "script" / "prune-blueprint"), *args],
        cwd=repo,
        capture_output=True,
        text=True,
        check=False,
    )


@pytest.mark.unit
def test_dry_run_lists_without_deleting(repo: Path) -> None:
    """Without --apply the script reports and changes nothing."""
    result = _run(repo)

    assert result.returncode == 0
    assert "FUNDING.yml" in result.stdout
    assert all((repo / name).exists() for name in PRUNED)
    assert (repo / SECTION_FILE).read_text(encoding="utf-8") == README


@pytest.mark.unit
def test_apply_removes_leftovers_and_keeps_the_rest(repo: Path) -> None:
    """--apply removes the listed paths and sections and leaves other files alone."""
    result = _run(repo, "--apply")

    assert result.returncode == 0
    assert not any((repo / name).exists() for name in PRUNED)
    assert (repo / SECTION_FILE).read_text(encoding="utf-8") == "keep\nkeep too\n"
    assert (repo / "docs" / "user" / "GUIDE.md").exists()


@pytest.mark.unit
def test_apply_is_idempotent(repo: Path) -> None:
    """A second run finds nothing left to do."""
    _run(repo, "--apply")
    result = _run(repo, "--apply")

    assert result.returncode == 0
    assert "Nothing to prune" in result.stdout


@pytest.mark.unit
def test_refuses_while_initialize_script_exists(repo: Path) -> None:
    """The blueprint and uninitialised copies are never pruned."""
    (repo / "initialize.sh").write_text("#!/bin/bash\n", encoding="utf-8")

    result = _run(repo, "--apply")

    assert result.returncode == 1
    assert all((repo / name).exists() for name in PRUNED)
