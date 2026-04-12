# Integration Blueprint

[![GitHub Release][releases-shield]][releases]
[![GitHub Activity][commits-shield]][commits]
[![License][license-shield]](LICENSE)

[![hacs][hacsbadge]][hacs]
![Project Maintenance][maintenance-shield]

<!--
Uncomment and customize these badges if you want to use them:

[![BuyMeCoffee][buymecoffeebadge]][buymecoffee]
[![Discord][discord-shield]][discord]
-->

**✨ Develop in the cloud:** Want to contribute or customize this integration? Open it directly in GitHub Codespaces - no local setup required!

[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/jpawlowski/hacs.integration_blueprint?quickstart=1)

## ✨ Features

- **Easy Setup**: Simple configuration through the UI - no YAML required
- **Air Quality Monitoring**: Track AQI and PM2.5 levels in real-time
- **Filter Management**: Monitor filter life and get replacement alerts
- **Smart Control**: Adjust fan speed, target humidity, and operating modes
- **Child Lock**: Safety feature to prevent accidental changes
- **Diagnostic Info**: View filter life, runtime hours, and device statistics
- **Reconfigurable**: Change credentials anytime without removing the integration
- **Options Flow**: Adjust settings like update interval after setup
- **Custom Services**: Advanced control with built-in service calls

**This integration will set up the following platforms.**

| Platform        | Description                                              |
| --------------- | -------------------------------------------------------- |
| `sensor`        | Air quality index (AQI), PM2.5, filter life, and runtime |
| `binary_sensor` | API connection status and filter replacement alert       |
| `switch`        | Child lock and LED display controls                      |
| `select`        | Fan speed selection (Low/Medium/High/Auto)               |
| `number`        | Target humidity setting (30-80%)                         |
| `button`        | Reset filter timer after replacement                     |
| `fan`           | Air purifier fan control with speed settings             |

> **💡 Interactive Demo**: The entities are interconnected for demonstration:
>
> - Press the **Reset Filter Timer** button → **Filter Life Remaining** sensor updates to 100%
> - Change the **Air Purifier** fan speed → **Fan Speed** select syncs automatically
> - Change the **Fan Speed** select → **Air Purifier** fan syncs automatically

## 🚀 Quick Start

### Step 1: Install the Integration

**Prerequisites:** This integration requires [HACS](https://hacs.xyz/) (Home Assistant Community Store) to be installed.

Click the button below to open the integration directly in HACS:

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=jpawlowski&repository=hacs.integration_blueprint&category=integration)

Then:

1. Click "Download" to install the integration
2. **Restart Home Assistant** (required after installation)

> **Note:** The My Home Assistant redirect will first take you to a landing page. Click the button there to open your Home Assistant instance.

<details>
<summary>**Manual Installation (Advanced)**</summary>

If you prefer not to use HACS:

1. Download the `custom_components/ha_integration_domain/` folder from this repository
2. Copy it to your Home Assistant's `custom_components/` directory
3. Restart Home Assistant

</details>

### Step 2: Add and Configure the Integration

**Important:** You must have installed the integration first (see Step 1) and restarted Home Assistant!

#### Option 1: One-Click Setup (Quick)

Click the button below to open the configuration dialog:

