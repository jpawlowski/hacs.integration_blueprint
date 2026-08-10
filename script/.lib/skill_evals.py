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

Invoked by script/skill-evals; not intended to be run directly.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import json
from pathlib import Path
import subprocess
import sys
import textwrap

SKILLS_DIR = Path(".agents/skills")
REPORT_DIR = Path(".agents/scratch")

ANSWER_PREAMBLE = """\
You are working in this Home Assistant custom integration repository. Answer the request
below the way you normally would: consult the repository's own agent skills, instructions
and code as needed.

Do not modify any files. Describe what you would do and show the code you would write.

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


def run_agent(agent_bin: str, model: str, prompt: str, timeout: int, *, repo_access: bool) -> str:
    """
    Send a prompt to the agent CLI and return its stdout.

    The prompt goes in on stdin rather than through -p: judge prompts embed a full answer
    and would otherwise risk the argv length limit. Writes are denied in both passes — an
    eval must never mutate the repository it is measuring.
    """
    argv = [agent_bin, "--model", model, "--no-color", "--log-level", "none"]
    if repo_access:
        argv += ["--allow-tool=shell(rg)", "--allow-tool=shell(cat)", "--allow-tool=shell(ls)"]
    argv += ["--deny-tool=write", "--deny-tool=shell(git)", "--deny-tool=shell(rm)"]

    completed = subprocess.run(
        argv,
        input=prompt,
        capture_output=True,
        text=True,
        timeout=timeout,
        check=False,
    )
    if completed.returncode != 0:
        message = completed.stderr.strip() or "agent CLI exited non-zero"
        raise RuntimeError(message)
    return completed.stdout.strip()


def judge(agent_bin: str, model: str, item: dict, answer: str, timeout: int) -> list[dict]:
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
    raw = run_agent(agent_bin, model, prompt, timeout, repo_access=False)
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


def run_eval(agent_bin: str, model: str, skill: str, item: dict, timeout: int) -> EvalResult:
    """Run one eval end to end."""
    answer = run_agent(agent_bin, model, ANSWER_PREAMBLE + item["prompt"], timeout, repo_access=True)
    results = judge(agent_bin, model, item, answer, timeout)
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
    parser.add_argument("--agent-bin", required=True, help="Path to the agent CLI binary")
    parser.add_argument("--model", required=True, help="Model identifier passed to the agent CLI")
    parser.add_argument("--skill", default=None, help="Only run evals for this skill")
    parser.add_argument("--timeout", type=int, default=300, help="Per-call timeout in seconds")
    args = parser.parse_args()

    items = load_evals(args.skill)
    if not items:
        print(f"No evals found{f' for skill {args.skill!r}' if args.skill else ''}.")
        return 1

    print(f"Running {len(items)} evals with {args.model} (2 model calls each)\n")

    results: list[EvalResult] = []
    for index, (skill, item) in enumerate(items, start=1):
        label = f"[{index}/{len(items)}] {skill} eval {item['id']}"
        try:
            result = run_eval(args.agent_bin, args.model, skill, item, args.timeout)
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
