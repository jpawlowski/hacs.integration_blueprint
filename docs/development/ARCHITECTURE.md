# Architecture Overview

This document describes the technical architecture of the Integration Blueprint custom component for Home Assistant.

## Directory Structure

```text
custom_components/ha_integration_domain/
├── __init__.py              # Integration setup and unload
├── config_flow.py           # Config flow entry point
├── const.py                 # Constants and configuration keys
├── coordinator/             # Data update coordinator package
│   ├── __init__.py          # Exports IntegrationBlueprintDataUpdateCoordinator
│   ├── base.py              # Main coordinator class
│   ├── data_processing.py   # Data validation and transformation
│   ├── error_handling.py    # Error recovery and retry logic
│   └── listeners.py         # Entity callbacks and event listeners
├── data.py                  # Data classes and type definitions
├── diagnostics.py           # Diagnostic data for troubleshooting
├── entity/                  # Base entity package
│   ├── __init__.py          # Exports IntegrationBlueprintEntity
│   └── base.py              # Base entity class implementation
├── manifest.json            # Integration metadata
├── repairs.py               # Repair flows for fixing issues
├── services.yaml            # Service action definitions (legacy filename)
├── api/                     # External API communication
│   ├── __init__.py
│   └── client.py            # API client implementation
├── config_flow_handler/     # Config flow implementation
│   ├── __init__.py          # Package exports
│   ├── handler.py           # Backward compatibility wrapper
│   ├── config_flow.py       # Main config flow (user, reauth, reconfigure)
│   ├── options_flow.py      # Options flow
│   ├── subentry_flow.py     # Subentry flow template
│   ├── schemas/             # Voluptuous schemas
│   │   ├── __init__.py      # Schema exports
│   │   ├── config.py        # Config flow schemas
│   │   └── options.py       # Options flow schemas
│   └── validators/          # Input validation
│       ├── __init__.py      # Validator exports
│       ├── credentials.py   # Credential validation
│       └── sanitizers.py    # Input sanitizers
├── entity_utils/            # Entity helper utilities
│   ├── __init__.py
│   ├── device_info.py       # Device information helpers
│   └── state_helpers.py     # State management utilities
├── service_actions/         # Service action implementations
│   ├── __init__.py
│   └── example_service.py   # Example service action handler
├── translations/            # Localization files
│   └── en.json              # English translations
└── <platform>/              # Platform-specific implementations
    ├── __init__.py          # Platform setup
    └── <entity>.py          # Individual entity implementations
```

## Core Components

### Data Update Coordinator

**Directory:** `coordinator/`

The coordinator package manages periodic data fetching from the external API and distributes
updates to all entities. It is organized as a package with separate modules for different concerns:

**Package structure:**

- `base.py` - Main coordinator class (`IntegrationBlueprintDataUpdateCoordinator`)
- `data_processing.py` - Data validation, transformation, and caching utilities
- `error_handling.py` - Error recovery strategies, retry logic, and circuit breaker patterns
- `listeners.py` - Entity callbacks, event listeners, and performance monitoring

**Core functionality:**

- Configurable update interval (default: 5 minutes)
- Error handling with exponential backoff
- Shared data access for all entities
- Automatic retry on transient failures
- Data validation and transformation before distribution
- Performance monitoring and metrics

**Key class:** `IntegrationBlueprintDataUpdateCoordinator` (exported from `coordinator/__init__.py`)

**Design rationale:**

The coordinator is structured as a package rather than a single file to support future extensibility:

- **Separation of concerns**: Core logic, error handling, and data processing are isolated
- **Easy extension**: New features (caching, metrics, webhooks) can be added as new modules
- **Maintainability**: Individual modules stay focused and manageable (<400 lines)
- **Testability**: Each module can be tested independently

### API Client

**Directory:** `api/`

Handles all communication with external APIs or devices. Implements:

- Async HTTP requests using `aiohttp`
- Connection management and timeouts
- Authentication handling
- Error translation to custom exceptions

**Key class:** `IntegrationBlueprintApiClient`

### Config Flow

**Directory:** `config_flow_handler/`

Implements the configuration UI for adding and configuring the integration. The package
is organized modularly to support complex flows without becoming monolithic.

**Structure:**

- `config_flow.py`: Main flow (user setup, reauth, reconfigure)
- `options_flow.py`: Options flow for post-setup configuration
- `schemas/`: Voluptuous schemas for all forms
- `validators/`: Validation logic separated from flow logic
- `subentry_flow.py`: Template for multi-device/location support

