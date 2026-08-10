---
name: blueprint-scaffold
description: >-
  Turn this freshly initialised blueprint into a working integration for one concrete device or service — decide
  the manifest classification, write the API client, shape the coordinator payload, keep or delete each example
  entity platform, and get the first end-to-end run green. Use when asked to "transform the blueprint", "make
  this an integration for <device>", "implement the API client", "remove the example entities", "adapt the
  template to my service", or when the repository still ships the blueprint's demo platforms and nobody has
  written real code yet. Covers the facts to gather before writing anything, the order the layers must be built
  in, and how to retire this skill afterwards. SYMPTOMS — load this if you are about to: invent a response
  payload instead of asking for a real one; keep an example platform "for later"; write entities before the API
  client and coordinator exist; pick `hub` because it sounds impressive; or start scaffolding in a repository
  that already has real integration code.
---

# Scaffold the blueprint into a real integration

**This is a one-time task.** It runs once, in a repository that has been initialised with `initialize.sh` but still
contains the blueprint's example platforms. Everything it produces is ordinary integration code afterwards, maintained
with the `ha-*` skills.

**Stop if the repository already has real code.** Placeholder identifiers gone _and_ platforms that match a real
device mean scaffolding already happened. Adding an entity to an existing integration is
[`ha-entity-platform`](../ha-entity-platform/SKILL.md), not this. Migrating a pre-existing integration in is
[`blueprint-import`](../blueprint-import/SKILL.md).

## 1. Gather the facts — do not start without them

| Fact                            | Why it decides something                                            |
| ------------------------------- | ------------------------------------------------------------------- |
| What the device or service does | Which platforms survive step 4                                      |
| Protocol and base URL           | API client shape; whether an existing library is the better call    |
| Authentication                  | Config flow fields, and whether reauth is needed                    |
| **A real response payload**     | The coordinator's data shape, and every entity's value accessor     |
| Push or poll, and how often     | `iot_class`, `UPDATE_INTERVAL`, whether a listener replaces polling |
| A stable per-install identifier | The config entry `unique_id`                                        |

The payload is the one that cannot be guessed. Ask for an actual captured response — a curl dump, a log line, a
screenshot of the vendor docs. Entities built against an invented shape look finished and fail on first contact.

If a maintained PyPI library already wraps this API, weigh it against a small `aiohttp` client using the criteria in
[`AGENTS.md`](../../../AGENTS.md) ("Custom Integration Flexibility"), and record the outcome in
`docs/development/DECISIONS.md` ([`ha-planning`](../ha-planning/SKILL.md)). This is the decision that is most
expensive to revisit later.

## 2. Classify it in the manifest

`integration_type` drives how Home Assistant presents the integration and how you model devices:

- `device` — one physical thing per config entry. The common case.
- `service` — one account or cloud service per config entry.
- `hub` — a gateway that fans out to several devices. Only if a single entry really yields many devices.

Set `iot_class` to match reality (`local_polling`, `cloud_polling`, `local_push`, `cloud_push`). Add discovery
matchers only when you will also implement the matching flow step
([`ha-config-flow`](../ha-config-flow/SKILL.md)); a matcher without a handler fails `script/hassfest`.

Declare runtime dependencies in **both** `manifest.json` → `requirements` and the root `requirements.txt`
([`blueprint-tooling`](../blueprint-tooling/SKILL.md)).

## 3. Build the layers bottom-up

Entities → coordinator → API client. Build in the reverse of that order, because each layer is testable before the
one above it exists.

1. **`api/`** — the client and its exception types. Nothing Home Assistant-specific in here: no `hass`, no entity
   imports. Raise your own auth/connection/unknown exceptions and let the coordinator translate them.
2. **`coordinator/`** — replace `_async_update_data` with the real call and return the shape the entities will read.
   Translate API exceptions into `ConfigEntryAuthFailed` or `UpdateFailed` there and only there
   ([`ha-coordinator-debug`](../ha-coordinator-debug/SKILL.md)).
3. **`data.py` / `const.py`** — the runtime data container and the constants the platforms share.

Decide the coordinator's data shape deliberately: a parsed model or `TypedDict` beats passing raw JSON around,
because every entity would otherwise repeat the same defensive key lookups.

## 4. Keep, adapt, delete each platform

The blueprint ships `binary_sensor`, `button`, `fan`, `number`, `select`, `sensor`, `switch` as worked examples. For
each one: does the real device expose this?

- **Yes** → adapt it. Reuse the file layout and the `EntityDescription` pattern
  ([`ha-entity-platform`](../ha-entity-platform/SKILL.md)).
- **No** → delete the whole directory. Not a stub, not a commented-out class.

Then update `PLATFORMS` in `custom_components/<domain>/__init__.py` to exactly the surviving list, and delete the
matching `entity.<platform>.*` blocks from `translations/en.json` and `icons.json`. A platform left in `PLATFORMS`
without a directory fails at setup; an orphaned translation key fails `script/hassfest`.

Same treatment for `service_actions/` and `services.yaml` — the example actions go unless the device has a real
equivalent ([`ha-service-action`](../ha-service-action/SKILL.md)).

## 5. Config flow and identity

Ask for the minimum needed to connect, validate it by actually connecting, and set a `unique_id` from a serial
number, MAC, or account ID — never a host, IP, URL, or user-chosen name. Add reauth if credentials can expire.
Details and the reserved step names: [`ha-config-flow`](../ha-config-flow/SKILL.md).

The unique ID choice is effectively permanent — changing it later is a breaking change
([`ha-breaking-changes`](../ha-breaking-changes/SKILL.md)).

## 6. Strings, then validation, then a real run

1. `translations/en.json` and `icons.json` for every surviving entity, flow step, action and exception —
   English only, `en.json` only ([`ha-translations`](../ha-translations/SKILL.md)).
2. `script/lint` and `script/type-check` until both are clean, then `script/hassfest`.
3. Tests for the config flow and at least one platform ([`ha-testing`](../ha-testing/SKILL.md)), then `script/test`.
4. `script/develop`, add the integration through the UI, and confirm the entities carry real values. Scaffolding is
   not done until this has happened — a green suite proves the mocks agree with each other, not that the device
   answers.

Report honestly which of these you ran and which you could not ([`AI_POLICY.md`](../../../AI_POLICY.md)). Real-device
verification is the developer's to do, not yours to claim.

## 7. Finish the paperwork, then retire this skill

- Update `README.md` and `docs/user/` to describe the real integration.
- Record the library-versus-own-client decision in `docs/development/DECISIONS.md` if you have not already.
- Commit in reviewable pieces, following [`ha-release`](../ha-release/SKILL.md). Never commit unasked.

Scaffolding happens once. Once the integration is real, this skill is dead weight in every future session, so remove
it as the last step:

1. Delete `.agents/skills/blueprint-scaffold/`.
2. Remove its rows from the catalogues in `.agents/skills/README.md` and `AGENTS.md`.
3. Add `.agents/skills/blueprint-scaffold/` to `.templatesyncignore` — without it, the next weekly template-sync
   pull request puts the skill straight back.

## Do not

- Do not write entities against a payload nobody has seen.
- Do not keep an example platform because it "might be useful later" — it ships broken entities to users.
- Do not hardcode `name=` or `icon=` while scaffolding with the intention of fixing it afterwards; the fix never
  comes and the entity IDs are already public by then.
- Do not skip `script/hassfest` because `script/check` passed — they check different things.
- Do not describe the result as tested when only the mocked suite ran.
