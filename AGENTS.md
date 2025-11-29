# AI Agent Instructions

This document provides guidance for AI coding agents working on this Home Assistant custom integration project.

## Project Overview

This is a Home Assistant custom integration that was generated from a blueprint template. The integration follows Home Assistant Core development patterns and quality standards.

**Integration details:**

- **Domain:** `ha_integration_domain`
- **Title:** Integration Blueprint
- **Repository:** jpawlowski/hacs.integration_blueprint

**Key directories:**

- `custom_components/ha_integration_domain/` - Main integration code
- `config/` - Home Assistant configuration for local testing
- `tests/` - Unit and integration tests
- `script/` - Development and validation scripts

**Local Home Assistant instance:**

When testing the integration, you'll need to run Home Assistant locally using `./script/develop`. Important considerations:

- **Assume unpredictable state** - Developer may have an instance running, or may have stopped it
- **You can force restart anytime** - Use commands that ensure clean state
- **Avoid checking if running** - This leads to unnecessary loops and confusion

**Recommended approach for starting Home Assistant:**

```bash
# Kill any existing instance first, then start fresh
pkill -f "hass --config" || true && pkill -f "debugpy.*5678" || true && ./script/develop
```

This ensures:

- Any existing instance (yours or developer's) is stopped
- The debugpy debugger process on port 5678 is terminated
- Fresh start with known state
- No ambiguity about what's running
- `|| true` prevents error if nothing was running

**Why kill debugpy?** The `./script/develop` script starts Home Assistant with debugpy listening on port 5678. If you only kill the `hass` process but not debugpy, the port remains blocked and prevents clean restarts.

**When to restart Home Assistant:**

- After modifying integration code (Python files)
- After changing `manifest.json` or `services.yaml`
- After updating translations
- When testing config flow changes
- When log output is needed to verify behavior

**Reading logs:**

- Live logs: Shown directly in terminal where `./script/develop` runs
- Log file: `config/home-assistant.log` (most recent)
- Previous log: `config/home-assistant.log.1`

**Adjusting log levels:**

The `config/configuration.yaml` contains log level configuration optimized for integration development:

- **Your integration:** `custom_components.ha_integration_domain: debug` (shows everything)
- **Most HA components:** Reduced to `warning` or `error` to minimize noise
- **Important helpers:** `update_coordinator`, `entity_registry`, `config_entries` set to `info`

**When you need more logging from a specific component:**

1. Check `config/configuration.yaml` under `logger: logs:` section
2. Add or modify the log level for the component you need
3. Restart Home Assistant to apply changes

Example - if you need to see HTTP requests:

```yaml
logger:
  logs:
    homeassistant.components.http: debug  # Change from warning to debug
```

**You are allowed to modify log levels in configuration.yaml** when debugging requires visibility into specific components. Just restart Home Assistant after changes.

**Context-specific instructions:**

If you're using GitHub Copilot, path-specific instructions in `.github/instructions/*.instructions.md` provide additional guidance for specific file types (Python, YAML, JSON, etc.). This document serves as the primary reference for all agents.

## Working With Developers

### When Instructions Conflict With Requests

If a developer requests something that contradicts these instructions:

1. **Clarify the intent** - Ask if they want you to deviate from the documented guidelines
2. **Confirm understanding** - Restate what you understood to avoid misinterpretation
3. **Suggest instruction updates** - If this represents a permanent change in approach, offer to update these instructions
4. **Proceed once confirmed** - Follow the developer's explicit direction after clarification

**Example:**
> "These instructions specify 4-space indentation, but you're asking for tabs. Should I proceed with tabs for this file, or would you like me to update the project guidelines?"

### Maintaining These Instructions

**This project was recently initialized from a template.** Instructions should evolve as the project matures:

- **Refine guidelines** based on actual project needs
- **Remove outdated rules** that no longer apply
- **Consolidate redundant sections** to prevent bloat
- **Keep files focused** - Move architectural decisions to `docs/development/`

**Critical: Keep instruction files manageable.**

- `AGENTS.md` should stay under ~650 lines
- Path-specific `.instructions.md` files should stay under ~300 lines each
- When adding new rules, consider removing or consolidating old ones
- Archive historical context in separate documentation, not in instructions

**Propose updates when:**

- You notice repeated deviations from documented patterns
- Instructions become outdated or contradict actual code
- New patterns emerge that should be standardized
- Files are approaching size limits

### Documentation vs. Instructions

**Three types of content with clear separation:**

1. **Agent Instructions** - How AI should write code
   - Location: `.github/instructions/`, `AGENTS.md`
   - Audience: AI agents and maintainers
   - Maintained collaboratively

2. **Developer Documentation** - Architecture and design decisions
   - Location: `docs/development/`
   - Files: `ARCHITECTURE.md`, `DECISIONS.md`, optional `ROADMAP.md`
   - Audience: Integration developers and maintainers
   - Created when asked, or suggested for significant architectural decisions

3. **User Documentation** - End-user guides and help
   - Location: `docs/user/`
   - Files: `GETTING_STARTED.md`, `CONFIGURATION.md`, optional `EXAMPLES.md`
   - Audience: Home Assistant users installing this integration
   - Created when asked, or suggested for complex features

**AI Planning and Temporary Notes:**

- Location: `.ai-scratch/` (ignored by git)
- Purpose: Temporary planning, task breakdowns, implementation notes
- Only for AI use during complex work - never committed
- Keep files focused: `plan.md`, `notes.md`, `refactoring.md`

**Rules for creating documentation:**

- ❌ **NEVER** create random markdown files (README.md, GUIDE.md, etc.) in code directories
- ❌ **NEVER** create markdown files outside `docs/` or `.ai-scratch/` without explicit permission
- ❌ **NEVER** create "helpful" READMEs in package directories - use module docstrings instead
- ✅ **ALWAYS ask first** before creating permanent documentation
- ✅ **Prefer module/class/function docstrings** over separate markdown files
- ✅ **Prefer extending** existing docs over creating new files
- ✅ **Suggest documentation** for complex features or significant decisions (but ask first!)
- ✅ **Use `.ai-scratch/`** for all temporary planning and notes

**The developer can see the structure through:**

- VS Code's file tree and symbol navigation
- Google-style docstrings in code
- Type hints and function signatures
- Module-level documentation strings

**Example suggestions:**

- "This architectural decision affects the coordinator design. Should I document it in `docs/development/DECISIONS.md`?"
- "This config flow has many options. Would you like me to create user documentation in `docs/user/CONFIGURATION.md`?"
- "I'll create a temporary plan in `.ai-scratch/plan.md` to track this multi-step refactoring."

### Session and Context Management

**Commit suggestions:**

When a task completes and the developer moves to a new topic, suggest committing changes before proceeding. Offer a commit message based on the work done - you have the full context now, they won't later.

**Commit message format:**

Follow [Conventional Commits](https://www.conventionalcommits.org/) specification:

```text
type(scope): short summary (max 72 chars)

- Optional detailed points
- Reference issues if applicable
```

**Always check git diff first** - don't rely on session memory. Include all changes in your message.

**Common types:**

- `feat:` - User-facing functionality (new sensor, service, config option)
- `fix:` - Bug fixes (user-facing issues)
- `chore:` - Dev tools, dependencies, devcontainer (NOT user-facing)
- `refactor:` - Code restructuring (no functional change)
- `docs:` - Documentation changes

**Examples:**

```text
feat(sensor): add air quality index sensor

fix(config_flow): validate host format before connection
- Fixes #123
```

**Context monitoring:**

If context grows large (~50k+ tokens) and a new topic starts, warn the developer and offer to create a session summary. Suggest once per topic transition, then respect their decision.

## Code Style and Quality

### Python (`.py` files)

**Formatting:**

- 4 spaces for indentation (never tabs)
- Max line length: 120 characters
- Use double quotes for strings consistently

**Type annotations:**

- Use type hints for all function parameters and return values
- Import from `typing` or `collections.abc` as needed
- Use `from __future__ import annotations` for forward references

**Common type annotation patterns:**

```python
from __future__ import annotations

from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

# Platform setup
async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up sensor platform."""

# Coordinator with typed data
class IntegrationBlueprintDataUpdateCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Class to manage fetching data from the API."""

# Entity with coordinator
class IntegrationBlueprintSensor(
    CoordinatorEntity[IntegrationBlueprintDataUpdateCoordinator],
    SensorEntity,
):
    """Representation of a sensor."""
```

**Async patterns:**

- All I/O operations must be async (never block the event loop)
- Use `async def` for coroutines
- Prefer `asyncio.timeout()` over deprecated `async_timeout`
- Use `asyncio.gather()` for concurrent operations

**Import order:**

1. Future imports (`from __future__ import annotations`)
2. Standard library
3. Third-party libraries
4. Home Assistant core imports
5. Local integration imports

Use standard Home Assistant import aliases:

```python
import voluptuous as vol
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers import entity_registry as er
from homeassistant.util import dt as dt_util
```

**Naming conventions:**

- Classes: `PascalCase` (prefix with `IntegrationBlueprint` namespace)
- Functions/variables: `snake_case`
- Constants: `UPPER_SNAKE_CASE`
- Private members: `_leading_underscore`

**Docstrings:**

- Use Google-style docstrings for all public classes and functions
- Include links to Home Assistant documentation where relevant
- Document non-obvious parameters; obvious ones can be omitted

**Error handling:**

- Use specific exception types
- Log errors appropriately (`_LOGGER.error()`, `_LOGGER.warning()`)
- Handle coordinator failures gracefully (entities become unavailable)
- Never let exceptions crash the integration

**Home Assistant specific "Don'ts":**

- ❌ **NEVER** use `time.sleep()` - Use `await asyncio.sleep()` instead
- ❌ **NEVER** use blocking I/O in async functions - Use aiohttp, aiofiles, etc.
- ❌ **NEVER** access `hass.states` directly in entities - Use coordinator data
- ❌ **NEVER** import from other integrations (`homeassistant.components.X`) - Only from your own integration
- ❌ **NEVER** hardcode URLs, API keys, or secrets - Use config entries or constants
- ❌ **NEVER** modify `hass.data` from outside `async_setup_entry` - Use coordinator for shared data
- ❌ **NEVER** use `@property` methods that do I/O - Properties must be synchronous
- ❌ **NEVER** catch broad exceptions without re-raising (`except Exception: pass`) - Always log and handle appropriately

### YAML Files

**Home Assistant configuration and blueprints:**

- 2 spaces for indentation
- Use modern trigger/condition/action syntax (not legacy `platform:` style)
- Always include descriptive `alias:` for automations
- Use proper service call syntax: `service: domain.service_name`

**Example (modern style):**

```yaml
automation:
  - alias: "Example automation"
    trigger:
      - trigger: state
        entity_id: binary_sensor.example
        to: "on"
    condition:
      - condition: state
        entity_id: input_boolean.enable
        state: "on"
    action:
      - action: light.turn_on
        target:
          entity_id: light.example
```

### JSON Files

**Configuration files (manifest.json, etc.):**

- 2 spaces for indentation
- No trailing commas
- No comments (JSON spec doesn't support them)
- Validate against schema when available

## Project-Specific Rules

### Integration Identifiers

This integration uses the following identifiers consistently:

- **Domain:** `ha_integration_domain`
- **Title:** Integration Blueprint
- **Class prefix:** `IntegrationBlueprint`

**When creating new files:**

- Use the domain `ha_integration_domain` for all DOMAIN references
- Prefix all integration-specific classes with `IntegrationBlueprint`
- Use "Integration Blueprint" as the display title
- Never hardcode different values

### Integration Structure

**Entity organization:**

- Each platform has its own directory: `sensor/`, `binary_sensor/`, `switch/`, etc.
- Platform `__init__.py` contains `async_setup_entry()` and entity list
- Individual entity classes in separate files (e.g., `air_quality.py`)
- Use `EntityDescription` dataclasses for static entity metadata

**Code organization principles:**

- **Keep files focused and manageable** - Aim for 200-400 lines per file maximum
- **Split large modules** - If a file exceeds ~500 lines, refactor into smaller modules
- **One class per file** for entity implementations (sensors, switches, etc.)
- **Group related utilities** - Helper functions in `utils/`, shared types in separate files
- **Avoid monolithic files** - You need to be able to read and modify these files later

**When files grow too large:**

1. Extract helper functions to `utils/` directory
2. Split entity classes into separate files
3. Move constants to `const.py`
4. Create subpackages for related functionality
5. Use clear, descriptive file names

**Remember:** AI models have context limits. Keep files small enough to process efficiently.

**Coordinator pattern:**

- All data fetching goes through `IntegrationBlueprintDataUpdateCoordinator`
- Entities inherit from both platform base and `IntegrationBlueprintEntity`
- Update interval configured in `coordinator.py`
- Handle `UPDATE_FAILED` exceptions gracefully

**API client:**

- Keep API logic in `api/client.py`
- Use aiohttp for HTTP requests
- Implement proper error handling and timeouts
- Raise custom exceptions from `exceptions.py`

### Device Info

All entities should provide consistent device info via the base entity class. Device info should include:

- Manufacturer, model, serial number
- Configuration URL if applicable
- Software/firmware version if available

## Validation Scripts

**Before committing, run:**

```bash
script/check      # Full validation (type + lint + spell)
script/lint       # Auto-format and fix linting issues
script/type-check # Pyright type checking only
script/test       # Run unit tests
```

**Configured tools:**

- **Ruff** - Fast Python linter and formatter ([Rules Reference](https://docs.astral.sh/ruff/rules/))
- **Pyright** - Type checker configured for "basic" mode ([Docs](https://microsoft.github.io/pyright/))
- **pytest** - Test runner with async support ([Docs](https://docs.pytest.org/))

**Use these tools proactively:**

- Run `script/check` while developing, not just before committing
- Look up specific Ruff error codes to understand issues
- Check Pyright documentation when type errors are unclear
- These tools are your friends - consult their docs liberally

**Linter overrides:**

- You may use `# noqa: CODE` or `# type: ignore` when genuinely necessary
- Use sparingly and only with good reason (e.g., false positives, external library issues)
- Always include the specific error code, never blanket `# noqa`
- Add a comment explaining why the override is needed
- Prefer fixing the underlying issue over suppressing warnings

**Example:**

```python
from external_lib import something  # noqa: F401 - Required for plugin registration
result = complex_type_inference()  # type: ignore[attr-defined] - Library lacks stubs
```

**Common issues to avoid:**

- Missing type annotations
- Using sync I/O in async functions
- Importing from `tests` in production code
- Unused imports or variables (Ruff will catch these)
- Magic values without constants (use module-level CONSTANTS)

### Error Recovery Strategy

**When validation fails (`script/check` errors):**

1. **First attempt** - Fix the specific error reported by the tool
2. **Second attempt** - If it fails again, reconsider your approach (maybe your understanding was wrong)
3. **Third attempt** - If still failing, ask for clarification rather than looping indefinitely
4. **After 3 failed attempts** - Stop and explain what you tried and why it's not working

**When tool operations fail:**

- **File read/write errors** - Verify path exists, check for typos, try once more
- **Terminal timeouts** - Don't retry automatically; inform the user and suggest manual intervention
- **API/network timeouts in tests** - Mention in response, don't silently ignore
- **Git operations fail** - Report the error immediately; don't attempt to work around it

**When gathering context:**

- Start with semantic_search (1-2 queries maximum)
- Read 3-5 most relevant files based on search results
- If still unclear, read 2-3 more specific files
- **After ~10 file reads, you should have enough context** - make a decision or ask for clarification
- Don't fall into infinite research loops

**Context gathering strategy:**

1. **First pass** - semantic_search to find relevant areas (1-2 queries)
2. **Second pass** - Read the 3-5 most relevant files identified
3. **Evaluate** - Do you have enough context to proceed? If yes, start implementation
4. **Third pass (if needed)** - Read 2-3 additional specific files for missing details
5. **Decision point** - After ~10 file reads total, you must either:
   - Proceed with implementation based on available context
   - Ask the developer specific questions about what's unclear
   - Never continue searching indefinitely without making progress

## Testing

**Test structure:**

- `tests/` mirrors `custom_components/ha_integration_domain/` structure
- Mark tests: `@pytest.mark.unit` for fast tests, `@pytest.mark.integration` for coordinator tests
- Use fixtures for common setup (Home Assistant mock, coordinator, etc.)
- Mock external API calls

**Running tests:**

```bash
script/test              # All tests
script/test --cov-html   # With coverage report
```

## Home Assistant Patterns

**Config flow:**

- Main implementation in `config_flow_handler/config_flow.py`
- Options flow in `config_flow_handler/options_flow.py`
- Schemas organized in `config_flow_handler/schemas/`
- Validators in `config_flow_handler/validators/`
- Support reauthentication via `async_step_reauth()`
- Validate user input and show appropriate errors
- Use `DOMAIN` constant for all references

**Services:**

- Define in `services.yaml` with full descriptions
- Implement handlers in `services/` directory
- Use voluptuous schemas for validation
- Register in `async_setup_entry()`

**Entity availability:**

- Set `_attr_available = False` when device is unreachable
- Update availability based on coordinator success/failure
- Don't raise exceptions from `@property` methods

**State updates:**

- Use `self.async_write_ha_state()` for immediate updates
- Let coordinator handle periodic updates
- Minimize API calls (batch requests when possible)

## Breaking Changes

**Always warn the developer before making changes that:**

- Change entity IDs or unique IDs (users' automations will break)
- Modify config entry data structure (existing installations will fail)
- Change state values or attributes format (dashboards and automations affected)
- Alter service call signatures (user scripts will break)
- Remove or rename config options (users must reconfigure)

**Never do without explicit approval:**

- Removing config options (even if "unused")
- Changing service parameters or return values
- Modifying how data is stored in config entries
- Renaming entities or changing their device classes
- Changing unique_id generation logic

**How to warn:**

> "⚠️ This change will modify the entity ID format from `sensor.device_name` to `sensor.device_name_sensor`. Existing users' automations and dashboards will break. Should I proceed, or would you prefer a migration path?"

**When breaking changes are necessary:**

- Document the breaking change in commit message (`BREAKING CHANGE:` footer)
- Consider providing migration instructions
- Suggest version bump (major version change)
- Update documentation if it exists

## File Changes

**Scope Management:**

**Single logical feature or fix:**

- Implement completely even if it spans 5-8 files
- Example: New sensor needs entity class + platform init + translations + tests → implement all together
- Example: Bug fix requires changes in coordinator + entity + error handling → do all at once

**Multiple independent features:**

- Implement one at a time
- After completing each feature, suggest committing before proceeding to the next
- Example: "Add 3 different sensors" → implement first sensor completely, offer to commit, then proceed with second

**Large refactoring (>10 files or architectural changes):**

- Propose a plan first before starting implementation
- Get explicit confirmation from developer
- Example: "Restructure coordinator to support multiple devices" → outline approach, wait for approval

**When in doubt:**

- Prefer completing the current logical unit over stopping mid-implementation
- If the scope seems unclear, ask: "Should I implement X completely, or would you prefer to review after Y?"

**When modifying files:**

- Keep changes focused and minimal
- Update docstrings if behavior changes
- Run validation scripts before considering the task complete

**Important: Do NOT create or modify tests unless explicitly requested.** Your primary task is implementing functionality and fixing bugs. The developer will decide if and when tests are needed.

**When creating new entities:**

1. Create entity file in appropriate platform directory
2. Add entity class inheriting from platform + `IntegrationBlueprintEntity`
3. Add `EntityDescription` if applicable
4. Update platform `__init__.py` to include new entity

## Research and Validation

**When uncertain, consult official documentation:**

- **Always check current patterns** in [Home Assistant Developer Docs](https://developers.home-assistant.io/)
- **Read the blog** at [Home Assistant Developer Blog](https://developers.home-assistant.io/blog/) for recent changes and best practices
- **Search for examples** using Google: `site:developers.home-assistant.io [your topic]`
- **Verify with tools** before assuming - run `script/check` to catch issues early

**Don't rely on assumptions:**

- Home Assistant APIs and patterns evolve frequently
- What worked in older versions may be deprecated
- Use official docs and working examples over guesswork
- When in doubt, search for recent integration examples in Home Assistant Core

**Tool documentation:**

- [Ruff Rules](https://docs.astral.sh/ruff/rules/) - Understand what each rule checks
- [Pyright Configuration](https://microsoft.github.io/pyright/#/configuration) - Type checking options
- Don't hesitate to look up specific error codes when validation fails

## Tool Parallelization

**Safe to call in parallel:**

- Multiple `read_file` operations (different files or different sections of same file)
- `file_search` + `read_file` + `grep_search` (independent read-only operations)
- `semantic_search` followed by parallel `read_file` of results (but only 1 semantic_search at a time)

**Never call in parallel:**

- Multiple `run_in_terminal` commands (execute sequentially, wait for output)
- Multiple `replace_string_in_file` on the same file (use `multi_replace_string_in_file` instead)
- `semantic_search` with other `semantic_search` (execute one at a time)

**Best practices:**

- Batch independent read operations together in one parallel call
- After gathering context in parallel, provide brief progress update before proceeding
- For file edits, use `multi_replace_string_in_file` when making multiple changes
- Terminal commands must always be sequential to see output before next command

## Additional Resources

- [Home Assistant Developer Docs](https://developers.home-assistant.io/) - Primary reference
- [Integration Quality Scale](https://developers.home-assistant.io/docs/integration_quality_scale_index)
- [Architecture Docs](https://developers.home-assistant.io/docs/architecture_index)
- [Ruff Rules](https://docs.astral.sh/ruff/rules/) - Linter documentation
- [Pyright Configuration](https://microsoft.github.io/pyright/#/configuration) - Type checker documentation
- [pytest Documentation](https://docs.pytest.org/) - Testing framework
- See `CONTRIBUTING.md` for contribution guidelines
