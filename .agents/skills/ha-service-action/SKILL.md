---
name: ha-service-action
description: >-
  Add, change, or remove a Home Assistant service action (also called a "service" or "action") in this custom
  integration. Use when asked to "add a service", "add an action", "expose X as a service call", "add a service
  that returns data", "make this callable from an automation", or when editing services.yaml, the service_actions/
  package, service schemas, service response data, or the async_setup() registration. Covers the services.yaml
  contract, voluptuous schemas, selectors, entity/device targeting, response data, translated error messages, and
  the Bronze quality-scale rule that actions must be registered in async_setup(). SYMPTOMS — load this if you are
  about to: register an action in `async_setup_entry()`; add a `services.yaml` field without a selector; add an
  `entity_id` field where `target:` belongs; raise a plain English `HomeAssistantError`; or swallow an action
  failure into a log line.
---

# Add or change a service action

Terminology: Home Assistant renamed "services" to **actions** in the UI, but the Python API, the file name
`services.yaml`, and the translation keys all still say `service`. Use "action" when talking to users, `service` in
code.

**Read [`blueprint.service_actions.instructions.md`](../../instructions/blueprint.service_actions.instructions.md)
and [`blueprint.services_yaml.instructions.md`](../../instructions/blueprint.services_yaml.instructions.md)
first** — they hold the rules: where registration must happen, the voluptuous schema pattern, which exception type to
raise, the `target:` field, response-data requirements (including the `.isoformat()` trap), entity service actions, and
the `icons.json` shape. This skill is the order of operations and the design decisions.

## Decide the shape first

Target the thing the action actually acts on — there are three levels, and picking the wrong one is what makes an
action awkward to call:

| Question                                            | Consequence                                                                      |
| --------------------------------------------------- | -------------------------------------------------------------------------------- |
| Does it act on one entity?                          | Add a `target:` with an `entity:` selector — do not invent an `entity_id` field. |
| Does it act on one device?                          | A required `device_id` field with a `device:` selector.                          |
| Does it act on the whole account/hub?               | A required `config_entry_id` field with a `config_entry:` selector.              |
| Does the caller need data back?                     | `SupportsResponse.ONLY` or `.OPTIONAL` and return a `ServiceResponse` dict.      |
| Could an entity attribute or a button entity do it? | Prefer the entity. Actions are for things that do not map onto entity state.     |

**A target is never optional and never defaulted.** Picking "the only entry" when the caller named none makes every
automation break the day a second entry is added. The one exception is `single_config_entry: true` in the manifest,
where there can only ever be one.

If an entity would model it better, say so before implementing — a `button` or `number` entity is more discoverable
than an action.

## Procedure

### 1. Describe it in `services.yaml`

```yaml
set_target_value:
  name: Set target value
  description: Write a new target value to the device.
  fields:
    config_entry_id:
      name: Integration entry
      description: The configured entry to write to.
      required: true
      selector:
        config_entry:
          integration: <domain>
    value:
      name: Value
      description: The new target value.
      required: true
      example: 21.5
      selector:
        number:
          min: 0
          max: 100
          step: 0.5
          unit_of_measurement: "%"
```

Write this before the Python. The YAML is the contract the user sees, and getting it right forces you to decide what
the action actually takes. Every field needs a selector; `required: true` only when there is no sensible default;
rarely used fields go under `advanced: true`.

### 2. Implement the handler

One module per logical group under `service_actions/`. Handlers take `(hass, entry, call)`:

```python
async def async_handle_set_target_value(
    hass: HomeAssistant,
    entry: {ClassPrefix}ConfigEntry,
    call: ServiceCall,
) -> None:
    """Handle the set_target_value action."""
    value: float = call.data[ATTR_VALUE]
    client = entry.runtime_data.client
    try:
        await client.async_set_target_value(value)
    except {ClassPrefix}ApiClientAuthenticationError as err:
        entry.async_start_reauth(hass)
        raise HomeAssistantError(
            translation_domain=DOMAIN,
            translation_key="auth_failed",
        ) from err
    except {ClassPrefix}ApiClientError as err:
        raise HomeAssistantError(
            translation_domain=DOMAIN,
            translation_key="set_target_value_failed",
            translation_placeholders={"error": str(err)},
        ) from err
    await entry.runtime_data.coordinator.async_request_refresh()
```

Every raised exception needs a matching `exceptions.<key>.message` entry in `translations/en.json`
([`ha-translations`](../ha-translations/SKILL.md)) — that is the step most easily forgotten, and hassfest will catch it.

`ConfigEntryAuthFailed` is deliberately absent: it only starts the reauth flow from `async_setup_entry` in
`__init__.py` or from the coordinator. In a handler it would just log, so the flow is started explicitly.

