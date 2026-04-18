# Home Assistant Integration Blueprint

[![Home Assistant](https://img.shields.io/badge/Home%20Assistant-2026.4%2B-blue.svg)](https://www.home-assistant.io/)
[![Python](https://img.shields.io/badge/python-3.14%2B-blue.svg)](https://www.python.org/)
[![AI Agent Ready](https://img.shields.io/badge/AI%20Agent-Ready-purple.svg)](#ai-agent-support)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

A modern blueprint for creating Home Assistant custom integrations, based on [ludeeus/integration_blueprint](https://github.com/ludeeus/integration_blueprint) but closely aligned with **Home Assistant Core development practices**.

This blueprint is designed to work with **Home Assistant 2026.4+** and includes all the patterns and tooling you need to build a professional integration without reinventing the wheel.

> [!IMPORTANT]
> **Use the template — don't fork!**
> Click the **"Use this template"** button to create your own repository.
> Forking copies the entire commit history, which you don't need and can't easily remove.
> A template repository gives you a **clean start with a single initial commit** — exactly what your integration deserves.

## 📋 Quick Navigation

- **[Getting Started](#getting-started---creating-your-integration)** - Create your integration in minutes
- **[Development Guide](#development-guide)** - Scripts, tasks, and workflow
- **[Architecture](#architecture--code-structure)** - Project structure and packages → [full details](docs/development/ARCHITECTURE.md)
- **[Integration Features](#integration-features)** - Config flow, coordinator, entities, and more
- **[Resources & Support](#resources--support)** - Documentation, tools, and community

---

## Getting Started - Creating Your Integration

Ready to create your own Home Assistant integration? **First, create your own repository from this template**, then choose one of two development options:

- **Option 1: GitHub Codespaces** ☁️ - Develop in the cloud (browser-based, zero install, recommended for beginners)
- **Option 2: Local DevContainer** 💻 - Develop on your machine (requires Docker + VS Code)

Both options use the same DevContainer setup, so your code and workflow are identical!

### Step 0: Create Your Repository First! 🎯

**Before you start developing**, create your own repository:

1. Click the **"Use this template"** button at the top of this page
2. Choose a name for your integration repository (e.g., `hass-my-awesome-device`)
3. Click **"Create repository"**
4. In your new repository, go to **Settings > Actions > General** and enable
   **"Allow GitHub Actions to create and approve pull requests"**
   (required for the Release Please workflow to open release PRs automatically)

> [!WARNING]
> **Do not use the "Fork" button.**
> Forking is meant for contributing changes back to the original project.
> It copies all ~800 commits of this blueprint's history into your repo — unnecessary baggage you cannot easily get rid of.
> The **"Use this template"** button creates a fresh repository with just one commit, which is the correct starting point for your own integration.

**🤖 Optional: Initialize with Copilot Coding Agent**

After clicking "Create repository", GitHub may offer an optional prompt field for **[Copilot Coding Agent](https://github.com/copilot/agents)**. You can use this to automatically initialize your integration (500 character limit):

```markdown
Run ./initialize.sh with: --domain <domain> --title "<Title>" --namespace "<Prefix>" --repo <owner/repo> --author "<Name>" --force

Replace:

- <domain>: lowercase_with_underscores
- <Title>: Your Integration Name
- <Prefix>: YourCamelCase (optional)
- <owner/repo>: github_user/repo_name
- <Name>: Your Name

Verify: custom_components/<domain>/ exists, manifest.json correct, README.md updated. Create PR if successful. The script deletes itself after completion.
```

**Example:** `--domain my_device --title "My Device" --repo user/hacs-my-device --author "John Doe" --force`

The agent uses `AGENTS.md` and `.github/copilot-instructions.md` for guidance and runs `./script/check` for validation.

**Manual initialization?** Continue with Option 1 or Option 2 below.

### Option 1: GitHub Codespaces (Recommended for Beginners) ☁️

Develop directly in your browser without installing anything locally!

1. In **your new repository** (created in Step 0), click the green **"Code"** button
2. Switch to the **"Codespaces"** tab
3. Click **"Create codespace on main"**
4. **Wait for setup** (2-3 minutes first time) - everything installs automatically
5. **Run `./initialize.sh`** in the terminal to configure your integration
6. **Follow the prompts** to customize:
   - **Domain**: Your integration's unique identifier (e.g., `my_awesome_device`)
   - **Title**: Display name (e.g., "My Awesome Device")
   - **Repository**: Your GitHub repo (e.g., `yourusername/your-repo`)
   - **Author**: Your name for the LICENSE

7. **Review and commit** your changes in the Source Control panel (`Ctrl+Shift+G`)

**That's it!** You're developing in a fully configured environment with Home Assistant, Python 3.14, Node.js LTS, and all tools ready. No local setup needed!

> [!TIP]
> Codespaces gives you **60 hours/month free** for personal accounts. When you start Home Assistant (`script/develop`), port 8123 forwards automatically. The setup script removes itself after initialization. See the [Codespaces Development Guide](docs/development/CODESPACES.md) for more details.

### Option 2: Local Development with VS Code

If you prefer working on your local machine (requires Docker + VS Code):

#### Prerequisites

You'll need these installed locally:

- **A Docker-compatible container engine** — see options by platform:

  | Option                                                                                                                   | 🍎 macOS | 🐧 Linux | 🪟 Windows | Notes                                                                                                                                                                                                                                     |
  | ------------------------------------------------------------------------------------------------------------------------ | :------: | :------: | :--------: | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
  | [Docker Desktop](https://www.docker.com/products/docker-desktop/)                                                        |    ✅    |    ✅    |     ✅     | **Easiest starting point for all platforms.** GUI-based, well-documented, one installer. Uses WSL2 as default backend on Windows (Hyper-V also available). Installation requires admin rights; daily use does not. Free for personal use. |
  | [OrbStack](https://orbstack.dev/) ⭐                                                                                     |    ✅    |    —     |     —      | **Recommended for macOS** once Docker Desktop feels slow. Starts in ~2s, much lighter on RAM/CPU, full Docker API compatibility. Free for personal use.                                                                                   |
  | [Docker CE](https://docs.docker.com/engine/install/) (native) ⭐                                                         |    —     |    ✅    |     —      | **Recommended for Linux.** Install directly via your package manager — no VM, no GUI, no overhead. Free.                                                                                                                                  |
  | [WSL2](https://learn.microsoft.com/windows/wsl/install) + [Docker CE](https://docs.docker.com/engine/install/ubuntu/) ⭐ |    —     |    —     |     ✅     | **Recommended for Windows** once you're comfortable with WSL2. Docker runs natively inside WSL2 — no GUI overhead. Requires one-time WSL2 setup. Free.                                                                                    |
  | [Rancher Desktop](https://rancherdesktop.io/)                                                                            |    ✅    |    ✅    |     ✅     | Open source by SUSE. GUI-based, uses WSL2 on Windows. Good alternative to Docker Desktop. Free.                                                                                                                                           |
  | [Colima](https://github.com/abiosoft/colima)                                                                             |    ✅    |    ✅    |     —      | CLI-only, very lightweight. Good for terminal-focused workflows. Free.                                                                                                                                                                    |

- **VS Code** with the [Dev Containers extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers)
- **Git** — macOS and Linux usually have it already; see below if not, or to get a newer version:
  - **🍎 macOS:** The system Git (`xcode-select --install`) works fine. Recommended: `brew install git` ([Homebrew](https://brew.sh/)) for a current version.
  - **🐧 Linux:** Usually pre-installed. If not: `sudo apt install git` (or your distro's equivalent).
  - **🪟 Windows + WSL2 ⭐:** Install Git _inside WSL2_ with `sudo apt install git`. Git on Windows itself is not needed — VS Code clones and operates entirely within WSL2.
  - **🪟 Windows + Docker Desktop:** Install via `winget install Git.Git` or download [Git for Windows](https://git-scm.com/download/win).
- **Hardware** — the devcontainer runs a full Home Assistant instance including Python tooling:

  |          | Minimum    | Recommended                           |
  | -------- | ---------- | ------------------------------------- |
  | **RAM**  | 8 GB       | 16 GB or more                         |
  | **CPU**  | 4 cores    | 8 cores or more                       |
  | **Disk** | 10 GB free | 20 GB free (SSD strongly recommended) |

> [!TIP]
> **Not sure which Docker option to pick?** Start with [Docker Desktop](https://www.docker.com/products/docker-desktop/) — it works on all platforms, has a GUI, and needs no extra setup. The ⭐ options are faster alternatives once you're comfortable. macOS and Linux offer the best devcontainer experience — containers run with no extra VM layer and file I/O is fast. Windows works well too; this blueprint uses named container volumes (files live inside WSL2, not on the Windows drive) to keep performance acceptable.

> [!NOTE]
> **Remote development via SSH (VS Code Remote SSH) is not supported.** Running the devcontainer on a remote host requires that host to be fully compatible with Docker devcontainers — for example, AppArmor must not restrict container operations, and the Docker daemon must be configured without restrictive security policies. These requirements are hard to guarantee on shared or managed servers. Use one of the options above instead.

> [!NOTE]
> **New to Dev Containers?** See the [VS Code Dev Containers documentation](https://code.visualstudio.com/docs/devcontainers/containers#_system-requirements) for system requirements and how to install the extension. **Once the extension is installed, you're done** — this blueprint already ships a complete devcontainer configuration. You don't need to follow the rest of the VS Code guide; the setup steps below are all that's needed.

#### Setup Steps

1. **Create your repository** from this template (click "Use this template" at the top)

2. **Clone in a Dev Container:**

   **🍎 macOS / 🐧 Linux:** Clone the repository and open the folder in VS Code → click **"Reopen in Container"** when prompted (or `F1` → **"Dev Containers: Reopen in Container"**).

   **🪟 Windows:** In VS Code, press `F1` → **"Dev Containers: Clone Repository in Named Container Volume..."** and enter your repository URL. This keeps files inside WSL2 for best I/O performance.

   Wait for the container to build (2-3 minutes first time).

3. **Run `./initialize.sh`** in the terminal to configure your integration

4. **Follow the prompts** to customize:
   - **Domain**: Your integration's unique identifier (e.g., `my_awesome_device`)
   - **Title**: Display name (e.g., "My Awesome Device")
   - **Repository**: Your GitHub repo (e.g., `yourusername/your-repo`)
   - **Author**: Your name for the LICENSE

5. **Review and commit** changes in Source Control (`Ctrl+Shift+G`)

6. **Start developing**:

   ```bash
   script/develop  # Home Assistant runs at http://localhost:8123
   ```

> [!NOTE]
> Both Codespaces and local DevContainer provide the exact same experience. After the container is ready, run `./initialize.sh` to customize your integration. The only difference is where the container runs (GitHub's cloud vs. your machine).

Then customize the API client in [`api/client.py`](custom_components/ha_integration_domain/api/client.py) to connect to your actual device or service.

---

## About This Blueprint

### Why use this blueprint?

Creating a custom integration from scratch means figuring out config flows, coordinators, entity platforms, error handling, and modern Python patterns. This blueprint gives you a working foundation so you can focus on your specific device or service.

**What makes this blueprint different:**

- ✅ **Core-aligned development**: Follows Home Assistant Core patterns and tooling conventions
- ✅ **Future-proof**: Compatible with Home Assistant 2026.4+ (including latest breaking changes)
- ✅ **Modern Python**: Built for Python 3.14+ with `asyncio.timeout` (no deprecated `async_timeout`)
- ✅ **Fast tooling**: Uses [uv](https://github.com/astral-sh/uv) for lightning-fast dependency management
- ✅ **Fast rebuilds**: Named Docker volumes keep the Python venv _and_ uv's package cache alive across container rebuilds — no re-downloading on every `Rebuild Container`
- ✅ **Complete test setup**: Includes `pytest-homeassistant-custom-component` for proper testing
- ✅ **Developer-friendly**: Comprehensive scripts for development, testing, and maintenance
- ✅ **Stays current**: Weekly automated PRs keep your project in sync with blueprint improvements — see [Customization Guide](docs/development/CUSTOMIZATION.md)
- ✅ **Release ready**: Automated release workflow (Release Please) + AI-assisted release notes via `script/release-notes` — see [Release Guide](docs/development/RELEASE.md)

By having a common structure, it's easier for developers to help each other and for users to understand integrations. This blueprint stays close to how Home Assistant Core itself is developed, making it easier to contribute to Core later or migrate your integration.

**Credits:** This blueprint is inspired by and builds upon [ludeeus/integration_blueprint](https://github.com/ludeeus/integration_blueprint). Thank you ludeeus for creating the original foundation!

### What's included?

This blueprint demonstrates all the essential integration features:

**Core Integration Features:**

- Config flow for user setup with validation
- Reconfiguration support to update credentials without reinstalling
- Translation keys for proper internationalization
- Diagnostics support for troubleshooting
- DataUpdateCoordinator pattern for efficient API polling
- Multiple entity types (sensor, binary sensor, switch, select, number, button, fan)
- Async API client with proper error handling and typed exceptions
- Package-based architecture for better organization and maintainability

**Development & Quality Tools:**

- Modern development tooling (Ruff for linting/formatting, Pyright for type checking)
- Pre-commit hooks for automatic code quality checks
- VS Code dev container with Python 3.14, Node.js LTS, and all extensions pre-configured
- Comprehensive development scripts (based on "Scripts to Rule Them All" pattern)
- Test infrastructure with pytest and Home Assistant test utilities
- HACS integration support out of the box

## Contributing to this Blueprint

Want to improve this blueprint itself? We welcome contributions!

1. **Fork** this repository
2. **Clone** in dev container: Use VS Code's "Dev Containers: Clone Repository in Named Container Volume..."
3. **Make your changes** to improve the blueprint structure
4. **Test** with `script/develop` to ensure everything works
5. **Submit** a pull request

For creating your own integration from this blueprint, see [Getting Started](#getting-started---creating-your-integration) above.

---

## Development Guide

Everything you need to work with the blueprint day-to-day: script reference, keeping your fork up to date, and troubleshooting. The initialization script is a one-time setup step — expand it below if you need dry-run or unattended options.

<details>
<summary><strong>Initialization Script Options</strong></summary>

The `initialize.sh` script supports both interactive and unattended modes:

**Interactive mode** (recommended for first-time users):

```bash
./initialize.sh
```

**Dry-run mode** (test without making changes):

```bash
./initialize.sh --dry-run
```

**Unattended mode** (for automation):

```bash
./initialize.sh \
  --domain my_awesome_device \
  --title "My Awesome Device" \
  --repo myusername/my-hacs-integration \
  --author "Your Name" \
  --force
```

The script will:

- ✅ Validate your domain name and check for conflicts with existing integrations
- ✅ Replace all placeholders (`ha_integration_domain`, `Integration Blueprint`, etc.)
- ✅ Rename the custom_components directory to match your domain
- ✅ Update the LICENSE with your name and current year
- ✅ Replace README.md with a customized version from README.template.md
- ✅ Delete itself and the template files after completion

</details>

### Development scripts

This repository uses the [Scripts to Rule Them All](https://github.com/github/scripts-to-rule-them-all) pattern for consistency and ease of use. All scripts use [uv](https://github.com/astral-sh/uv) for faster dependency management.

#### Setup & Maintenance

- **`script/setup/bootstrap`** - First-time setup after cloning (installs dependencies and pre-commit hooks)
- **`script/setup/setup`** - Complete project setup (runs bootstrap + additional configuration)
- **`script/setup/reset`** - Reset development environment to fresh state
- **`script/setup/sync-hacs`** - Sync HACS-installed integrations to `custom_components/` for development

#### Development

- **`script/develop`** - Start Home Assistant in development mode with your integration loaded
- **`script/test`** - Run project tests with pytest
  - Add `--cov` for coverage report, `--cov-html` for HTML report in `htmlcov/`
  - Pass any pytest options: `script/test -v -k test_name`
- **`script/lint`** - Run Ruff linting and auto-format code
- **`script/lint-check`** - Check linting without making changes (for CI)
- **`script/type-check`** - Run Pyright type checking
- **`script/spell`** - Run spell checking and fix spelling issues
- **`script/spell-check`** - Check spelling without making changes (for CI)
- **`script/check`** - Run type checking, linting, and spell checking (useful before commits)
- **`script/clean`** - Clean up development artifacts and caches
- **`script/help`** - Display all available scripts with descriptions

#### VS Code tasks

The project includes pre-configured VS Code tasks for common operations. Press `Ctrl+Shift+B` (or `Cmd+Shift+B` on macOS) to see available tasks like "Run Home Assistant (Development Mode)", "Run Tests", "Lint", etc.

### Staying up to date

Once your integration is live, a weekly pull request will offer you any improvements made to the upstream blueprint. Review the PR and merge what's useful — anything you want to keep as-is can simply be excluded.

You can also extend any `script/` or `.devcontainer/` script without touching the original files by placing **hook scripts** in `script/hooks/` or `.devcontainer/hooks/`. These directories are never overwritten by template sync.

See [docs/development/CUSTOMIZATION.md](docs/development/CUSTOMIZATION.md) for details on both topics.

### Migrating an existing integration

Already have a HACS integration? You can adopt this blueprint's structure and tooling without starting from scratch. The short version: copy your `custom_components/<domain>/` folder in and adapt your code incrementally.

See [docs/development/MIGRATION.md](docs/development/MIGRATION.md) for an overview of strategies (clean start vs. preserving git history) and common pitfalls like namespace mismatches and repository permissions.

### Troubleshooting

Expand a section below for solutions to common devcontainer issues.

<details>
<summary><strong>Many "Problems" showing after first devcontainer build?</strong></summary>

When you first build and attach to the devcontainer, VS Code's Python extensions (especially Pylance) need time to fully index the workspace. You may see many false "Problems" in the Problems panel that don't actually exist.

**Solution:** Reload the VS Code window

1. Press `F1` (or `Ctrl+Shift+P` / `Cmd+Shift+P`)
2. Type: `Developer: Reload Window`
3. Press Enter

After the reload, the linters and language servers will be fully initialized and the false problems will disappear.

> [!NOTE]
> **Why does this happen?** When the devcontainer is first built, the `postCreateCommand` installs all dependencies and sets up the Python environment, but the VS Code extensions haven't finished indexing yet when you first attach. A window reload ensures all extensions are properly initialized with the completed environment.
>
> **Alternative:** Close VS Code completely and re-open the devcontainer. This has the same effect but takes longer.
>
> **This is normal!** This is a known limitation of how VS Code initializes extensions in devcontainers. It only happens on the first attach after building — subsequent sessions work perfectly.

</details>

<details>
<summary><strong>Docker disk usage keeps growing — how to reclaim space</strong></summary>

When working on multiple devcontainer projects, Docker's disk footprint grows steadily: build cache accumulates with every rebuild, old image layers stack up, and volumes are left behind after containers are removed. Run this first to understand what's consuming space:

```bash
docker system df        # summary: images, containers, volumes, build cache
docker system df -v     # detailed breakdown per image and volume
```

**Reclaim space — from safest to most aggressive:**

```bash
docker builder prune              # build cache only — often the largest contributor, safe to remove
docker system prune               # stopped containers + dangling images + unused networks + build cache
docker system prune -a            # same + all unused images (not just dangling ones)
docker volume prune               # unused volumes — see warning below
docker system prune -a --volumes  # everything — use when starting completely fresh
```

> [!CAUTION]
> **`docker volume prune` deletes devcontainer volumes**, including the project files and the Python virtual environment inside the container. Only use it when you intend a clean rebuild. Re-opening the devcontainer in VS Code will recreate everything automatically.

**Limit build cache size proactively:**

```bash
docker builder prune --keep-storage 5gb   # trim build cache to at most 5 GB
```

Run this periodically (e.g. as a weekly cron job) to keep disk usage bounded without losing everything.

**macOS with Docker Desktop: the VM disk image problem**

Docker Desktop on macOS runs inside a VM whose disk image (`Docker.raw`) grows as data is added — but _never automatically shrinks_ when data is deleted. Even after a thorough `docker system prune`, the host disk does not get space back.

To reclaim host disk space:

1. Open **Docker Desktop → Settings → Resources**
2. Click **"Clean / Purge data"** — this rebuilds the VM image from scratch and returns all freed space to macOS
3. Alternatively, lower the **"Disk image size"** slider — Docker Desktop will trim the image on next restart

> [!TIP]
> **OrbStack users don't have this problem.** OrbStack uses macOS APFS sparse files instead of a fixed VM image, so freed space is returned to the host automatically — no manual purge step needed.

**RAM usage with multiple devcontainers open**

Each open devcontainer runs VS Code Remote Server + Pylance + a full Home Assistant instance. That adds up to roughly 2–4 GB per container. If you develop multiple projects in parallel, RAM fills up quickly — not because of the AI tooling itself, but because of the language servers and the HA Python process.

Practical approaches: keep only one devcontainer active at a time, or use VS Code's **"Dev Containers: Stop Container"** command to suspend containers you're not actively using.

</details>

#### Other common issues

For Codespaces-specific troubleshooting, see [docs/development/CODESPACES.md](docs/development/CODESPACES.md#troubleshooting).

---

## Architecture & Code Structure

This section documents the project layout and the reasoning behind the package-based structure. Expand the file tree below for a full reference, or read the package architecture overview for the design rationale.

<details>
<summary><strong>Project structure</strong></summary>

```text
custom_components/ha_integration_domain/  # Your integration code
├── __init__.py                # Integration setup and entry point
├── config_flow.py             # Config flow entry point (delegates to handler)
├── const.py                   # Constants and configuration
├── data.py                    # Data models and type definitions
├── diagnostics.py             # Diagnostics data for troubleshooting
├── manifest.json              # Integration metadata
├── repairs.py                 # Repair flows for fixing issues
├── services.yaml              # Service action definitions (legacy filename)
│
├── api/                       # API client package
│   ├── __init__.py
│   └── client.py              # API client implementation
│
├── coordinator/               # DataUpdateCoordinator package
│   ├── __init__.py            # Main coordinator export
│   ├── base.py                # Core coordinator implementation
│   ├── data_processing.py     # Data transformation
│   ├── error_handling.py      # Error recovery
│   └── listeners.py           # Entity callbacks
│
├── entity/                    # Base entity package
│   ├── __init__.py            # Base entity export
│   └── base.py                # IntegrationBlueprintEntity class
│
├── config_flow_handler/       # Config flow package
│   ├── __init__.py
│   ├── handler.py             # Base handler logic
│   ├── config_flow.py         # User setup flow
│   ├── options_flow.py        # Options flow (reconfigure)
│   ├── subentry_flow.py       # Subentry flow (for multi-device setups)
│   ├── schemas/               # Voluptuous schemas
│   │   ├── __init__.py
│   │   ├── config.py          # Config flow schemas
│   │   └── options.py         # Options flow schemas
│   └── validators/            # Input validators
│       ├── __init__.py
│       ├── credentials.py     # Credential validation
│       └── sanitizers.py      # Input sanitizers
│
├── entity_utils/              # Entity utilities package
│   ├── __init__.py
│   ├── device_info.py         # Device info helpers
│   └── state_helpers.py       # State calculation helpers
│
├── service_actions/           # Service action handlers package
│   ├── __init__.py            # Service action registration and handlers
│   └── example_service.py     # Example: Service action implementation
│
├── utils/                     # General utilities package
│   ├── __init__.py            # Utility functions
│   ├── string_helpers.py      # String formatting utilities
│   └── validators.py          # General validation utilities
│
├── sensor/                    # Sensor platform package
│   ├── __init__.py            # Platform setup
│   ├── air_quality.py         # Example: Air quality sensor
│   ├── diagnostic.py          # Example: Diagnostic sensor
│   └── ...                    # Additional sensor entities
│
├── binary_sensor/             # Binary sensor platform package
│   ├── __init__.py            # Platform setup
│   ├── connectivity.py        # Example: Connectivity sensor
│   ├── filter.py              # Example: Filter status sensor
│   └── ...                    # Additional binary sensor entities
│
├── switch/                    # Switch platform package
│   ├── __init__.py            # Platform setup
│   ├── example_switch.py      # Example: Switch entity
│   └── ...                    # Additional switch entities
│
├── select/                    # Select platform package
│   ├── __init__.py            # Platform setup
│   ├── fan_speed.py           # Example: Fan speed selector
│   └── ...                    # Additional select entities
│
├── number/                    # Number platform package
│   ├── __init__.py            # Platform setup
│   ├── target_humidity.py     # Example: Target humidity setter
│   └── ...                    # Additional number entities
│
├── button/                    # Button platform package
│   ├── __init__.py            # Platform setup
│   ├── reset_filter.py        # Example: Filter reset button
│   └── ...                    # Additional button entities
│
├── fan/                       # Fan platform package
│   ├── __init__.py            # Platform setup
│   ├── air_purifier_fan.py    # Example: Air purifier fan control
│   └── ...                    # Additional fan entities
│
└── translations/              # User-facing text in multiple languages
    ├── en.json                # English translations
    └── ...                    # Additional languages

config/                        # Home Assistant configuration for development
script/                        # Development scripts
├── hooks/                     # Your custom pre/post hook scripts (see docs/development/CUSTOMIZATION.md)
│   └── setup/                 # Hooks for script/setup/* scripts
└── setup/                     # Setup & maintenance scripts
tests/                         # Your test files (add your own!)
.devcontainer/                 # VS Code dev container configuration
├── hooks/                     # Your custom pre/post hook scripts (see docs/development/CUSTOMIZATION.md)
└── post-attach.sh             # Auto-initialization trigger  ⚑ removed by initialize.sh
docs/                          # Documentation
├── development/               # Developer documentation
│   ├── ARCHITECTURE.md        # Architecture overview
│   ├── CODESPACES.md          # Codespaces setup guide
│   ├── COPILOT_AGENT.md       # GitHub Copilot agent setup
│   ├── CUSTOMIZATION.md       # Customization guide
│   ├── DECISIONS.md           # Architectural decisions
│   ├── MIGRATION.md           # Migration guide  ⚑ removed by initialize.sh
│   └── RELEASE.md             # Release process
└── user/                      # User documentation
    ├── CONFIGURATION.md       # Configuration guide
    ├── EXAMPLES.md            # Usage examples
    └── GETTING_STARTED.md     # Installation guide
pyproject.toml                 # Python project configuration (Ruff, Pyright, pytest)
requirements*.txt              # Python dependencies
README.md                      # This file (blueprint documentation)  ⚑ replaced by initialize.sh
README.template.md             # Template for your integration's README  ⚑ removed by initialize.sh
initialize.sh                  # One-time setup script  ⚑ removes itself after completion
```

**Note for new integrations:** When you run `./initialize.sh`, it will automatically replace this `README.md` with the content from `README.template.md`, customized with your integration's details.

</details>

### Package-based architecture

This blueprint uses a **package-based structure** where each major component is organized into its own package (directory with `__init__.py`):

**Benefits:**

- ✅ **Better organization** - Related code is grouped together
- ✅ **Easier to maintain** - Each package has a clear responsibility
- ✅ **Scalable** - Easy to add new entities or features without creating monolithic files
- ✅ **Clear boundaries** - Each platform, utility, and handler has its own namespace

**Platform packages:**

Each platform (sensor, binary_sensor, switch, etc.) is a package containing:

- `__init__.py` - Platform setup with `async_setup_entry()` function
- Individual entity files - One file per entity type (e.g., `air_quality.py`, `connectivity.py`)

**Other packages:**

- **`api/`** - API client and exceptions
- **`config_flow_handler/`** - All config flow logic, schemas, and validators
- **`entity_utils/`** - Shared entity helpers (device info, state calculations)
- **`service_actions/`** - Service action registration and handlers (e.g., `example_service.py`)
- **`utils/`** - General utility functions (string helpers, validators, etc.)

See [docs/development/ARCHITECTURE.md](docs/development/ARCHITECTURE.md) for a detailed architecture overview and architectural decision records.

---

## Integration Features

This section explains the key features and patterns used in this integration blueprint.

### Config flow

The config flow is organized in the [`config_flow_handler/`](custom_components/ha_integration_domain/config_flow_handler/) package. Users can:

- Add the integration through Settings → Devices & Services
- Enter credentials (or other configuration)
- The config flow validates input before creating a config entry
- Reconfigure credentials later without removing and re-adding

**Package structure:**

- [`handler.py`](custom_components/ha_integration_domain/config_flow_handler/handler.py) - Base handler with shared logic
- [`config_flow.py`](custom_components/ha_integration_domain/config_flow_handler/config_flow.py) - User setup flow
- [`options_flow.py`](custom_components/ha_integration_domain/config_flow_handler/options_flow.py) - Options flow for reconfiguration
- [`subentry_flow.py`](custom_components/ha_integration_domain/config_flow_handler/subentry_flow.py) - Subentry flow for multi-device setups
- [`schemas/`](custom_components/ha_integration_domain/config_flow_handler/schemas/) - Voluptuous schemas for input validation
- [`validators/`](custom_components/ha_integration_domain/config_flow_handler/validators/) - Custom validators

**Key features:**

- Input validation with custom error messages
- Unique ID to prevent duplicate entries
- Reconfiguration support via options flow
- Proper error handling with user-friendly messages

### DataUpdateCoordinator

The [`coordinator/`](custom_components/ha_integration_domain/coordinator/) package efficiently manages data fetching:

- **Single API call**: Instead of each entity polling separately, the coordinator fetches data once
- **Shared data**: All entities receive the same data, reducing API load
- **Error handling**: Handles authentication failures and communication errors consistently
- **Automatic updates**: Polls at regular intervals (configurable in `__init__.py`)

This is the recommended pattern in Home Assistant Core for any integration that polls an API.

### Translation keys

All user-facing strings use translation keys instead of hardcoded English text. See [`translations/en.json`](custom_components/ha_integration_domain/translations/en.json).

**Benefits:**

- Easy to add more languages
- Consistent terminology across integrations
- Users see text in their configured language

The config flow, entity states, and error messages all support translations.

### Diagnostics

The [`diagnostics.py`](custom_components/ha_integration_domain/diagnostics.py) file provides debug information that users can download from the UI:

- Device information
- Configuration details (with sensitive data redacted)
- Coordinator data for troubleshooting
- Integration version and metadata

Users can share this file when reporting issues without exposing passwords or tokens.

<details>
<summary><strong>Entity platforms</strong></summary>

The blueprint includes multiple entity types organized as packages to demonstrate different patterns:

**Sensors** ([`sensor/`](custom_components/ha_integration_domain/sensor/))

- Shows how to create sensors with state values
- Demonstrates state classes and device classes
- Examples:
  - [`air_quality.py`](custom_components/ha_integration_domain/sensor/air_quality.py) - Air quality index sensor
  - [`diagnostic.py`](custom_components/ha_integration_domain/sensor/diagnostic.py) - Diagnostic sensor

**Binary Sensors** ([`binary_sensor/`](custom_components/ha_integration_domain/binary_sensor/))

- Shows binary (on/off) sensors
- Uses device classes for proper icons
- Examples:
  - [`connectivity.py`](custom_components/ha_integration_domain/binary_sensor/connectivity.py) - Connectivity status
  - [`filter.py`](custom_components/ha_integration_domain/binary_sensor/filter.py) - Filter replacement indicator

**Switches** ([`switch/`](custom_components/ha_integration_domain/switch/))

- Shows controllable entities that interact with the API
- Implements `turn_on` and `turn_off` methods
- Demonstrates error handling for control commands
- Example: [`example_switch.py`](custom_components/ha_integration_domain/switch/example_switch.py) - Example switch entity

**Select Entities** ([`select/`](custom_components/ha_integration_domain/select/))

- Shows dropdown selection entities
- Example: [`fan_speed.py`](custom_components/ha_integration_domain/select/fan_speed.py) - Fan speed selector

**Number Entities** ([`number/`](custom_components/ha_integration_domain/number/))

- Shows numeric input entities
- Example: [`target_humidity.py`](custom_components/ha_integration_domain/number/target_humidity.py) - Target humidity setter

**Button Entities** ([`button/`](custom_components/ha_integration_domain/button/))

- Shows action button entities
- Example: [`reset_filter.py`](custom_components/ha_integration_domain/button/reset_filter.py) - Filter reset button

**Fan Entities** ([`fan/`](custom_components/ha_integration_domain/fan/))

- Shows fan control entities
- Example: [`air_purifier_fan.py`](custom_components/ha_integration_domain/fan/air_purifier_fan.py) - Air purifier fan control

Each platform package shows best practices for entity setup, naming, and data handling.

</details>

### API client

The API client is organized in the [`api/`](custom_components/ha_integration_domain/api/) package:

**Modern patterns:**

- Uses `asyncio.timeout` instead of deprecated `async_timeout` (required for HA 2026.4+)
- Proper async/await throughout
- Custom exception classes for different error types
- Type hints for better IDE support

**Error handling:**

- `IntegrationBlueprintApiClientError` - Base exception for all API errors
- `IntegrationBlueprintApiClientAuthenticationError` - Invalid credentials (401/403)
- `IntegrationBlueprintApiClientCommunicationError` - Network or connection errors

Replace the dummy API calls in [`api/client.py`](custom_components/ha_integration_domain/api/client.py) with your actual device/service API.

<details>
<summary><strong>Development container</strong></summary>

The [`.devcontainer/devcontainer.json`](.devcontainer/devcontainer.json) configures a complete development environment:

**What's included:**

- Python 3.14 (matching Home Assistant Core requirements)
- Node.js LTS (for frontend development if needed)
- GitHub CLI pre-installed
- All VS Code extensions configured (Python, Ruff, YAML, etc.)
- Home Assistant 2026.4+ automatically installed
- HACS pre-installed and configured
- Automatic port forwarding for Home Assistant (port 8123)

**First startup:**

The container runs `script/setup/setup` automatically, which:

1. Creates a Python virtual environment
2. Installs all dependencies
3. Downloads Home Assistant
4. Sets up HACS
5. Installs pre-commit hooks

Just wait for the setup to complete (check the terminal), then run `script/develop`.

> [!NOTE]
> **Codespaces users:** See [docs/development/CODESPACES.md](docs/development/CODESPACES.md) for tips on developing in GitHub Codespaces.

</details>

<a id="ai-agent-support"></a>

<details>
<summary><strong>AI agent support</strong></summary>

This blueprint is optimized for development with AI coding assistants like **GitHub Copilot**, **Claude**, and other AI agents.

**Quick start for AI assistants:**

- **`AGENTS.md`** - Primary instruction file with project overview, workflow, and validation guidelines
- **`.github/instructions/*.instructions.md`** - 16 path-specific instruction files for different file types (Python, YAML, JSON, config flows, entities, repairs, etc.)
- **`.github/copilot-instructions.md`** - GitHub Copilot-specific workflow guidance
- **`docs/development/COPILOT_AGENT.md`** - Guide for using GitHub Copilot Coding Agent with this template

**Benefits:**

- ✅ **Consistent code quality** - AI generates code that passes validation on first run
- ✅ **Home Assistant patterns** - Follows Core development standards automatically
- ✅ **Context-aware** - File-specific instructions ensure appropriate patterns
- ✅ **Faster development** - Less iteration, more productive sessions
- ✅ **Autonomous initialization** - Copilot Coding Agent can initialize projects from template

**Using Copilot Coding Agent:**

When creating a new repository from this template, you can provide initialization instructions to **GitHub Copilot Coding Agent** ([github.com/copilot/agents](https://github.com/copilot/agents)):

1. Click "Use this template" on GitHub
2. In the optional prompt field, provide your integration details (domain, title, repository)
3. The agent will run `initialize.sh` in unattended mode and create a pull request

See [`docs/development/COPILOT_AGENT.md`](docs/development/COPILOT_AGENT.md) for detailed instructions and example prompts.

**For complete details:**

See [`docs/development/ARCHITECTURE.md`](docs/development/ARCHITECTURE.md#ai-agent-instructions) for the full list of instruction files, their purpose, and application patterns.

**Maintaining instructions:**

As your integration evolves, keep these instruction files updated. They should reflect your actual patterns and decisions, not just theoretical guidelines. When you establish new conventions or change approaches, update the relevant instruction files so AI agents stay aligned with your project's direction.

</details>

<details>
<summary><strong>Pre-commit hooks</strong></summary>

The repository uses [pre-commit](https://pre-commit.com/) to automatically check code before commits:

**What's checked:**

- Ruff formatting (auto-fixes)
- Ruff linting (auto-fixes when possible)
- YAML syntax
- JSON syntax
- Trailing whitespace
- File endings

Hooks are installed automatically by `script/setup/bootstrap`. Run manually with:

```bash
pre-commit run --all-files
```

</details>

<details>
<summary><strong>Testing infrastructure</strong></summary>

The blueprint includes a complete test setup:

**Tools provided:**

- `pytest` for running tests
- `pytest-homeassistant-custom-component` for Home Assistant-specific fixtures
- `pytest-asyncio` for async test support
- `pytest-cov` for coverage reporting

**Add your own tests:**
Create test files in the `tests/` directory. Example:

```python
"""Test integration setup."""
from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import MockConfigEntry

async def test_setup_entry(hass: HomeAssistant) -> None:
    """Test setting up the integration."""
    entry = MockConfigEntry(domain="ha_integration_domain", data={...})
    assert await hass.config_entries.async_setup(entry.entry_id)
```

Run tests with `script/test` or `script/test --cov` for coverage.

</details>

<details>
<summary><strong>Type checking and linting</strong></summary>

This blueprint uses the same tools as Home Assistant Core:

**Ruff** (replaces Black, isort, flake8, and more)

- Fast linter and formatter written in Rust
- Automatically fixes many issues
- Configuration in `pyproject.toml` matches Core standards
- Run with `script/lint`

**Pyright** (type checker)

- Checks type hints for errors
- Helps catch bugs before runtime
- Configuration in `pyproject.toml`
- Run with `script/type-check`

Both tools are integrated into pre-commit hooks and the dev container.

</details>

---

## Comparison & Next Steps

### Differences from ludeeus/integration_blueprint

While this blueprint is inspired by the original, it includes significant enhancements:

| Feature                     | This Blueprint                                                                           | Original Blueprint             |
| --------------------------- | ---------------------------------------------------------------------------------------- | ------------------------------ |
| **Home Assistant version**  | 2026.4+ (Python 3.14 native)                                                             | 2026.3.x                       |
| **Timeout handling**        | `asyncio.timeout` (modern)                                                               | `async_timeout` (deprecated)   |
| **Package manager**         | uv (fast)                                                                                | pip (standard)                 |
| **Container rebuild speed** | Named Docker volumes keep venv + uv cache alive across rebuilds — near-instant re-attach | Fresh install on every rebuild |
| **Development scripts**     | Comprehensive Scripts to Rule Them All                                                   | Basic scripts                  |
| **Test infrastructure**     | Preconfigured `pytest-homeassistant-custom-component`                                    | Manual test setup needed       |
| **Type checking**           | Pyright configured                                                                       | Not included                   |
| **HACS integration**        | Auto-installed in dev container                                                          | Manual setup                   |
| **VS Code tasks**           | Pre-configured tasks for common operations                                               | Not included                   |
| **Package architecture**    | Organized into packages for scalability                                                  | Single-file platforms          |
| **AI agent support**        | Comprehensive instructions for GitHub Copilot, Claude, etc.                              | Not included                   |
| **Blueprint updates**       | Weekly PRs keep your project in sync with upstream                                       | No update mechanism            |
| **Release workflow**        | Release Please + AI-assisted `script/release-notes`                                      | Not included                   |

Both blueprints share the same core concepts (config flow, coordinator, entity platforms), but this one is more closely aligned with how Home Assistant Core is developed today.

### Next steps

Once you have the blueprint working with your device or service:

#### Testing & quality

- **Add tests**: Use `pytest-homeassistant-custom-component` to test your config flow, coordinator, and entities
- **Run type checking**: Ensure `script/type-check` passes without errors
- **Test with real Home Assistant**: Install via HACS or copy to your real HA instance

#### Branding & distribution

- **Add brand images**: Place logo (`logo.png`) and icon (`icon.png`) in the `brand/` directory — Home Assistant picks them up automatically for custom integrations (see [docs](https://developers.home-assistant.io/docs/creating_integration_file_structure/#brand-images---brand))
- **Write documentation**: Update this README with your integration's specific features
- **Create releases**: Use the included Release Please workflow and `script/release-notes` for AI-assisted changelogs — see [docs/development/RELEASE.md](docs/development/RELEASE.md)

#### Share & Connect

- **Share your work**: Post on the [Home Assistant Forum](https://community.home-assistant.io/)
- **Submit to HACS**: Follow the [HACS documentation](https://hacs.xyz/docs/publish/start) to make your integration discoverable
- **Contribute**: If your integration would benefit many users, consider [submitting it to Home Assistant Core](https://developers.home-assistant.io/docs/creating_integration_manifest)

---

## Resources & Support

### This blueprint's documentation

- [docs/development/ARCHITECTURE.md](docs/development/ARCHITECTURE.md) - Architecture overview and decision records
- [docs/development/CUSTOMIZATION.md](docs/development/CUSTOMIZATION.md) - Extending scripts and staying up to date
- [docs/development/RELEASE.md](docs/development/RELEASE.md) - Release process and versioning
- [docs/development/CODESPACES.md](docs/development/CODESPACES.md) - GitHub Codespaces setup and tips
- [docs/development/COPILOT_AGENT.md](docs/development/COPILOT_AGENT.md) - Using GitHub Copilot Coding Agent
- [docs/development/MIGRATION.md](docs/development/MIGRATION.md) - Migrating an existing integration

### Home Assistant documentation

- [Developer documentation](https://developers.home-assistant.io/) - Official developer guide
- [Creating a custom integration](https://developers.home-assistant.io/docs/creating_component_index) - Step-by-step tutorial
- [Config flow documentation](https://developers.home-assistant.io/docs/config_entries_config_flow_handler) - Setting up user configuration
- [DataUpdateCoordinator](https://developers.home-assistant.io/docs/integration_fetching_data) - Efficient data fetching pattern
- [Entity documentation](https://developers.home-assistant.io/docs/core/entity) - Creating entities

### Development tools

- [uv package manager](https://github.com/astral-sh/uv) - Fast Python package installer
- [Ruff](https://github.com/astral-sh/ruff) - Fast Python linter and formatter
- [Pyright](https://github.com/microsoft/pyright) - Static type checker for Python
- [pytest-homeassistant-custom-component](https://github.com/MatthewFlamm/pytest-homeassistant-custom-component) - Test fixtures for custom components

### Community resources

- [Home Assistant Discord](https://discord.gg/home-assistant) - Chat with developers
- [Home Assistant Forum](https://community.home-assistant.io/) - Discussion and support
- [Original blueprint by ludeeus](https://github.com/ludeeus/integration_blueprint) - Where it all started

---

## Contributing

Contributions are welcome! If you find a bug or have a feature suggestion:

1. Check existing [issues](../../issues) first
2. Open a new issue to discuss major changes
3. Submit a pull request with your improvements

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.

## License

MIT License - see [LICENSE](LICENSE) file for details.

---

## Built with AI

This blueprint was developed with significant assistance from AI coding assistants (GitHub Copilot, Claude). We believe in transparency about AI usage in open-source projects. The comprehensive AI agent instructions included in this repository ([`AGENTS.md`](AGENTS.md), `.github/instructions/`) reflect our experience and best practices for AI-assisted development.

If you're using AI assistants for your integration, these instructions will help ensure consistent, high-quality code generation that follows Home Assistant Core patterns.

---

**Happy coding! 🎉** If you build something cool with this blueprint, let us know!
