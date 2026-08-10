# Prompting an agent to transform the blueprint

This guide applies **before** the template has been turned into an integration. `initialize.sh` removes it
together with the rest of `docs/blueprint/`, because after the transformation there is nothing left to prompt for.

**Context:** The repository is a fresh, unmodified blueprint template. Turning it into a working integration for one
device or service is a defined procedure, and it lives in the
[`blueprint-scaffold`](../../.agents/skills/blueprint-scaffold/SKILL.md) agent skill — not in this document. The skill
carries the layer order, the manifest classification, what happens to each example platform, and the validation steps.

Your prompt only has to supply the facts the skill cannot know, and point the agent at it. The Coding Agent runs in
GitHub Actions and reads `AGENTS.md` natively; naming the skill file explicitly is the reliable way to load it there.

## What to Include in Your Prompt

**Essential information:**

- **High-level idea** - What the device/service does (2-3 sentences)
- **API/Protocol** - How to connect (REST/MQTT/WebSocket, authentication)
- **Example API response** - Paste an actual captured JSON/data structure. This is the one thing the agent cannot
  derive or guess; entities built against an invented payload look finished and fail on first contact with the device.

**Optional (the agent works these out):**

- Config flow requirements - determined from the authentication and connection details
- Which example platforms to keep or remove - determined from the API structure
- Rate limits or API considerations - include if critical

## Prompt Template

```markdown
Follow .agents/skills/blueprint-scaffold/SKILL.md to transform this blueprint for [DEVICE/SERVICE NAME].

High-level: [2-3 sentences about what it does]

API Details:

- Protocol: [REST/GraphQL/WebSocket/MQTT/etc.]
- Endpoint: [base URL or connection details]
- Auth: [API key/OAuth/none]
- Push or poll: [and how often]
- Stable identifier for the config entry unique ID: [serial/MAC/account ID]

Example API response:
[paste JSON or data structure from actual device/service]
```

## Example: Smart Thermostat

```markdown
Follow .agents/skills/blueprint-scaffold/SKILL.md to transform this blueprint for MyDevice Smart Thermostat.

High-level: Smart thermostat that controls temperature via REST API. Reads current
temp/humidity, sets target temperature, changes heating/cooling mode.

API Details:

- Protocol: REST API
- Endpoint: http://{host}/api/v1/
- Auth: API key in X-API-Key header
- Push or poll: poll, 30s is fine
- Stable identifier: "serial" field from /info

Example API response from /status:
{
"temp": {"current": 21.5, "target": 22.0},
"humidity": 45,
"mode": "heat",
"state": "heating"
}
```

The skill decides the rest: which example platforms survive, the order the layers are built in, and what has to be
green before the work counts as done.

> [!TIP]
> Migrating an **existing** integration rather than starting from scratch is a different procedure with different
> risks — see [`blueprint-import`](../../.agents/skills/blueprint-import/SKILL.md) and [MIGRATION.md](MIGRATION.md).