### 3. Register in `async_setup()` — not `async_setup_entry()`

Actions must exist even when no config entry is loaded, so automations referencing them validate and produce a helpful
error instead of "unknown service". Add the wrapper and registration in `service_actions/__init__.py`:

```python
SERVICE_SET_TARGET_VALUE = "set_target_value"

SET_TARGET_VALUE_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_CONFIG_ENTRY_ID): cv.string,
        vol.Required(ATTR_VALUE): vol.Coerce(float),
    }
)


async def async_setup_services(hass: HomeAssistant) -> None:
    async def handle_set_target_value(call: ServiceCall) -> None:
        entry = hass.config_entries.async_get_entry(call.data[ATTR_CONFIG_ENTRY_ID])
        if entry is None or entry.domain != DOMAIN:
            raise ServiceValidationError(
                translation_domain=DOMAIN,
                translation_key="entry_not_found",
            )
        if entry.state is not ConfigEntryState.LOADED:
            raise ServiceValidationError(
                translation_domain=DOMAIN,
                translation_key="entry_not_loaded",
            )
        await async_handle_set_target_value(hass, entry, call)

    if not hass.services.has_service(DOMAIN, SERVICE_SET_TARGET_VALUE):
        hass.services.async_register(
            DOMAIN,
            SERVICE_SET_TARGET_VALUE,
            handle_set_target_value,
            schema=SET_TARGET_VALUE_SCHEMA,
        )
```

`async_setup_services(hass)` is already called from `async_setup()` in `__init__.py` — do not add a second call in
`async_setup_entry()`.

The two checks are the other half of `action-setup`: because the action now exists while no entry is loaded, the
handler is the only thing standing between an unloaded entry and an `AttributeError` on `entry.runtime_data`.

### 4. Translations and icons

`services.<action>.name` / `.description` plus one pair per field, and the action icon in `icons.json`. The strings in
`services.yaml` are only the fallback — the translation file is what users actually see. See
[`ha-translations`](../ha-translations/SKILL.md).

### 5. Validate

```bash
script/lint && script/type-check
script/hassfest          # validates services.yaml against the translation keys
script/test
```

Then restart Home Assistant and call the action from _Developer tools → Actions_ — check that every field renders with
its selector, and that an intentional failure surfaces a readable message.

## Triggers and conditions

The same contract in a different file. When the integration should offer its own automation triggers — "the device
reported a fault", "the price crossed a threshold" — that is `trigger.py` plus `triggers.yaml`, not a device
automation.

**`device_trigger.py`, `device_condition.py` and `device_action.py` are frozen upstream**: existing ones keep working,
new ones are not accepted. They appear all over integrations from 2021–2023, so the pattern is familiar and wrong.

```python
class {ClassPrefix}FaultTrigger(Trigger):
    """Fires when the device reports a fault."""

    async def async_validate_config(self, hass, config): ...
    async def async_attach_runner(self, hass, run_action, config): ...


async def async_get_triggers(hass: HomeAssistant) -> dict[str, type[Trigger]]:
    """Return the triggers this integration provides."""
    return {"fault": {ClassPrefix}FaultTrigger}
```

New implementations only need `async_get_triggers`; the older `async_attach_trigger` / `TRIGGER_SCHEMA` module-level
form is the legacy shape. `conditions.yaml` and `async_get_conditions` mirror this exactly.

`triggers.yaml` has the same structure as `services.yaml` — `target:`, `fields:`, selectors — and the strings live
under the `triggers` and `conditions` keys in `translations/en.json`.

**Name them as a sentence about the device, not about the code**: "Light turned on", "Motion detected", "Vacuum
cleaner started cleaning", "[measurement] crossed threshold".

## Actions are what a voice assistant reads

The Assist LLM API exposes service actions to conversation agents using the `description` from the translations. That
makes the description functional, not decorative: write what the action does in a sentence a person would say, not
"Calls the set_target_value endpoint".

## Removing or renaming an action

Renaming an action breaks every automation and script that calls it. Treat it as a breaking change: see
[`ha-breaking-changes`](../ha-breaking-changes/SKILL.md) and get explicit approval first.

## Do not

- Do not add `vol.Schema` validation that contradicts the selector in `services.yaml` — two sources of truth for the
  same field is how a form starts accepting values the handler then rejects.
- Do not call it done before invoking it from _Developer tools → Actions_.

The remaining rules — registration location, exception types, `target:`, response data — are in
[`blueprint.service_actions.instructions.md`](../../instructions/blueprint.service_actions.instructions.md).
