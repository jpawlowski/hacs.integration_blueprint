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

[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/@jpawlowski/hacs.integration_blueprint?quickstart=1)

*Integration to integrate with [integration_blueprint][integration_blueprint].*

## ✨ Features

- **Multiple Sensors**: Track various metrics from your device
- **Switch Control**: Turn devices on and off through Home Assistant
- **Binary Sensors**: Monitor boolean states and conditions
- **Easy Setup**: Simple configuration through the UI
- **Diagnostics Support**: Built-in diagnostic tools for troubleshooting

**This integration will set up the following platforms.**

Platform | Description
-- | --
`binary_sensor` | Show something `True` or `False`.
`sensor` | Show info from Integration blueprint API.
`switch` | Switch something `On` or `Off`.

## 🚀 Quick Start

### Step 1: Install the Integration

**Prerequisites:** This integration requires [HACS](https://hacs.xyz/) (Home Assistant Community Store) to be installed.

Click the button below to open the integration directly in HACS:

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=@jpawlowski&repository=hacs.integration_blueprint&category=integration)

Then:

1. Click "Download" to install the integration
2. **Restart Home Assistant** (required after installation)

> **Note:** The My Home Assistant redirect will first take you to a landing page. Click the button there to open your Home Assistant instance.

<details>
<summary><b>Manual Installation (Advanced)</b></summary>

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

This will guide you through:

1. Enter your username
2. Enter your password
3. Configure additional options

#### Option 2: Manual Configuration

1. Go to **Settings** → **Devices & Services**
2. Click **"+ Add Integration"**
3. Search for "Integration blueprint"
4. Follow the configuration steps (same as Option 1)

### Step 3: Start Using!

The integration will now create sensors and switches based on your device. You can find all entities in **Settings** → **Devices & Services** → **Integration Blueprint** → **Entities**.

## Configuration

### Available Options

Name | Type | Default | Description
-- | -- | -- | --
`username` | `string` | **Required** | Username for authentication
`password` | `string` | **Required** | Password for authentication

## Usage

After installation, the integration will create sensors and switches based on your device.

### Sensors

- **Status Sensor**: Shows the current status of your device
- **Battery Sensor**: Displays battery level (if applicable)

### Switches

- **Main Switch**: Control your device on/off state

## Troubleshooting

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
3. Try removing and re-adding the integration

#### Device Not Responding

If your device is not responding:

1. Check your network connection
2. Verify the device is powered on
3. Check the integration diagnostics (Settings → Devices & Services → Integration blueprint → 3 dots → Download diagnostics)

## 🤝 Contributing

Contributions are welcome! Please open an issue or pull request if you have suggestions or improvements.

### 🛠️ Development Setup

Want to contribute or customize this integration? You have two options:

#### Cloud Development (Recommended)

The easiest way to get started - develop directly in your browser with GitHub Codespaces:

[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/@jpawlowski/hacs.integration_blueprint?quickstart=1)

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

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

**Made with ❤️ by [@jpawlowski][user_profile]**

---

[integration_blueprint]: https://github.com/ludeeus/integration_blueprint
[commits-shield]: https://img.shields.io/github/commit-activity/y/jpawlowski/hacs.integration_blueprint.svg?style=for-the-badge
[commits]: https://github.com/jpawlowski/hacs.integration_blueprint/commits/main
[hacs]: https://github.com/hacs/integration
[hacsbadge]: https://img.shields.io/badge/HACS-Default-orange.svg?style=for-the-badge
[license-shield]: https://img.shields.io/github/license/jpawlowski/hacs.integration_blueprint.svg?style=for-the-badge
[maintenance-shield]: https://img.shields.io/badge/maintainer-%40jpawlowski-blue.svg?style=for-the-badge
[releases-shield]: https://img.shields.io/github/release/jpawlowski/hacs.integration_blueprint.svg?style=for-the-badge
[releases]: https://github.com/jpawlowski/hacs.integration_blueprint/releases
[user_profile]: https://github.com/@jpawlowski

<!-- Optional badge definitions - uncomment if needed:
[buymecoffee]: https://www.buymeacoffee.com/jpawlowski
[buymecoffeebadge]: https://img.shields.io/badge/buy%20me%20a%20coffee-donate-yellow.svg?style=for-the-badge
[discord]: https://discord.gg/Qa5fW2R
[discord-shield]: https://img.shields.io/discord/330944238910963714.svg?style=for-the-badge
-->
