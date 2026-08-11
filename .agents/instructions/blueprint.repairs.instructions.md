---
name: "Repair Flows"
description: "Creating issues, implementing RepairsFlow, and deleting issues after a fix"
applyTo: "custom_components/**/repairs.py"
paths:
  - "custom_components/**/repairs.py"
---

# Repairs Instructions

**Procedure:** [`ha-breaking-changes`](../skills/ha-breaking-changes/SKILL.md) — load it before creating an issue.
This file is the rule set; the skill is what a repair issue is _for_ — a migration or a deprecation the user has to
act on — and the warn-first policy that comes before either.

**Official Documentation:**

- [Repairs Framework](https://developers.home-assistant.io/docs/core/platform/repairs)
- [Issue Registry](https://developers.home-assistant.io/docs/core/platform/repairs#issue-registry)

## Overview

Repair Flows guide users through fixing issues (expired credentials, deprecated settings, missing configuration, etc.).

**Key differences from Config Flow:**

- **Location**: `repairs.py` in integration root (NOT in `config_flow_handler/`)
- **Base class**: `homeassistant.components.repairs.RepairsFlow` (NOT `ConfigFlow`)
- **Trigger**: System creates issue → user clicks "Fix" → Repair Flow runs
- **Purpose**: Fix existing problems, not create new config entries

## Architecture

**Lifecycle:**

1. Integration detects issue → `async_create_issue()`
2. User clicks "Fix" → `async_create_fix_flow()` called with issue_id
3. Repair flow guides user through steps
4. Fix applied → `async_delete_issue()`

## Creating Issues

```python
from homeassistant.helpers import issue_registry as ir

ir.async_create_issue(
    hass,
    DOMAIN,
    "issue_id",
    is_fixable=True,  # Shows "Fix" button; requires a fix flow
    severity=ir.IssueSeverity.WARNING,
    translation_key="issue_id",
    translation_placeholders={"key": "value"},  # Optional
    breaks_in_ha_version="2027.1",  # Optional: when this stops working
    learn_more_url="https://…",  # Optional: link to docs/user/
    issue_domain=DOMAIN,  # Optional: only when raising on another integration's behalf
    data={"entry_id": entry.entry_id},  # Optional: reaches async_create_fix_flow
)
```

`is_persistent=True` marks an issue that only exists because it was observed once — an update that failed, an
unknown action in an automation — so it must survive a restart. Leave it off for anything the integration re-checks
on its own, such as a deprecated option found during setup; that one comes back by itself if it is still true.

**Only raise an issue the user can act on.** Something broken that they cannot fix themselves is a log entry, not a
repair.

**Ignoring is sticky.** An ignored issue stays ignored across restarts until it is deleted — by the integration or by
the user completing its flow — and then created again. Re-creating the same `issue_id` on every coordinator update is
therefore harmless; inventing a new id each time defeats the user's choice.

`ir.async_create_issue` must run in the event loop. From a worker thread use `ir.create_issue` / `ir.delete_issue`.

**When to create:**

- During `async_setup_entry()` - Config validity, API compatibility
- In coordinator updates - Deprecated endpoints, expired features
- On API responses - Device warnings, missing capabilities

## Repair Flow Implementation

**Required function in repairs.py:**

```python
async def async_create_fix_flow(
    hass: HomeAssistant,
    issue_id: str,
    data: dict[str, str | int | float | None] | None,
) -> RepairsFlow:
    """Create flow for issue_id."""
    return MyRepairFlow()
```

**When the fix is just "acknowledge and I will handle it", do not write a flow class** — return the built-in one:

```python
from homeassistant.components.repairs import ConfirmRepairFlow

return ConfirmRepairFlow()
```

**Flow class structure** (only when the user has something to enter or choose):

```python
from homeassistant.components.repairs import RepairsFlow
from homeassistant.components.repairs.models import RepairsFlowResult

class MyRepairFlow(RepairsFlow):
    async def async_step_init(self, user_input=None) -> RepairsFlowResult:
        if user_input is not None:
            # Apply fix
            entry = self.hass.config_entries.async_get_entry(self.handler)
            # Update entry, reload if needed
            ir.async_delete_issue(self.hass, entry.domain, "issue_id")
            return self.async_create_entry(data={})

        return self.async_show_form(step_id="init")
```

The form mechanics are Data Entry Flow's and are identical to the config flow's — see
[`blueprint.config_flow`](blueprint.config_flow.instructions.md). Two things differ here:
`async_create_entry(data={})` always takes an **empty** dict, and the issue must be deleted before you return it.

**Redirecting to reauth** is the pattern worth having in full, because the ordering is not obvious — delete the issue
first, then start the flow:

```python
async def async_step_init(self, user_input=None):
    if user_input:
        entry = self.hass.config_entries.async_get_entry(self.handler)
        ir.async_delete_issue(self.hass, entry.domain, "issue_id")
        entry.async_start_reauth(self.hass)
        return self.async_create_entry(data={})
    return self.async_show_form(step_id="init")
```

## Translations

**Exactly one of `fix_flow` and `description` per issue** — never both. Which one depends on `is_fixable`.

Not fixable (`is_fixable=False`) — the user reads it and acts elsewhere:

```json
{
  "issues": {
    "api_key_expired": {
      "title": "Issue title",
      "description": "Description with {placeholder}"
    }
  }
}
```

Fixable (`is_fixable=True`) — the flow's own steps carry the text:

```json
{
  "issues": {
    "deprecated_option": {
      "title": "Issue title",
      "fix_flow": {
        "step": {
          "init": {
            "title": "Repair step title",
            "description": "Instructions"
          }
        }
      }
    }
  }
}
```

## Rules

**MUST:**

- Place `repairs.py` in integration root (NOT in `config_flow_handler/`)
- Implement `async_create_fix_flow()` function returning `RepairsFlow` subclass
- Delete issue after successful repair: `ir.async_delete_issue()`
- Set `is_fixable=True` only if repair flow exists
- Provide translations for all text (title, description, fix_flow steps)
- Validate user input before applying fixes
- Pick severity by tense, not by urgency: `ERROR` — something is broken **now** and needs attention; `WARNING` —
  something breaks **later** (an API shutdown, a removal). `CRITICAL` is reserved for true panic and has no use in
  this integration.

**SHOULD:**

- Keep repair steps simple (1-2 steps maximum)
- Use existing patterns (reauth, reconfigure) when applicable
- Reload entry after config changes: `await hass.config_entries.async_reload(entry.entry_id)`

**NEVER:**

- Copy `from __future__ import annotations` out of the upstream examples — this repository dropped it repo-wide and
  Ruff rejects it
- Put repair flows in `config_flow_handler/` (separate system)
- Leave issues after repair completes (always delete)
- Use repair flows for normal config changes (use reconfigure instead)
- Create issues without translations
- Skip validation of user input
