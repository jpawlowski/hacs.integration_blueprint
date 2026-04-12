# Configuration Reference

This document describes all configuration options and settings available in the Integration Blueprint custom integration.

## Integration Configuration

### Initial Setup Options

These options are configured during initial setup via the Home Assistant UI.

#### Connection Settings

| Option      | Type    | Required | Default | Description                                  |
| ----------- | ------- | -------- | ------- | -------------------------------------------- |
| **Host**    | string  | Yes      | -       | Hostname or IP address of the device/service |
| **Port**    | integer | No       | 8080    | Connection port                              |
| **API Key** | string  | Yes\*    | -       | Authentication key or token                  |
| **Use SSL** | boolean | No       | false   | Enable HTTPS connection                      |

\*Required if the device/service requires authentication.

#### Update Settings

| Option              | Type              | Required | Default  | Description                                         |
| ------------------- | ----------------- | -------- | -------- | --------------------------------------------------- |
| **Update Interval** | integer (seconds) | No       | 300      | How often to poll for updates (minimum: 30 seconds) |
| **Name**            | string            | No       | "Device" | Friendly name for the integration instance          |

### Options Flow (Reconfiguration)

After initial setup, you can modify settings:

1. Go to **Settings** → **Devices & Services**
2. Find "Integration Blueprint"
3. Click **Configure**
4. Modify settings
5. Click **Submit**

**Available options:**

- Update interval
- Name/identifier
- Connection timeout
- Additional features (device-specific)

## Entity Configuration

### Entity Customization

Customize entities via the UI or `configuration.yaml`:

#### Via Home Assistant UI

1. Go to **Settings** → **Devices & Services** → **Entities**
2. Find and click the entity
3. Click the settings icon
4. Modify:
   - Entity ID
   - Name
   - Icon
   - Device class (for applicable entities)
   - Area assignment

#### Via configuration.yaml

```yaml
homeassistant:
  customize:
    sensor.device_name_sensor:
      friendly_name: "Custom Sensor Name"
      icon: mdi:custom-icon
      unit_of_measurement: "units"
```

### Disabling Entities

If you don't need certain entities:

1. Go to **Settings** → **Devices & Services** → **Entities**
2. Find the entity
3. Click it, then click **Settings** icon
4. Toggle **Enable entity** off

Disabled entities won't update or consume resources.

## Services

The integration provides the following services:

### `ha_integration_domain.example_service`

Execute an example service action on the device.

**Service data:**

| Parameter   | Type           | Required | Description                                      |
| ----------- | -------------- | -------- | ------------------------------------------------ |
| `entity_id` | string or list | No       | Target entity/entities (if omitted, targets all) |
| `parameter` | string         | Yes      | Service-specific parameter                       |
| `value`     | integer        | No       | Numeric value for the action                     |

**Example:**

```yaml
service: ha_integration_domain.example_service
target:
  entity_id: switch.device_name_switch
data:
  parameter: "setting_name"
  value: 42
```

### Using Services in Automations

```yaml
automation:
  - alias: "Call service at sunset"
    trigger:
      - trigger: sun
        event: sunset
    action:
      - action: ha_integration_domain.example_service
        target:
          entity_id: switch.device_name_switch
        data:
          parameter: "mode"
          value: 1
```

## Advanced Configuration

### Multiple Instances

You can add multiple instances of this integration for different devices:

1. Go to **Settings** → **Devices & Services**
2. Click **+ Add Integration**
3. Search for "Integration Blueprint"
4. Configure with different connection details

Each instance creates separate entities with unique entity IDs.

### Network Configuration

If the device is on a different network or behind a firewall:

- Ensure ports are open (default: 8080)
- Configure port forwarding if needed
- Consider VPN for remote access
- Some devices may require static IP addresses

### Polling Behavior

The integration uses polling to fetch updates:

- **Minimum interval:** 30 seconds (prevents overloading the device)
- **Recommended interval:** 5 minutes (default)
- **Longer intervals:** Save resources but reduce responsiveness

Adjust based on your needs:

- Real-time monitoring: 30-60 seconds
- Regular updates: 5 minutes
- Slow-changing values: 15-30 minutes

## Diagnostic Data

The integration provides diagnostic data for troubleshooting:

1. Go to **Settings** → **Devices & Services**
2. Find "Integration Blueprint"
3. Click on the device
4. Click **Download Diagnostics**

Diagnostic data includes:

- Connection status
- Last update timestamp
- API response data
- Entity states
- Error history

**Privacy note:** Diagnostic data may contain sensitive information. Review before sharing.

## Blueprints

The integration works with Home Assistant Blueprints for reusable automations:

### Example Blueprint

```yaml
blueprint:
  name: Integration Blueprint Alert
  description: Send notification when sensor exceeds threshold
  domain: automation
  input:
    sensor_entity:
      name: Sensor
      selector:
        entity:
          domain: sensor
          integration: ha_integration_domain
    threshold:
      name: Threshold
      selector:
        number:
          min: 0
          max: 100

trigger:
  - trigger: numeric_state
    entity_id: !input sensor_entity
    above: !input threshold

action:
  - action: notify.notify
    data:
      message: "Sensor exceeded threshold!"
```

## Configuration Examples

See [EXAMPLES.md](./EXAMPLES.md) for complete automation and dashboard examples.

## Troubleshooting Configuration

### Config Entry Fails to Load

If the integration fails to load after configuration:

1. Check Home Assistant logs for errors
2. Verify connection details are correct
3. Test connectivity from Home Assistant to the device
4. Try removing and re-adding the integration

### Options Don't Save

If configuration changes aren't persisted:

1. Check for validation errors in the UI
2. Ensure values are within allowed ranges
3. Review logs for detailed error messages
4. Try restarting Home Assistant

## Related Documentation

- [Getting Started](./GETTING_STARTED.md) - Installation and initial setup
- [Examples](./EXAMPLES.md) - Automation and dashboard examples
- [GitHub Issues](https://github.com/jpawlowski/hacs.integration_blueprint/issues) - Report problems
