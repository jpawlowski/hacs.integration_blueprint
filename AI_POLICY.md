# Community AI Development Policy

This project supports the use of AI tools in the development of Home Assistant custom integrations. AI-assisted
development can make useful integrations possible when a contributor would otherwise lack the time or specialized
knowledge to build them.

## Scope

Home Assistant custom integrations, commonly distributed through HACS, are community projects. They are not part of
Home Assistant Core and are not automatically subject to the contribution rules of the Open Home Foundation (OHF).
Core policies may still provide valuable guidance, but this project does not assume that every restriction appropriate
for Core is also appropriate for an independently maintained community integration.

If code from this project is contributed to an OHF repository, the current
[OHF AI Policy](https://developers.home-assistant.io/docs/ai_policy/) applies to that contribution.

## AI use is welcome

AI tools may be used for any part of development, including research, implementation, tests, documentation, review,
and project initialization. An integration may be substantially or predominantly AI-generated. This project values a
useful, inspectable attempt to solve a community problem over requiring that every project could have been completed
without AI.

AI assistance does not by itself determine software quality. Handwritten and AI-generated code are held to the same
automated checks and architectural standards provided by this blueprint.

## Transparency enables informed decisions

Users choose whether to install a custom integration and accept the associated risk. Maintainers must not create a
misleading impression of the integration's maturity or level of verification. When relevant, project documentation
should distinguish between:

- the extent of AI assistance;
- the extent of human code review and maintainer understanding;
- automated test coverage and results;
- testing with real devices or services;
- known limitations, untested areas, and security-sensitive uncertainty; and
- the integration's maturity, such as experimental, beta, or stable.

AI usage, human review, automated testing, and real-world testing are separate facts. Passing linters or tests must not
be presented as proof that a maintainer fully understands the code, and extensive AI use must not be presented as proof
that the code is low quality.

## Maintainer responsibility

Maintainers are encouraged to understand and oversee as much of their integration as reasonably possible, especially
when distributing it through HACS. They remain responsible for honestly documenting what they have and have not
reviewed or tested, responding to safety and security concerns, and avoiding unsupported claims about reliability.

Where complete manual review is impractical, stronger indirect safeguards become more important. These include focused
modules, type checking, linting, Home Assistant validation, automated tests for important behavior and regressions, and
real-device testing where available. Automated checks reduce risk; they do not eliminate it.

## Agents and publication

Review expectations depend on what the agent produced. Generated code and other repository changes that can alter the
integration, its distribution, security, privacy or user-visible behaviour must receive human review proportionate to
their risk before they are merged or released. Maintainer attention is finite, so reviewing code, security-sensitive
work and consequential project decisions takes priority over polishing external prose. Agents must never represent
code as human-reviewed, understood or tested when that has not occurred.

External communication is different. A maintainer may explicitly delegate both writing and sending replies to issues,
pull requests, email or other online discussions. This project does not require the maintainer to review each such
reply before it is sent or published: the purpose of the delegation is to let a volunteer maintainer spend scarce time
on the integration itself while contributors still receive timely, considerate answers. An instruction to write and
send or post a reply is sufficient authority to do both without a separate approval of the finished wording. If the
maintainer asks for a draft or says they want to review it first, the agent must stop before sending or publication.
The destination project's rules always take precedence.

Delegating the communication does not delegate a decision the maintainer has not made. Where the substance depends on
a missing technical judgment, policy position or support commitment, the agent must ask instead of inventing one. Once
the maintainer has made the decision, the agent may communicate it, handle the discussion and carry out an explicitly
requested close or other moderation action.

A reply written on a maintainer's behalf should read in the maintainer's own voice — first person, and plain about
what is required rather than merely suggested. Declining an ordinary good-faith contribution should take one brief
reason rather than a bare no; spam, harassment, and sensitive security handling need no detailed public explanation.
The reply should match the language of the thread it responds to. Where no visible bot or app identity marks the
message as agent-authored, it should carry a short disclaimer matching the actual level of human involvement. For
an unreviewed reply: "An AI agent wrote this on my behalf, unreviewed by me. The work behind it is mine; I delegated
only the writing." A reply the maintainer reviewed must not claim to be unreviewed. Reading naturally and disclosing
authorship are not in tension: the first is for the reader's benefit, the second means no one has to assume the
maintainer typed it themselves.

This deliberately differs from the OHF rule against unreviewed agent-written communication; it does not relax that rule
when contributing to an OHF project. Community integrations are often maintained by one volunteer in limited personal
time. Transparency and retained maintainer control over decisions are the safeguards here; mandatory advance review of
every agent-written message is not.

Deterministic automation such as dependency updates, release workflows, and template synchronization is not treated as
AI authorship merely because it opens a pull request. Its output should still be reviewed according to the risk of the
change.

## Contributing upstream to Open Home Foundation

The rules above govern this repository. The moment a contribution is aimed at an Open Home Foundation repository —
`home-assistant/core`, the developer documentation, the brands repository — the [OHF AI
policy](https://developers.home-assistant.io/docs/ai_policy) applies instead, and it is stricter:

- **Agents must never open an issue, pull request, or comment there.** Autonomous contributions are closed on sight,
  and that includes anything that bypasses the issue or pull request templates. Prepare the material locally and hand
  it to a human to submit.
- **Do not use AI to answer a maintainer's question.** A contributor is expected to understand and explain their own
  work.
- If AI-generated context is quoted in a discussion, it belongs in a quote block, is disclosed as such, and is
  accompanied by the contributor's own reasoning about why it is relevant. Long pasted transcripts are not welcome.
- An AI-drafted pull request description still has to be checked for technical accuracy by the person submitting it.

Home Assistant also runs AI review bots of its own. Their comments are not authoritative — maintainers decide.

## Purpose of this blueprint

This blueprint helps both humans and AI agents work at a useful level of abstraction. Its prescribed architecture,
small modules, type hints, validation scripts, and Home Assistant patterns are intended to make generated code easier
to inspect and verify. They are safeguards, not a guarantee of correctness or a substitute for transparent maintenance.
