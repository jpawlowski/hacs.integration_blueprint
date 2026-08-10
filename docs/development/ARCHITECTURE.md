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

## AI Agent Context

Agent-facing content is layered so each piece is loaded only when it is relevant:

| Layer                             | Loaded                      | Contains                                          |
| --------------------------------- | --------------------------- | ------------------------------------------------- |
| `AGENTS.md`                       | always                      | project identity, workflow rules, validation loop |
| `.agents/instructions/*.md`       | per touched file            | passive style rules for one file type             |
| `.agents/skills/*/SKILL.md`       | when a task matches         | active procedures for a specific kind of work     |
| `docs/development/`, `docs/user/` | when a human or agent reads | explanations, decisions, guides — this document   |

Style rules belong in `.agents/instructions/`, procedures belong in a skill, explanations belong in `docs/`.

One copy of each instruction file serves two agents: GitHub Copilot and VS Code match its `applyTo` glob string,
Claude Code matches the identical `globs` string and reaches the same files through the
`.claude/rules/instructions` symlink. Codex has no comparable file-triggered mechanism — its nested `AGENTS.md` support keys off the working
directory rather than the file being edited — so it relies on the root `AGENTS.md` plus the pointers each skill
carries.

The skill catalogue, the symlink layout that makes one directory work for every agent vendor, and the rules for writing
a new skill are documented in [`.agents/skills/README.md`](../../.agents/skills/README.md).

For using the GitHub Copilot coding agent with this repository, see [`COPILOT_AGENT.md`](./COPILOT_AGENT.md).

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
