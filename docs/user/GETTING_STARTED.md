# Getting Started with Integration Blueprint

This guide will help you install and set up the Integration Blueprint custom integration for Home Assistant.

## Prerequisites

- Home Assistant 2026.10.0 or newer
- Network connectivity to [external service/device]

## Installation

### Via the Marketplace (Home Assistant 2026.11 and newer, recommended)

1. Go to **Settings** → **Marketplace**
2. Add this repository as a custom repository: `https://github.com/jpawlowski/ha-integration-blueprint`, category "Integration". The Marketplace asks you to connect a GitHub account for repositories outside its catalog.
3. Open "Integration Blueprint" and click "Download"

A restart is not needed for the first installation; updates and removal ask for one.

### Via HACS (before Home Assistant 2026.11)

1. Open HACS in your Home Assistant instance
2. Click the three dots in the top right corner
3. Select "Custom repositories"
4. Add this repository URL: `https://github.com/jpawlowski/ha-integration-blueprint`
5. Set category to "Integration"
6. Click "Add"
7. Find "Integration Blueprint" in the list and click "Download"
8. Restart Home Assistant

### Manual Installation

1. Download the latest release from the [releases page](https://github.com/jpawlowski/ha-integration-blueprint/releases)
2. Extract the `ha_integration_domain` folder from the archive
3. Copy it to `custom_components/ha_integration_domain/` in your Home Assistant configuration directory
4. Restart Home Assistant

## Initial Setup

After installation, add the integration:

1. Go to **Settings** → **Devices & Services**
2. Click **+ Add Integration**
3. Search for "Integration Blueprint"
4. Follow the configuration steps:

### Step 1: Connection Information

Enter the required connection details:

- **Host/IP Address:** The hostname or IP address of your device/service
- **API Key/Token:** Your authentication credentials (if applicable)
- **Port:** Connection port (default: 8080)

Click **Submit** to test the connection.

### Step 2: Configuration Options

Configure optional settings:

- **Name:** Friendly name for this integration instance

Click **Submit** to complete setup.

## What Gets Created

After successful setup, the integration creates:

### Devices

- **Device Name:** Main device representing your connected service/hardware
  - Model information
  - Software version
  - Configuration URL (link to device web interface)

### Entities

The following entities are automatically created:

#### Sensors

- `sensor.<device_name>_<sensor_name>` - Descriptive sensor measurements
- More sensors as applicable to your setup

#### Binary Sensors

- `binary_sensor.<device_name>_<sensor_name>` - On/off status indicators

#### Switches

- `switch.<device_name>_<switch_name>` - Controllable on/off switches

#### Other Platforms

Additional entities may be created depending on your device capabilities.

## First Steps

### Dashboard Cards

Add entities to your dashboard:

1. Go to your dashboard
2. Click **Edit Dashboard** → **Add Card**
3. Choose card type (e.g., "Entities", "Glance")
4. Select entities from "Integration Blueprint"

Example entities card:

```yaml
type: entities
title: Integration Blueprint
entities:
  - sensor.device_name_sensor
  - binary_sensor.device_name_connectivity
  - switch.device_name_switch
```

### Automations

Use the integration in automations:

**Example - Trigger on sensor change:**

```yaml
automation:
  - alias: "React to sensor value"
    trigger:
      - trigger: state
        entity_id: sensor.device_name_sensor
    action:
      - action: notify.notify
        data:
          message: "Sensor changed to {{ trigger.to_state.state }}"
```

**Example - Control switch based on time:**

```yaml
automation:
  - alias: "Turn on in morning"
    trigger:
      - trigger: time
        at: "07:00:00"
    action:
      - action: switch.turn_on
        target:
          entity_id: switch.device_name_switch
```

## Troubleshooting

### Connection Failed

If setup fails with connection errors:

1. Verify the host/IP address is correct and reachable
2. Check that the API key/token is valid
3. Ensure no firewall is blocking the connection
4. Check Home Assistant logs for detailed error messages

### Entities Not Updating

If entities show "Unavailable" or don't update:

1. Check that the device/service is online
2. Verify API credentials haven't expired
3. Review logs: **Settings** → **System** → **Logs**
4. Try reloading the integration

### Debug Logging

Enable debug logging to troubleshoot issues:

```yaml
logger:
  default: warning
  logs:
    custom_components.ha_integration_domain: debug
```

Add this to `configuration.yaml`, restart, and reproduce the issue. Check logs for detailed information.

## Next Steps

- See [CONFIGURATION.md](./CONFIGURATION.md) for detailed configuration options
- See [EXAMPLES.md](./EXAMPLES.md) for more automation examples
- Report issues at [GitHub Issues](https://github.com/jpawlowski/ha-integration-blueprint/issues)

## Support

For help and discussion:

- [GitHub Discussions](https://github.com/jpawlowski/ha-integration-blueprint/discussions)
- [Home Assistant Community Forum](https://community.home-assistant.io/)