**Supported flows:**

- Initial user setup with validation
- Options flow for reconfiguration
- Reauthentication flow for expired credentials
- Ready for subentry flows (multi-device support)

**Key classes:**

- `IntegrationBlueprintConfigFlowHandler` (main flow)
- `IntegrationBlueprintOptionsFlow` (options)

### Base Entity

**Package:** `entity/`

Provides common functionality for all entities in the integration:

- Device information
- Unique ID generation
- Coordinator integration
- Availability tracking

**Key class:** `IntegrationBlueprintEntity` (in `entity/base.py`)

## Platform Organization

Each platform (sensor, binary_sensor, switch, etc.) follows this pattern:

```text
<platform>/
├── __init__.py              # Platform setup: async_setup_entry()
└── <entity_name>.py         # Individual entity implementation
```

Platform entities inherit from both:

1. Home Assistant platform base (e.g., `SensorEntity`)
2. `IntegrationBlueprintEntity` for common functionality

## Data Flow

```text
┌─────────────────┐
│  Config Entry   │ ← Created by config flow
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Coordinator   │ ← Fetches data from API every 5 min
└────────┬────────┘
         │
         ▼
    ┌────┴────┐
    │  Data   │ ← Stored in coordinator.data
    └────┬────┘
         │
    ┌────┴────────────────┐
    │                     │
    ▼                     ▼
┌─────────┐         ┌─────────┐
│ Sensor  │         │ Switch  │ ← Entities read from coordinator
└─────────┘         └─────────┘
```

## AI Agent Instructions

This project includes comprehensive instruction files for AI coding assistants (GitHub Copilot, Claude, etc.) to ensure consistent code generation that follows Home Assistant patterns and project conventions.

### Instruction File Architecture

**Layered approach:**

1. **`AGENTS.md`** - High-level "survival guide" for all AI agents (project overview, workflow, validation)
2. **`.github/instructions/*.instructions.md`** - Detailed path-specific patterns (applied based on file being edited)
3. **`.github/copilot-instructions.md`** - GitHub Copilot-specific workflow guidance

### Available Instruction Files

| File                                           | Applies To                                            | Purpose                                                                        |
| ---------------------------------------------- | ----------------------------------------------------- | ------------------------------------------------------------------------------ |
| `blueprint.python.instructions.md`             | `**/*.py`                                             | Python code style, imports, type hints, async patterns, linting                |
| `blueprint.yaml.instructions.md`               | `**/*.yaml`, `**/*.yml`                               | YAML formatting, Home Assistant YAML conventions                               |
| `blueprint.json.instructions.md`               | `**/*.json`                                           | JSON formatting, schema validation, no trailing commas                         |
| `blueprint.markdown.instructions.md`           | `**/*.md`                                             | Markdown formatting, documentation structure, linting                          |
| `blueprint.manifest.instructions.md`           | `**/manifest.json`                                    | Integration manifest requirements, quality scale, IoT class                    |
| `blueprint.configuration_yaml.instructions.md` | `**/configuration.yaml`                               | Home Assistant configuration patterns (deprecated for device integrations)     |
| `blueprint.config_flow.instructions.md`        | `**/config_flow_handler/**/*.py`, `**/config_flow.py` | Config flow patterns, discovery, reauth, reconfigure, unique IDs               |
| `blueprint.service_actions.instructions.md`    | `**/service_actions/**/*.py`                          | Service action implementation, registration in `async_setup()`, error handling |
| `blueprint.services_yaml.instructions.md`      | `**/services.yaml`                                    | Service action definitions, schema, descriptions, examples (legacy filename)   |
| `blueprint.entities.instructions.md`           | Entity platform files                                 | Entity implementation, EntityDescription, device info, state management        |
| `blueprint.coordinator.instructions.md`        | `**/coordinator/**/*.py`, `**/api/**/*.py`            | DataUpdateCoordinator patterns, error handling, caching, pull vs push          |
| `blueprint.api.instructions.md`                | `**/api/**/*.py`, `**/coordinator/**/*.py`            | API client implementation, exceptions, rate limiting, pagination               |
| `blueprint.diagnostics.instructions.md`        | `**/diagnostics.py`                                   | Diagnostics data collection, `async_redact_data()` for sensitive data          |
| `blueprint.repairs.instructions.md`            | `**/repairs.py`                                       | Repair flows, issue creation, severity levels, fix flows                       |
| `blueprint.translations.instructions.md`       | `**/translations/*.json`                              | Translation file structure, placeholders, nested keys                          |
| `blueprint.tests.instructions.md`              | `tests/**/*.py`                                       | Test patterns, fixtures, mocking, pytest conventions                           |

