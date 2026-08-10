"""
Run the agent-skill evals under .agents/skills/*/evals/evals.json.

Each eval is a prompt a developer might realistically type, plus assertions describing
what a good answer looks like. The runner does two passes per eval:

1. **Answer pass** — send the prompt to the agent CLI from the repository root, so the
   agent discovers and applies the repository's skills exactly as it would in real use.
   The agent runs read-only; it may inspect the repository but not modify it.
2. **Judge pass** — send the answer plus the assertions to the same CLI and ask for a
   strict JSON verdict per assertion.

This measures whether a skill actually changes agent behaviour, which linting a SKILL.md
cannot tell you. It costs real model calls, so it is never part of script/check.

Works with whichever agent CLI script/skill-evals resolved: Claude Code (`claude`),
Codex CLI (`codex`), or GitHub Copilot CLI (`copilot`). Each has a different flag
surface for models, tool permissions, and output capture — see the `_*_argv()`
builders below, one per agent.

Invoked by script/skill-evals; not intended to be run directly.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import textwrap

SKILLS_DIR = Path(".agents/skills")
REPORT_DIR = Path(".agents/scratch")

ANSWER_PREAMBLE = """\
You are working in this Home Assistant custom integration repository. Answer the request
below the way you normally would: consult the repository's own agent skills, instructions
and code as needed, including read-only commands (e.g. git status, git diff, git log) to
inspect the current repository state.

Do not create, edit, or delete any files, and do not run any command that changes
repository or git state (commit, push, add, reset, checkout, etc.). Describe what you
would do and show the code you would write.

REQUEST:
"""

JUDGE_PREAMBLE = """\
You are grading another agent's answer against a checklist. Be strict and literal: mark an
assertion as passing only if the answer clearly satisfies it. Absence of evidence is a
failure, not a pass.

Grade every assertion, in the order given, and return one entry per assertion. Evidence must
quote or reference the answer, not state an opinion.

Reply with JSON only, no prose and no code fences, in exactly this shape:
{"assertion_results": [{"text": "<the assertion>", "passed": true, "evidence": "<one short sentence>"}]}
"""


@dataclass
class EvalResult:
    """Outcome of a single eval, mirroring the canonical grading.json shape."""

    skill: str
    eval_id: object
    prompt: str
    results: list[dict]
    answer: str

    @property
    def ok(self) -> bool:
        """Return True when every assertion passed."""
        return all(r["passed"] for r in self.results)

    @property
    def failures(self) -> list[dict]:
        """Return only the failed assertion results."""
        return [r for r in self.results if not r["passed"]]


def _claude_argv(agent_bin: str, model: str, *, repo_access: bool) -> list[str]:
    """Build argv for Claude Code's non-interactive print mode (`claude -p`)."""
    argv = [agent_bin, "-p", "--output-format", "text"]
    if model:
        argv += ["--model", model]
    if repo_access:
        # Explicit allow-list: unlisted tools are auto-denied (no prompt possible in -p
        # mode), so the read tools the agent needs must be named here. Git is split into
        # read-only subcommands (allowed, needed to inspect status/diff before answering)
        # and mutating ones (explicitly disallowed) rather than blocking `git` outright.
        argv += [
            "--allowedTools",
            (
                "Read,Glob,Grep,Bash(rg:*),Bash(cat:*),Bash(ls:*),"
                "Bash(git status:*),Bash(git diff:*),Bash(git log:*),Bash(git show:*)"
            ),
            "--disallowedTools",
            (
                "Write,Edit,NotebookEdit,Bash(rm:*),"
                "Bash(git commit:*),Bash(git push:*),Bash(git add:*),"
                "Bash(git reset:*),Bash(git checkout:*),Bash(git clean:*),Bash(git branch:*)"
            ),
        ]
    else:
        # Judge pass needs no tools at all — reasoning over the prompt text only.
        argv += [
            "--disallowedTools",
            "Read,Write,Edit,NotebookEdit,Bash,Grep,Glob,WebFetch,WebSearch,Task,TodoWrite",
        ]
    return argv


