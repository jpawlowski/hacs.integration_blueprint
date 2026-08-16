"""Regression tests for synchronized agent lifecycle hooks."""

import json
from pathlib import Path
import subprocess

import pytest

HOOK = Path(__file__).parents[2] / ".agents" / "hooks" / "pre-push-check.sh"


def _initialize_repository(path: Path) -> None:
    """Create a clean main branch with the project marker required by the hook."""
    path.mkdir(parents=True)
    subprocess.run(["git", "init", "--quiet", "--initial-branch=main"], cwd=path, check=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=path, check=True)
    subprocess.run(["git", "config", "user.name", "Hook Test"], cwd=path, check=True)
    (path / "AGENTS.md").write_text("# Test project\n", encoding="utf-8")
    subprocess.run(["git", "add", "AGENTS.md"], cwd=path, check=True)
    subprocess.run(["git", "commit", "--quiet", "-m", "test: initialize"], cwd=path, check=True)


def _explain(command: str, cwd: Path) -> str:
    """Return the hook's explain-mode decision for one shell tool payload."""
    payload = json.dumps({"cwd": str(cwd), "tool_input": {"command": command}})
    result = subprocess.run(
        ["bash", str(HOOK), "--explain"],
        cwd=cwd,
        input=payload,
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout.strip()


@pytest.mark.unit
@pytest.mark.parametrize(
    "command",
    [
        'printf "git status\\n"',
        'grep "git push" README.md',
        'git commit -m "docs: explain how git push triggers deploy"',
        'printf "%s\\n" "git push"',
        "echo done # git push is documented here",
        "bash -c 'grep \"git push\" README.md'",
    ],
)
def test_allows_non_push_command(tmp_path: Path, command: str) -> None:
    """Quoted text, comments, and non-push git commands do not trigger the gate."""
    assert _explain(command, tmp_path) == "ALLOW"


@pytest.mark.unit
def test_detects_git_c_push_with_quoted_space(tmp_path: Path) -> None:
    """A quoted git -C path containing spaces still resolves to the worktree."""
    repository = tmp_path / "work tree"
    _initialize_repository(repository)

    assert _explain(f'git -C "{repository}" push origin main', tmp_path) == f"PUSH {repository}"


@pytest.mark.unit
def test_blocks_dirty_worktree(tmp_path: Path) -> None:
    """Uncommitted files cannot make checks pass for a different pushed commit."""
    repository = tmp_path / "repository"
    _initialize_repository(repository)
    (repository / "dirty.txt").write_text("not committed\n", encoding="utf-8")

    assert _explain("git push origin main", repository).startswith("BLOCK the worktree is dirty")


@pytest.mark.unit
def test_blocks_refspec_from_other_branch(tmp_path: Path) -> None:
    """The gate refuses to validate a source ref other than the checked-out HEAD."""
    repository = tmp_path / "repository"
    _initialize_repository(repository)

    assert _explain("git push origin other", repository) == (
        "BLOCK refspec 'other' does not push the checked-out HEAD (main)"
    )


@pytest.mark.unit
def test_blocks_repo_option_with_unverifiable_refspec(tmp_path: Path) -> None:
    """The alternative --repo syntax cannot hide a source ref from validation."""
    repository = tmp_path / "repository"
    _initialize_repository(repository)

    assert _explain("git push --repo origin other", repository) == (
        "BLOCK --repo makes the refspec position ambiguous to this gate"
    )


@pytest.mark.unit
@pytest.mark.parametrize("shell", ["bash -c", "bash -lc", "sh -c", "zsh -c"])
def test_detects_wrapped_push(tmp_path: Path, shell: str) -> None:
    """A push inside a known shell command wrapper is inspected normally."""
    repository = tmp_path / "repository"
    _initialize_repository(repository)

    assert _explain(f"{shell} 'git push origin main'", repository) == f"PUSH {repository}"
