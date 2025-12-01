# Contribution guidelines

Contributing to this project should be as easy and transparent as possible, whether it's:

- Reporting a bug
- Discussing the current state of the code
- Submitting a fix
- Proposing new features

## GitHub is used for everything

GitHub is used to host code, to track issues and feature requests, as well as accept pull requests.

Pull requests are the best way to propose changes to the codebase.

1. Fork the repo and create your branch from `main`.
2. Run `script/setup/bootstrap` to install dependencies and pre-commit hooks.
3. If you've changed something, update the documentation.
4. Make sure your code passes all checks (using `script/check` for linting and type checking).
5. Test your contribution.
6. Issue that pull request!

## Any contributions you make will be under the MIT Software License

In short, when you submit code changes, your submissions are understood to be under the same [MIT License](http://choosealicense.com/licenses/mit/) that covers the project. Feel free to contact the maintainers if that's a concern.

## Report bugs using GitHub's [issues](../../issues)

GitHub issues are used to track public bugs.
Report a bug by [opening a new issue](../../issues/new/choose); it's that easy!

## Write bug reports with detail, background, and sample code

**Great Bug Reports** tend to have:

- A quick summary and/or background
- Steps to reproduce
  - Be specific!
  - Give sample code if you can.
- What you expected would happen
- What actually happens
- Notes (possibly including why you think this might be happening, or stuff you tried that didn't work)

People *love* thorough bug reports. I'm not even kidding.

## Use a Consistent Coding Style

This project uses:

- [Ruff](https://github.com/astral-sh/ruff) for linting and formatting
- [Pyright](https://github.com/microsoft/pyright) for type checking

Run `script/check` to lint and type-check your code before submitting, or `script/lint` to auto-format and fix linting issues.

**Local validation:** Run `script/hassfest` to validate your integration against Home Assistant's quality standards using the official validation tools. This checks manifest.json, translations, services.yaml, and integration structure locally before pushing to GitHub.

## GitHub Copilot Support

This project includes [prompt files](./.github/prompts/) to help you work more efficiently with GitHub Copilot. These reusable templates provide context and requirements for common tasks:

- **Add New Sensor** - Create sensors with proper structure
- **Add New Service** - Implement services with validation
- **Add Config Option** - Add configuration options to flows
- **Add Entity to Device** - Expand device capabilities
- **Debug Coordinator Issue** - Diagnose data update problems
- **Update Translations** - Manage multilingual strings

**Example usage in Copilot Chat:**

```text
#file:Add New Sensor.prompt.md Add a temperature sensor
```

See the [prompts README](./.github/prompts/README.md) for details on using these templates.

## Code Quality

This blueprint follows Home Assistant's [integration quality standards](https://developers.home-assistant.io/docs/core/integration-quality-scale/) as best practices. The code includes:

- ✅ Comprehensive docstrings with links to official documentation
- ✅ Full type hints for better IDE support
- ✅ Config flow with reauthentication support
- ✅ Proper error handling and entity unavailability
- ✅ Coordinator pattern for efficient data fetching

**Don't worry!** You don't need to maintain all of this. The blueprint gives you a solid, well-documented starting point. Feel free to simplify or adapt anything to your needs - the goal is to help you get started quickly with good patterns, not to overwhelm you with requirements.

## Test your code modification

This project comes with a complete development environment in a container, easy to launch
if you use Visual Studio Code. With this container you will have a standalone
Home Assistant instance running and already configured with the included
[`configuration.yaml`](./config/configuration.yaml) file.

You can also run tests using `script/test` to ensure your changes don't break existing functionality.

## License

By contributing, you agree that your contributions will be licensed under its MIT License.
