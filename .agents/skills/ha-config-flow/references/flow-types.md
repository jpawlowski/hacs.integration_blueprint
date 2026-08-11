# The flow types, one by one

Read the section for the flow you are implementing. The rules that hold across all of them — data versus options,
unique IDs, reserved step names, schemas, versioning — are in
[`blueprint.config_flow.instructions.md`](../../../instructions/blueprint.config_flow.instructions.md) and load
automatically.

## User flow

Nothing beyond the general rules: validate before creating, set the unique ID and abort on a duplicate, return errors
by translation key, log unexpected exceptions.

## Discovery flow

**MUST:**

- Set unique ID in discovery step
- Abort if already configured: `self._abort_if_unique_id_configured()`
- Store placeholders for title: `self.context["title_placeholders"] = {"name": device_name}`
- Forward to user step for confirmation
- Update existing entries via `updates` parameter when device details change

**NEVER:**

- Auto-create entries without user confirmation
- Skip unique ID check

The `manifest.json` side, and the rule per protocol that fails silently when guessed, is in
[`discovery-matchers.md`](discovery-matchers.md).

## Reauth flow

**MUST:**

- Implement `async_step_reauth()` that forwards to `async_step_reauth_confirm()`
- Use `self._get_reauth_entry()` to access current entry
- Verify unique ID unchanged: `await self.async_set_unique_id(id)` then `self._abort_if_unique_id_mismatch()`
- Check source: `if self.source == SOURCE_REAUTH`
- Update entry: `return self.async_update_reload_and_abort(self._get_reauth_entry(), data_updates=user_input)`
- Set description placeholders: `description_placeholders={"name": self._get_reauth_entry().title}`

**NEVER:**

- Create new entry (always update existing)
- Skip unique ID verification
- Skip confirmation step

The flow starts with `source`, `entry_id` and `unique_id` already in `self.context`, and `title_placeholders` is set
to `{"name": <entry title>}` for you.

**Translation keys:**

- `config.step.reauth_confirm.title` — write the text out, e.g. `"Re-authenticate {name}"`
- `config.step.reauth_confirm.description` — explain what expired
- `config.abort.reauth_successful` — write the text out, e.g. `"Re-authentication was successful"`

Core's `[%key:common::…%]` references do not resolve in a custom integration.

**From outside a flow** — a coordinator or an action handler that hits an auth error — call
`entry.async_start_reauth(hass)`. `ConfigEntryAuthFailed` only starts the flow from `async_setup_entry` in
`__init__.py` or from the coordinator.

## Reconfigure flow

**MUST:**

- Use `self._get_reconfigure_entry()` to access current entry
- Verify unique ID unchanged if applicable: `await self.async_set_unique_id(id)` then
  `self._abort_if_unique_id_mismatch()`
- Check source: `if self.source == SOURCE_RECONFIGURE`
- Update entry: `return self.async_update_reload_and_abort(entry, data_updates=user_input)`
- Pre-fill form: `self.add_suggested_values_to_schema(schema, entry.data)`

**NEVER:**

- Create new entry (always update existing)
- Use for authentication changes (use reauth)

**Optional:** `reload_even_if_entry_is_unchanged=False` skips the reload when nothing changed.

## Options flow

**MUST:** Return via `async_get_options_flow()`, implement `async_step_init()`, pre-fill with existing options.

The handler is constructed with **no arguments** (`return OptionsFlowHandler()`); the base class provides
`self.config_entry`. Older examples that store it themselves are wrong.

**Auto-reload:** subclass `OptionsFlowWithReload` — no manual listener needed. The manual alternative is an update
listener registered in `async_setup_entry()` that calls `async_reload()`.

## Subentry flow

**MUST:** Return types via `async_get_supported_subentry_types()`, implement `async_step_user()`, finish with
`async_create_entry()` — on `ConfigSubentryFlow` it returns a `SubentryFlowResult`. There is no
`async_create_subentry()`.

**Access and reconfigure:** `self._get_entry()` for the parent entry, `self._get_reconfigure_subentry()` for the
subentry being edited, and `async_update_and_abort()` to finish a reconfigure step.

**NEVER:** Support discovery or reauth in subentries — a subentry flow can only start from `user` or `reconfigure`.

**Unique IDs:** a subentry's unique ID only has to be unique within its config entry, not globally.

**Translations:** subentry strings live under `config_subentries.<type>.…`, not under `config`.

**Device ownership (Home Assistant 2026.8+):**

- A device belongs to exactly one config entry and to at most one config subentry.
- Create one device per subentry. Multiple subentries must never attach entities to a shared device.
- Keep a hub/account device on the parent config entry without a subentry. Create separate devices for subentries and,
  when a parent relationship is needed, link them with `via_device_id`.
- Migrations that previously shared a device across subentries must create the per-subentry devices and relink their
  entities. Do not rely on Home Assistant's temporary composite-device compatibility behavior.

## Chaining flows

`next_flow` and `async_on_create_entry()` continue into another flow once an entry exists. Subentry and options flows
depend on the config entry already existing, so they **can only** be reached through `async_on_create_entry()`.
