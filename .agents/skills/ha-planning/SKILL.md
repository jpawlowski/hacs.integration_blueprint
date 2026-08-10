---
name: ha-planning
description: >-
  Plan a large change to this Home Assistant custom integration before writing code, or record an architectural
  decision. Use when asked to "create a plan", "plan this feature", "how should we approach", "propose an
  architecture", "write an ADR", "document this decision", "should we use library X or write our own client", or
  whenever a change would touch more than about ten files or alter the integration's structure. Covers when a plan
  is mandatory, the phased plan format, where plans live, when a decision is worth recording, and the DECISIONS.md
  entry format used by this project. SYMPTOMS — load this if you are about to: start a refactor spanning more than
  ten files without confirmation; write a plan whose phases name no files; create a planning markdown file outside
  `.agents/scratch/`; or make a hard-to-reverse architectural choice without recording why.
---

# Plan changes and record decisions

## When a plan is required

| Situation                                        | What to do                                             |
| ------------------------------------------------ | ------------------------------------------------------ |
| Single feature or fix, up to ~8 files            | Just implement it completely; no plan needed           |
| Several independent features                     | Implement one at a time, suggest a commit between each |
| >10 files, or an architectural/structural change | **Write a plan and get explicit confirmation first**   |
| A choice with long-term consequences             | Write the plan _and_ record the decision               |

Do not start a large refactor because it seems obviously right. The developer decides scope.

## Writing the plan

Plans are working documents, not deliverables. Put them in `.agents/scratch/` — that directory is gitignored and exists for
exactly this. Do not create markdown files elsewhere in the repository without being asked.

Structure:

```markdown
# Plan: <what and why in one line>

## Goal

<What changes for the user when this is done. One paragraph.>

## Current state

<What exists today, with concrete file references. What specifically is in the way.>

## Approach

<The chosen approach in a few sentences, and what you deliberately did not choose.>

## Phases

### Phase 1 — <name>

- **Files:** `custom_components/<domain>/coordinator/base.py`, …
- **Changes:** <specific edits>
- **Verification:** `script/test tests/test_init.py`, and <what to check in the UI>
- **Independently shippable:** yes / no

### Phase 2 — …

## Breaking changes

<None, or: what breaks and the migration path. See ha-breaking-changes.>

## Risks and open questions

<What could go wrong, and what you need the developer to decide.>
```

Rules that make a plan useful:

- Every phase names actual files. "Refactor the coordinator" is not a phase.
- Every phase ends in a verifiable state — the test suite passes and Home Assistant still starts.
- Order phases so the risky, uncertain part comes early. Discovering the approach is wrong in phase 1 is cheap; in
  phase 5 it is not.
- Keep phases independently reviewable, ideally one commit each.
- Say what you are **not** doing. Scope creep in a plan is scope creep in the implementation.

Present the plan, wait for confirmation, then implement phase by phase. Report deviations from the plan as they happen
rather than at the end.

## Recording a decision

Record a decision in `docs/development/DECISIONS.md` when it is expensive to reverse and the reasoning would otherwise
be lost:

- Third-party library vs. own API client (this is the most common one — see the decision process in `AGENTS.md`).
- Polling vs. push, and the update interval.
- Data structure of `coordinator.data`, or the shape of `entry.data`.
- Device modelling: one device per entry, per subentry, or a hub with children.
- Unique ID scheme.
- Anything you had to argue yourself into.

Do **not** record: routine implementation choices, anything the code already makes obvious, or a restatement of a Home
Assistant convention.

### Entry format

Append to the decision log in `docs/development/DECISIONS.md`, matching the entries already there:

```markdown
### <Decision in imperative form, e.g. "Use aiohttp directly instead of the vendor SDK">

**Date:** YYYY-MM-DD

**Context:** <The situation that forced a choice. What constraint made this non-obvious.>

**Decision:** <What was decided, stated plainly.>

**Rationale:**

- <Why this option won>
- <What the alternatives were and why they lost>

**Consequences:**

- <What this now obliges the code to do>
- <What becomes harder, and what we accept as a trade-off>
```

Be honest in **Consequences**. A decision record that lists only benefits is marketing, and it is useless to the person
who has to revisit it in two years.

Keep entries in the "Decision Log" section in chronological order, newest last, separated by `---`. Entries that were
later reversed stay in the log — add a new entry that supersedes them and say so, rather than editing history.

## Handoff

When a plan spans more than one session, leave the plan file in `.agents/scratch/` with phase checkboxes updated, so the
next session can pick it up without re-deriving the context.
