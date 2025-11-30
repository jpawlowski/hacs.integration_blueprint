# Working with GitHub Copilot Coding Agent

## Initial Transformation Prompt

**Context:** This project is a fresh, unmodified blueprint template. Your task is to transform it into a working integration for the target device/service.

The blueprint is well-documented (see `AGENTS.md` and `.github/copilot-instructions.md`). You should analyze the existing structure and remove/modify files as needed.

### What to Include in Your Prompt

**Essential information:**

- **High-level idea** - What the device/service does (2-3 sentences)
- **API/Protocol** - How to connect (REST/MQTT/WebSocket, authentication)
- **Example API response** - Paste actual JSON/data structure

**Optional (Copilot can figure these out):**

- Config flow requirements - Agent will analyze what needs to be configured
- Which entities to keep/remove - Agent will determine based on API structure
- Rate limits or API considerations - Include if critical

### Prompt Template

```markdown
This is a fresh Home Assistant integration blueprint. Transform it for [DEVICE/SERVICE NAME].

High-level: [2-3 sentences about what it does]

API Details:
- Protocol: [REST/GraphQL/WebSocket/MQTT/etc.]
- Endpoint: [base URL or connection details]
- Auth: [API key/OAuth/none]

Example API response:
[paste JSON or data structure from actual device/service]

Tasks:
1. Analyze the blueprint structure (documented in AGENTS.md)
2. Remove entity platforms not needed for this device
3. Implement API client based on above structure
4. Update entities to match available data
5. Customize config flow for required user inputs
6. Update README, docs, and translations
7. Run script/check to validate

The blueprint has example entities - remove what's not needed, keep and adapt what makes sense.
```

### Example: Smart Thermostat

```markdown
This is a fresh Home Assistant integration blueprint. Transform it for MyDevice Smart Thermostat.

High-level: Smart thermostat that controls temperature via REST API. Reads current
temp/humidity, sets target temperature, changes heating/cooling mode.

API Details:
- Protocol: REST API
- Endpoint: http://{host}/api/v1/
- Auth: API key in X-API-Key header

Example API response from /status:
{
  "temp": {"current": 21.5, "target": 22.0},
  "humidity": 45,
  "mode": "heat",
  "state": "heating"
}

Tasks:
1. Analyze the blueprint structure (documented in AGENTS.md)
2. Remove entity platforms not needed (fan, number, select, switch)
3. Keep climate platform, customize for thermostat control
4. Keep sensor platform for temperature/humidity
5. Keep binary_sensor for connectivity only
6. Implement API client: get_status(), set_temperature(), set_mode()
7. Update config flow to ask for host and API key
8. Update README and translations
9. Run script/check to validate

The blueprint has example entities - remove what's not needed, keep and adapt what makes sense.
```

Let the Copilot Agent analyze the blueprint and determine the best structure.

## Testing Copilot's Changes

After Copilot creates a draft pull request:

1. **Open the PR branch in Codespaces**
   - Navigate to the pull request on GitHub
   - Click "Code" → "Create codespace on `branch-name`"
   - Codespace starts with all dependencies pre-installed (see [CODESPACES.md](CODESPACES.md))

2. **Start Home Assistant**
   - Run `./script/develop` in the terminal
   - Port 8123 forwards automatically (forwarded URL appears in notification)
   - Click the forwarded port URL to open HA in browser

3. **Test the integration**
   - Add the integration via Home Assistant UI
   - Verify entities appear correctly
   - Test functionality with your actual device/service
   - Check logs: `config/home-assistant.log` or live in terminal

4. **Iterate if needed**
   - Comment on the PR with `@copilot` to request changes
   - Or make manual adjustments and commit to the PR branch
   - Stop Codespace when done to save free hours

**Note:** Copilot Agent runs in GitHub Actions (ephemeral environment), so it cannot provide live web access to Home Assistant during development. Manual testing in Codespaces is required.

For detailed Codespaces usage, troubleshooting, and resource management, see [CODESPACES.md](CODESPACES.md).

## Tips

- Start simple - get a working prototype first
- Use `@copilot` in PR comments to iterate
- Break large changes into multiple PRs

## Resources

- [GitHub Copilot Best Practices](https://docs.github.com/en/copilot/tutorials/coding-agent/get-the-best-results)
- `AGENTS.md` and `.github/copilot-instructions.md` - Instructions Copilot reads automatically
