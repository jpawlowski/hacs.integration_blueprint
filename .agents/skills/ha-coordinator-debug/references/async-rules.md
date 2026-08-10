# Async rules: threads, blocking calls, late imports

Lookup tables for the three async mistakes that produce a warning or a hang rather than a clean error. The everyday
rules — `async def` for I/O, `asyncio.timeout()`, `@callback` semantics, where to create tasks — are in
[`blueprint.python.instructions.md`](../../../instructions/blueprint.python.instructions.md) and load automatically.

Enable Home Assistant's debug mode **and** asyncio's during development: most of what follows is then reported the
moment it happens instead of surfacing later as a hang or a state that quietly went wrong.

## Calling Home Assistant from a non-event-loop thread

The `async_*` APIs are not thread-safe, and Home Assistant raises when they are called from the wrong thread. A
library callback running on its own thread is the usual reason to need one of these. Detection landed in HA 2024.5.

| From a worker thread, instead of                                                               | call                                                |
| ---------------------------------------------------------------------------------------------- | --------------------------------------------------- |
| `hass.async_create_task`                                                                       | `hass.create_task`                                  |
| `hass.bus.async_fire`                                                                          | `hass.bus.fire`                                     |
| `hass.services.async_register` / `async_remove`                                                | `hass.services.register` / `remove`                 |
| `entity.async_write_ha_state`                                                                  | `entity.schedule_update_ha_state`                   |
| `async_dispatcher_send`                                                                        | `dispatcher_send`                                   |
| `issue_registry.async_get_or_create` / `async_delete`                                          | `issue_registry.create_issue` / `delete_issue`      |
| `event.async_track_state_change_event`                                                         | `event.track_state_change_event`                    |
| The registries (`device_`, `entity_`, `area_`, …) and `hass.config_entries.async_update_entry` | no sync twin — wrap the call in `hass.add_job(...)` |

`hass.add_job` is the sync entry point and is not deprecated; `hass.async_add_job` is.

## Blocking calls in the event loop

Expanded detection landed in HA 2024.7, so an older integration may have been legal once and is not now.

- **File:** `open()`, `pathlib.Path.read_text()` / `.read_bytes()` / `.write_text()`
- **Directory:** `os.listdir()`, `os.walk()`, `os.scandir()`, `os.stat()`, `glob.glob()`, `glob.iglob()`
- **Network:** `urllib` — use `aiohttp`
- **Other:** `time.sleep()`

All of them belong in the executor: `await hass.async_add_executor_job(blocking_func)`, and
`await hass.async_add_executor_job(partial(f, kwarg=True))` when there are keyword arguments.

**The `open()` trap:** Home Assistant detects the `open` call and nothing after it. Moving `open` into the executor
while leaving `.read()` in the event loop silences the warning without fixing the block — move the whole file
operation.

**SSL is not an executor problem.** `SSLContext.load_default_certs()`, `load_verify_locations()`, `load_cert_chain()`
and `set_default_verify_paths()` block, and the fix is to stop building the context yourself:
`async_get_clientsession(hass)`, `homeassistant.helpers.httpx_client.get_async_client()`, or `homeassistant.util.ssl`.

## Late imports

CPython's import machinery is not thread-safe, so the right helper depends on how the module can be reached:

| The module is…                               | Import it with                                             |
| -------------------------------------------- | ---------------------------------------------------------- |
| At module level                              | A plain import — safe, it is loaded on the import executor |
| Imported in exactly one place, conditionally | `await hass.async_add_executor_job(_do_the_late_import)`   |
| Possibly imported concurrently               | `homeassistant.helpers.importlib.import_module`            |
| Reachable from several code paths            | `await async_import_module(hass, "module.path")`           |
| Needed only for type annotations             | `if TYPE_CHECKING:`                                        |

Prefer not importing rarely used code at all over importing it late and badly.
