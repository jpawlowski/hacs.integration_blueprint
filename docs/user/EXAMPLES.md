# Examples

This page provides ready-to-use examples for automations, dashboards, and blueprints
with the Integration Blueprint custom integration.

Replace entity IDs like `sensor.device_name_*` with your actual entity IDs after
setting up the integration.

## Automations

### Notify when a sensor exceeds a threshold

```yaml
automation:
  - alias: "Alert when sensor is high"
    trigger:
      - trigger: numeric_state
        entity_id: sensor.device_name_air_quality
        above: 100
    action:
      - action: notify.notify
        data:
          title: "Air quality alert"
          message: "Sensor value exceeded 100!"
```

### Turn on a switch when connectivity is lost

```yaml
automation:
  - alias: "React to connectivity loss"
    trigger:
      - trigger: state
        entity_id: binary_sensor.device_name_connectivity
        to: "off"
        for:
          minutes: 5
    action:
      - action: switch.turn_off
        target:
          entity_id: switch.device_name_switch
```

### Call a service action on schedule

```yaml
automation:
  - alias: "Reset filter counter weekly"
    trigger:
      - trigger: time
        at: "03:00:00"
    condition:
      - condition: time
        weekday:
          - mon
    action:
      - action: ha_integration_domain.example_service
        target:
          entity_id: button.device_name_reset_filter
```

### Use a blueprint for threshold alerts

Save this as a blueprint file and import it in Home Assistant:

```yaml
blueprint:
  name: Integration Blueprint — Threshold Alert
  description: Send a notification when a sensor exceeds a configurable threshold.
  domain: automation
  input:
    sensor_entity:
      name: Sensor
      selector:
        entity:
          domain: sensor
          integration: ha_integration_domain
    threshold:
      name: Threshold value
      selector:
        number:
          min: 0
          max: 1000
    notify_target:
      name: Notification service
      default: notify.notify
      selector:
        text:

trigger:
  - trigger: numeric_state
    entity_id: !input sensor_entity
    above: !input threshold

action:
  - action: !input notify_target
    data:
      message: >-
        {{ state_attr(trigger.entity_id, 'friendly_name') }}
        exceeded {{ threshold }} (current value: {{ trigger.to_state.state }}).
```

## Dashboard Cards

### Sensor value card

```yaml
type: sensor
entity: sensor.device_name_air_quality
name: Air Quality
graph: line
```

### Device summary — entities card

```yaml
type: entities
title: My Device
entities:
  - entity: sensor.device_name_air_quality
    name: Air Quality
  - entity: binary_sensor.device_name_connectivity
    name: Connected
  - entity: binary_sensor.device_name_filter
    name: Filter Status
  - entity: switch.device_name_switch
    name: Power
  - entity: select.device_name_fan_speed
    name: Fan Speed
  - entity: number.device_name_threshold
    name: Threshold
```

### Status badge — multiple entities

```yaml
type: glance
title: Device Status
entities:
  - entity: binary_sensor.device_name_connectivity
    name: Online
  - entity: sensor.device_name_air_quality
    name: Air Quality
  - entity: binary_sensor.device_name_filter
    name: Filter
show_state: true
```

### History graph

```yaml
type: history-graph
title: Air Quality (last 24 h)
entities:
  - entity: sensor.device_name_air_quality
hours_to_show: 24
```

## Related Documentation

- [Configuration Reference](./CONFIGURATION.md) - All configuration options
- [Getting Started](./GETTING_STARTED.md) - Installation and initial setup
- [GitHub Issues](https://github.com/jpawlowski/hacs.integration_blueprint/issues) - Report problems