def _codex_argv(agent_bin: str, model: str, answer_file: Path) -> list[str]:
    """
    Build argv for Codex CLI's non-interactive mode (`codex exec`).

    `--sandbox read-only` blocks writes and covers both passes (repo exploration reads
    are still allowed). The final answer is captured via --output-last-message rather
    than stdout, which also carries reasoning/tool-call trace lines.
    """
    argv = [
        agent_bin,
        "exec",
        "--sandbox",
        "read-only",
        "--output-last-message",
        str(answer_file),
    ]
    if model:
        argv += ["--model", model]
    return argv


def _copilot_argv(agent_bin: str, model: str, *, repo_access: bool) -> list[str]:
    """Build argv for GitHub Copilot CLI's programmatic mode."""
    argv = [agent_bin, "--model", model, "--no-color", "--log-level", "none"]
    if repo_access:
        argv += ["--allow-tool=shell(rg)", "--allow-tool=shell(cat)", "--allow-tool=shell(ls)"]
    argv += ["--deny-tool=write", "--deny-tool=shell(git)", "--deny-tool=shell(rm)"]
    return argv


def run_agent(agent: str, agent_bin: str, model: str, prompt: str, timeout: int, *, repo_access: bool) -> str:
    """
    Send a prompt to the configured agent CLI and return its answer text.

    The prompt goes in on stdin rather than through a positional/-p argument: judge
    prompts embed a full answer and would otherwise risk the argv length limit. Writes
    are denied in every pass — an eval must never mutate the repository it is measuring.
    """
    answer_file: Path | None = None
    try:
        if agent == "claude":
            argv = _claude_argv(agent_bin, model, repo_access=repo_access)
        elif agent == "codex":
            fd, path = tempfile.mkstemp(prefix="skill-eval-", suffix=".txt")
            os.close(fd)
            answer_file = Path(path)
            argv = _codex_argv(agent_bin, model, answer_file)
        elif agent == "copilot":
            argv = _copilot_argv(agent_bin, model, repo_access=repo_access)
        else:
            raise RuntimeError(f"Unknown agent CLI: {agent!r} (expected claude, codex, or copilot)")

        completed = subprocess.run(
            argv,
            input=prompt,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
        if completed.returncode != 0:
            message = completed.stderr.strip() or completed.stdout.strip() or "agent CLI exited non-zero"
            raise RuntimeError(message)

        if answer_file is not None:
            return answer_file.read_text().strip()
        return completed.stdout.strip()
    finally:
        if answer_file is not None:
            answer_file.unlink(missing_ok=True)


def judge(agent: str, agent_bin: str, model: str, item: dict, answer: str, *, timeout: int) -> list[dict]:
    """
    Grade an answer against the eval's assertions.

    Assertions are plain strings in the canonical format, so verdicts come back positionally
    rather than keyed by id. Returns entries in the canonical grading.json shape.
    """
    assertions: list[str] = item["assertions"]
    checklist = "\n".join(f"{i}. {text}" for i, text in enumerate(assertions, start=1))
    prompt = (
        f"{JUDGE_PREAMBLE}\n"
        f"ORIGINAL REQUEST:\n{item['prompt']}\n\n"
        f"WHAT A GOOD ANSWER LOOKS LIKE:\n{item['expected_output']}\n\n"
        f"ASSERTIONS (grade every one, in this order):\n{checklist}\n\n"
        f"ANSWER TO GRADE:\n{answer}\n"
    )
    raw = run_agent(agent, agent_bin, model, prompt, timeout=timeout, repo_access=False)
    start, end = raw.find("{"), raw.rfind("}")
    if start == -1 or end == -1:
        raise RuntimeError(f"judge did not return JSON: {raw[:200]}")
    verdicts = json.loads(raw[start : end + 1]).get("assertion_results", [])

    results: list[dict] = []
    for index, text in enumerate(assertions):
        verdict = verdicts[index] if index < len(verdicts) else {}
        results.append(
            {
                "text": text,
                "passed": bool(verdict.get("passed")),
                "evidence": str(verdict.get("evidence") or "judge returned no verdict"),
            }
        )
    return results


def run_eval(agent: str, agent_bin: str, model: str, skill: str, item: dict, *, timeout: int) -> EvalResult:
    """Run one eval end to end."""
    answer = run_agent(agent, agent_bin, model, ANSWER_PREAMBLE + item["prompt"], timeout, repo_access=True)
    results = judge(agent, agent_bin, model, item, answer, timeout=timeout)
    return EvalResult(skill=skill, eval_id=item["id"], prompt=item["prompt"], results=results, answer=answer)


def load_evals(only: str | None) -> list[tuple[str, dict]]:
    """Collect (skill, eval) pairs, optionally filtered to one skill."""
    items: list[tuple[str, dict]] = []
    for evals_file in sorted(SKILLS_DIR.glob("*/evals/evals.json")):
        skill = evals_file.parent.parent.name
        if only and skill != only:
            continue
        items.extend((skill, item) for item in json.loads(evals_file.read_text())["evals"])
    return items


def write_report(results: list[EvalResult]) -> Path:
    """Write a markdown report with every answer, for manual inspection."""
    REPORT_DIR.mkdir(exist_ok=True)
    report = REPORT_DIR / "skill-evals-report.md"
    lines = ["# Agent skill eval report", ""]
    for result in results:
        mark = "PASS" if result.ok else "FAIL"
        lines += [f"## {mark} — `{result.skill}` eval {result.eval_id}", "", f"> {result.prompt}", ""]
        for entry in result.results:
            if entry["passed"]:
                lines.append(f"- pass — {entry['text']}")
            else:
                lines.append(f"- **fail** — {entry['text']} _({entry['evidence']})_")
        lines += ["", "<details><summary>Answer</summary>", "", "```text", result.answer, "```", "", "</details>", ""]
    report.write_text("\n".join(lines))
    return report


def main() -> int:
    """Run the selected evals and print a summary."""
    parser = argparse.ArgumentParser(description="Run agent skill evals.")
    parser.add_argument("--agent", required=True, choices=["claude", "codex", "copilot"], help="Agent CLI to use")
    parser.add_argument("--agent-bin", required=True, help="Path to the agent CLI binary")
    parser.add_argument("--model", default="", help="Model identifier passed to the agent CLI (empty: CLI default)")
    parser.add_argument("--skill", default=None, help="Only run evals for this skill")
    parser.add_argument("--timeout", type=int, default=300, help="Per-call timeout in seconds")
    args = parser.parse_args()

    items = load_evals(args.skill)
    if not items:
        print(f"No evals found{f' for skill {args.skill!r}' if args.skill else ''}.")
        return 1

    print(f"Running {len(items)} evals with {args.agent} ({args.model or 'default model'}, 2 model calls each)\n")

    results: list[EvalResult] = []
    for index, (skill, item) in enumerate(items, start=1):
        label = f"[{index}/{len(items)}] {skill} eval {item['id']}"
        try:
            result = run_eval(args.agent, args.agent_bin, args.model, skill, item, timeout=args.timeout)
        except (RuntimeError, subprocess.TimeoutExpired, json.JSONDecodeError) as err:
            print(f"  ERROR {label}: {err}")
            failure = {"text": "runner completed the eval", "passed": False, "evidence": str(err)}
            results.append(EvalResult(skill, item["id"], item["prompt"], [failure], ""))
            continue
        results.append(result)
        if result.ok:
            print(f"  PASS  {label}")
        else:
            print(f"  FAIL  {label}")
            for entry in result.failures:
                print(f"          {textwrap.shorten(entry['text'], 80)} — {textwrap.shorten(entry['evidence'], 80)}")

    failed = [r for r in results if not r.ok]
    report = write_report(results)
    print(f"\n{len(results) - len(failed)}/{len(results)} evals passed. Full report: {report}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