[![Open your Home Assistant instance and start setting up a new integration.](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start/?domain=ha_integration_domain)

Follow the setup wizard:

1. Enter your username
2. Enter your password
3. Click Submit

That's it! The integration will start loading your data.

#### Option 2: Manual Configuration

1. Go to **Settings** → **Devices & Services**
2. Click **"+ Add Integration"**
3. Search for "Integration blueprint"
4. Follow the same setup steps as Option 1

### Step 3: Adjust Settings (Optional)

After setup, you can adjust options:

1. Go to **Settings** → **Devices & Services**
2. Find **Integration Blueprint**
3. Click **Configure** to adjust:
   - Update interval (how often to refresh data)
   - Enable debug logging

You can also **Reconfigure** your credentials anytime without removing the integration.

### Step 4: Start Using!

The integration creates several entities for your air purifier:

- **Sensors**: Air quality index, PM2.5 levels, filter life remaining, total runtime
- **Binary Sensors**: API connection status, filter replacement alert
- **Switches**: Child lock, LED display control
- **Select**: Fan speed (Low/Medium/High/Auto)
- **Number**: Target humidity (30-80%)
- **Button**: Reset filter timer
- **Fan**: Air purifier fan control

Find all entities in **Settings** → **Devices & Services** → **Integration Blueprint** → click on the device.

## Available Entities

### Sensors

- **Air Quality Index (AQI)**: Real-time air quality measurement (0-500 scale)
  - Includes air quality category (Good/Moderate/Unhealthy/etc.)
  - Health recommendations based on current AQI
- **PM2.5**: Fine particulate matter concentration in µg/m³
- **Filter Life Remaining** (Diagnostic): Shows remaining filter life as percentage
- **Total Runtime** (Diagnostic): Total operating hours of the device

### Binary Sensors

- **API Connection**: Shows whether the connection to the API is active
  - On: Connected and receiving data
  - Off: Connection lost or authentication failed
  - Shows update interval and API endpoint information
- **Filter Replacement Needed**: Alerts when filter needs replacement
  - Shows estimated days remaining
  - Turns on when filter life is low

### Switches

- **Child Lock**: Prevents accidental button presses on the device
  - Icon changes based on state (locked/unlocked)
- **LED Display**: Enable/disable the LED display
  - Disabled by default - enable in entity settings if needed

### Select

- **Fan Speed**: Choose from Low, Medium, High, or Auto
  - Icon changes dynamically based on selected speed
  - Auto mode adjusts speed based on air quality
  - Syncs bidirectionally with the Air Purifier fan entity

### Number

- **Target Humidity**: Set desired humidity level (30-80%)
  - Adjustable in 5% increments
  - Displayed as a slider in the UI

### Button

- **Reset Filter Timer**: Reset the filter life to 100%
  - Press to reset after replacing the filter
  - Instantly updates the Filter Life Remaining sensor

### Fan

- **Air Purifier**: Control the air purifier fan speed and power
  - Three speed levels: Low, Medium, High
  - Syncs bidirectionally with the Fan Speed select entity
  - Turn on/off functionality

## Custom Services

The integration provides services for advanced automation:

### `ha_integration_domain.example_action`

Perform a custom action (customize this for your needs).

**Example:**

```yaml
service: ha_integration_domain.example_action
data:
  # Add your parameters here
```

### `ha_integration_domain.reload_data`

Manually refresh data from the API without waiting for the update interval.

**Example:**

```yaml
service: ha_integration_domain.reload_data
```

Use these services in automations or scripts for more control.

## Configuration Options

### During Setup

| Name     | Required | Description           |
| -------- | -------- | --------------------- |
| Username | Yes      | Your account username |
| Password | Yes      | Your account password |

### After Setup (Options)

You can change these anytime by clicking **Configure**:

| Name             | Default | Description                |
| ---------------- | ------- | -------------------------- |
| Update Interval  | 1 hour  | How often to refresh data  |
| Enable Debugging | Off     | Enable extra debug logging |

## Troubleshooting

### Authentication Issues

#### Reauthentication

If your credentials expire or change, Home Assistant will automatically prompt you to reauthenticate:

1. Go to **Settings** → **Devices & Services**
2. Look for **"Action Required"** or **"Configuration Required"** message on the integration
3. Click **"Reconfigure"** or follow the prompt
4. Enter your updated credentials
5. Click Submit

The integration will automatically resume normal operation with the new credentials.

#### Manual Credential Update

You can also update credentials at any time without waiting for an error:

1. Go to **Settings** → **Devices & Services**
2. Find **Integration Blueprint**
3. Click the **3 dots menu** → **Reconfigure**
4. Enter new username/password
5. Click Submit

#### Connection Status

Monitor your connection status with the **API Connection** binary sensor:

- **On** (Connected): Integration is receiving data normally
- **Off** (Disconnected): Connection lost or authentication failed
  - Check the binary sensor attributes for diagnostic information
  - Verify credentials if authentication failed
  - Check network connectivity

### Enable Debug Logging

To enable debug logging for this integration, add the following to your `configuration.yaml`:

```yaml
logger:
  default: info
  logs:
    custom_components.ha_integration_domain: debug
```

### Common Issues

#### Authentication Errors

If you receive authentication errors:

1. Verify your username and password are correct
2. Check that your account has the necessary permissions
3. Wait for the automatic reauthentication prompt, or manually reconfigure
4. Check the API Connection binary sensor for status

#### Device Not Responding

If your device is not responding:

1. Check the **API Connection** binary sensor - it should be "On"
2. Check your network connection
3. Verify the device is powered on
4. Check the integration diagnostics (Settings → Devices & Services → Integration blueprint → 3 dots → Download diagnostics)

## 🤝 Contributing

Contributions are welcome! Please open an issue or pull request if you have suggestions or improvements.

### 🛠️ Development Setup

Want to contribute or customize this integration? You have two options:

#### Cloud Development (Recommended)

The easiest way to get started - develop directly in your browser with GitHub Codespaces:

[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/jpawlowski/hacs.integration_blueprint?quickstart=1)

- ✅ Zero local setup required
- ✅ Pre-configured development environment
- ✅ Home Assistant included for testing
- ✅ 60 hours/month free for personal accounts

#### Local Development

Prefer working on your machine? You'll need:

- Docker Desktop
- VS Code with the [Dev Containers extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers)

Then:

1. Clone this repository
2. Open in VS Code
3. Click "Reopen in Container" when prompted

Both options give you the same fully-configured development environment with Home Assistant, Python 3.13, and all necessary tools.

---

## 🤖 AI-Assisted Development

> **ℹ️ Transparency Notice**
>
> This integration was developed with assistance from AI coding agents (GitHub Copilot, Claude, and others). While the codebase follows Home Assistant Core standards, AI-generated code may not be reviewed or tested to the same extent as manually written code.
>
> AI tools were used to:
>
> - Generate boilerplate code following Home Assistant patterns
> - Implement standard integration features (config flow, coordinator, entities)
> - Ensure code quality and type safety
> - Write documentation and comments
>
> Please be aware that AI-assisted development may result in unexpected behavior or edge cases that haven't been thoroughly tested. If you encounter any issues, please [open an issue](../../issues) on GitHub.
>
> _Note: This section can be removed or modified if AI assistance was not used in your integration's development._

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

**Made with ❤️ by [@jpawlowski][user_profile]**

---

[commits-shield]: https://img.shields.io/github/commit-activity/y/jpawlowski/hacs.integration_blueprint.svg?style=for-the-badge
[commits]: https://github.com/jpawlowski/hacs.integration_blueprint/commits/main
[hacs]: https://github.com/hacs/integration
[hacsbadge]: https://img.shields.io/badge/HACS-Default-orange.svg?style=for-the-badge
[license-shield]: https://img.shields.io/github/license/jpawlowski/hacs.integration_blueprint.svg?style=for-the-badge
[maintenance-shield]: https://img.shields.io/badge/maintainer-%40jpawlowski-blue.svg?style=for-the-badge
[releases-shield]: https://img.shields.io/github/release/jpawlowski/hacs.integration_blueprint.svg?style=for-the-badge
[releases]: https://github.com/jpawlowski/hacs.integration_blueprint/releases
[user_profile]: https://github.com/jpawlowski

<!-- Optional badge definitions - uncomment if needed:
[buymecoffee]: https://www.buymeacoffee.com/jpawlowski
[buymecoffeebadge]: https://img.shields.io/badge/buy%20me%20a%20coffee-donate-yellow.svg?style=for-the-badge
[discord]: https://discord.gg/Qa5fW2R
[discord-shield]: https://img.shields.io/discord/330944238910963714.svg?style=for-the-badge
-->