> [!NOTE]
> Entity platform files include: `alarm_control_panel/**/*.py`, `binary_sensor/**/*.py`, `button/**/*.py`, `camera/**/*.py`, `climate/**/*.py`, `cover/**/*.py`, `fan/**/*.py`, `humidifier/**/*.py`, `light/**/*.py`, `lock/**/*.py`, `number/**/*.py`, `select/**/*.py`, `sensor/**/*.py`, `siren/**/*.py`, `switch/**/*.py`, `vacuum/**/*.py`, `water_heater/**/*.py`, `entity/**/*.py`, `entity_utils/**/*.py`

### Instruction File Application

**GitHub Copilot:**

Uses frontmatter `applyTo` patterns to automatically apply instructions based on file being edited:

```yaml
---
applyTo:
  - "**/*.py"
---
```

**Other AI Agents:**

Typically read `AGENTS.md` for project overview and may use path-specific instructions when available.

### Benefits

- ✅ **Consistent code quality** - AI generates code that passes validation on first run
- ✅ **Home Assistant patterns** - Follows Core development standards and best practices
- ✅ **Context-aware** - File-specific instructions ensure appropriate patterns
- ✅ **Reduced iteration** - Fewer validation errors and corrections needed
- ✅ **Knowledge transfer** - Instructions document project conventions and decisions

### Maintaining Instructions

- Keep `AGENTS.md` concise (high-level guidance only, ~30,000 ft view)
- Put detailed patterns in path-specific `.instructions.md` files
- Update instructions when patterns change or new conventions emerge
- Remove outdated rules to prevent bloat
- Document major architectural decisions in `DECISIONS.md`

### Using GitHub Copilot Coding Agent

**GitHub Copilot Coding Agent** ([github.com/copilot/agents](https://github.com/copilot/agents)) can autonomously initialize new projects from this template and implement features.

**Template Initialization:**

When creating a repository from this template, you can provide a prompt to Copilot Coding Agent that includes:

- Integration domain, title, and repository details
- Instructions to run `initialize.sh` in unattended mode with `--force` flag
- The agent will set up the project and create an initialization pull request

**Working with initialized projects:**

Once a project is initialized, Copilot Coding Agent:

- Automatically reads all instruction files (`AGENTS.md`, `.github/copilot-instructions.md`, `.github/instructions/*.instructions.md`)
- Runs validation scripts (`script/check`) to verify changes
- Creates pull requests with comprehensive implementations
- Can iterate based on test failures and linter errors

**Agent-specific instructions (since November 2025):**

Use `excludeAgent` frontmatter to control which agents use specific instructions:

```yaml
---
applyTo: "**/*.py"
excludeAgent: "code-review" # Only coding-agent uses this
---
```

See [`COPILOT_AGENT.md`](./COPILOT_AGENT.md) for detailed usage instructions, example prompts, and troubleshooting.

## Key Design Decisions

See [DECISIONS.md](./DECISIONS.md) for architectural and design decisions made during development.

## Extension Points

To add new functionality:

### Adding a New Platform

1. Create directory: `custom_components/ha_integration_domain/<platform>/`
2. Implement `__init__.py` with `async_setup_entry()`
3. Create entity classes inheriting from platform base + `IntegrationBlueprintEntity`
4. Add platform to `PLATFORMS` in `const.py`

### Adding a New Service Action

1. Create service action handler in `service_actions/<service_name>.py`
2. Define service action in `services.yaml` (legacy filename) with schema
3. Register service action in `__init__.py:async_setup()` (NOT `async_setup_entry`)

### Modifying Data Structure

1. Update coordinator data type in `coordinator.py`
2. Adjust API client response parsing in `api/client.py`
3. Update entity property implementations to match new structure

## Testing Strategy

- **Unit tests:** Test individual functions and classes in isolation
- **Integration tests:** Test coordinator with mocked API
- **Fixtures:** Shared test fixtures in `tests/conftest.py`

Tests mirror the source structure under `tests/`.

## Dependencies

Core dependencies (see `manifest.json`):

- `aiohttp` - Async HTTP client
- Home Assistant 2025.7.0+ - Platform requirements

Development dependencies (see `requirements_dev.txt`, `requirements_test.txt`).
