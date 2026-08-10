---
name: "Coordinator"
description: "Update intervals, pull versus push, and mapping API errors to HA exceptions"
applyTo: "custom_components/**/coordinator/**/*.py, custom_components/**/api/**/*.py"
paths:
  - "custom_components/**/coordinator/**/*.py"
  - "custom_components/**/api/**/*.py"
---

# Coordinator Instructions

**Procedure:** [`ha-coordinator-debug`](../skills/ha-coordinator-debug/SKILL.md) — load it when data is stale, entities
are unavailable or setup fails. This file is the rule set; the skill is the local run loop, how to read the log, and
the four coordinator failures no exception-mapping table can express.

**Applies to:** Coordinator implementation files (always sent together with `blueprint.api.instructions.md`)

## Using the Coordinator

✅ **Correct:** `self.coordinator.data.temperature` (in entity properties)

❌ **Wrong:** `await self.api_client.get_data()` (never fetch directly in entities)

## Error Handling in `_async_update_data()`

**Exception mapping:**

- `ApiAuthError` → `raise ConfigEntryAuthFailed from err` (triggers reauth)
- `ApiError` → `raise UpdateFailed("message") from err` (retry at next interval)
- `ApiRateLimited` → `raise UpdateFailed(retry_after=60) from err` (backoff)

**Automatic handling:** `TimeoutError` and `aiohttp.ClientError` handled by coordinator base class

## Pull vs. Push Architecture

**Polling (Pull) - Default for most integrations:**

- Coordinator fetches data at fixed intervals via `_async_update_data()`
- Simple, reliable, works with any API
- Set via `update_interval` parameter in coordinator constructor

**Push (Event-driven) - Preferred when available:**

- Device/service sends updates to Home Assistant
- Requires: WebSocket, Webhook, MQTT, or similar push mechanism
- Call `coordinator.async_set_updated_data(new_data)` when data arrives
- Set `update_interval=None` or use long interval as fallback for offline detection

**Prefer push over polling when:**

- Device supports push notifications (WebSocket, Webhook, etc.)
- Protocol is well-documented and implementation effort is reasonable
- Real-time updates improve user experience (faster reaction, less lag)
- Reduces system load (no periodic polling overhead, lower API/network usage)

**Use polling when:**

- Device/API doesn't support push
- Push protocol is proprietary/undocumented
- Implementation complexity outweighs benefits

**Implementation notes:**

- Pull: Coordinator handles everything automatically via `update_interval`
- Push: Set up the coordinator-level listener in `async_setup_entry()`, call `async_set_updated_data()` on events.
  A subscription held by an **entity** goes in `async_added_to_hass()` instead and is released via
  `self.async_on_remove(...)` — a disabled entity is never added, so subscribing at setup leaks.
- `async_set_updated_data()` on a polling coordinator also resets the timer until the next poll
- Hybrid: Use push for updates + polling as fallback for connection monitoring

See [HA Data Update Patterns](https://developers.home-assistant.io/docs/integration_fetching_data)

## First Refresh

**In `async_setup_entry()` in `__init__.py`:** Call `await coordinator.async_config_entry_first_refresh()`

**Automatic handling:** If `_async_update_data()` raises `UpdateFailed`, coordinator raises `ConfigEntryNotReady` automatically

**When setup should not be retried at all**, use `await coordinator.async_refresh()` instead — it does not raise, so
the entry loads with entities in an unavailable state rather than going into the retry loop.

See [Integration Setup Failures](https://developers.home-assistant.io/docs/integration_setup_failures#integrations-using-async_setup_entry)

## Always Update Parameter

`always_update=True` (default) - Always notify entities of new data

`always_update=False` - Only notify if data changed (requires `__eq__` implementation in data class)

## Caching API Data

### In memory, to fetch less often than entities update

**When:** API rate limits stricter than update needs (e.g., API allows 1 req/5min, entities need 30s updates)

**Pattern:** Store `_api_cache`, `_api_cache_time`, `_api_cache_ttl` as instance variables. In `_async_update_data()`: Check if cache fresh (TTL not expired), return cached data if fresh, else fetch new data and update cache.

**Use cases:** Expensive API calls, rate-limited APIs, multiple entities reading same raw data

**Result:** Entities update frequently (coordinator `update_interval`), API fetches less often (cache TTL)

### Persisted, so the integration works without a connection at startup

Home Assistant restarts without internet more often than one would think — after a power cut it is regularly up before
the router is. The reflex, `async_config_entry_first_refresh()`, raises `ConfigEntryNotReady` when that first fetch
fails, and then **no entity exists at all**: exactly when the user most wants to see the last known values, the
integration shows nothing.

**First decide whether the cached payload is still true**, because this is what separates honest caching from lying
about the device:

| The payload…                                                                           | On a cold start with no network            |
| -------------------------------------------------------------------------------------- | ------------------------------------------ |
| Covers a defined period — today's electricity prices, a published forecast, a schedule | Restore it. It is complete and still valid |
| Is a point-in-time reading — a temperature, a power draw, an online/offline flag       | Do **not** restore it. It is stale         |

For the first kind:

- Persist the payload with `homeassistant.helpers.storage.Store` when a fetch succeeds, and load it in
  `async_setup_entry` before the coordinator's first refresh.
- **Return the cached payload from `_async_update_data()` instead of raising `UpdateFailed`**, as long as it is still
  inside its validity window. This is the part that actually works: `CoordinatorEntity.available` is exactly
  `coordinator.last_update_success`, so raising `UpdateFailed` and merely leaving `coordinator.data` populated makes
  every entity unavailable and shows the user nothing.
- Once the window has passed, raise `UpdateFailed` as normal. Serving yesterday's prices as today's is worse than
  going unavailable.
- Log the fallback once at `info` level, so "still on cached data" is visible without spamming every poll.

The Bronze `test-before-setup` rule is satisfied either way: setup still fails loudly when there is nothing valid to
fall back on. What changes is that a valid cache counts as "we can work".

**Values that change with the clock need a scheduler, not a shorter interval.** A "current price" sensor derived from
a daily payload changes on the hour; the answer is one fetch per validity window plus
`async_track_point_in_utc_time` / `async_track_time_change` to recompute locally — not polling every minute so the
value happens to flip in time. Polling for something the integration can compute is also what makes
`appropriate-polling` look violated.

Entity-level state restoration is a different mechanism for a different problem — see `RestoreSensor` in
[`platform-members.md`](../skills/ha-entity-platform/references/platform-members.md). Use it for a value the entity
accumulates itself; use `Store` for the payload the coordinator hands out.
