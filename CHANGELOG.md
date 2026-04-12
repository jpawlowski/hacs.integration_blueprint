# Changelog

## [0.1.1](https://github.com/jpawlowski/hacs.integration_blueprint/compare/v0.1.0...v0.1.1) (2026-04-12)


### Features

* add migration guide for existing HACS integrations and update template sync ignore ([5770ade](https://github.com/jpawlowski/hacs.integration_blueprint/commit/5770adecb714a5751bbb8fcd70ad76a8d9277a3f))
* add shfmt installation step to lint workflow and remove unnecessary workflows permission from template sync ([be79477](https://github.com/jpawlowski/hacs.integration_blueprint/commit/be794779d15845f645e721f1b27690d5b4b4a689))
* add user extensibility layer and template sync infrastructure ([d0f08cd](https://github.com/jpawlowski/hacs.integration_blueprint/commit/d0f08cd1452b32ec6297a1c19eba1f76f2afe5f8))
* **bootstrap:** conditionally install pre-commit hooks based on environment ([25626d6](https://github.com/jpawlowski/hacs.integration_blueprint/commit/25626d6b7760a3aa80c1e35a75eb40c56c6b33c6))
* **bootstrap:** update pre-commit hook installation logic for GitHub Actions ([cc39641](https://github.com/jpawlowski/hacs.integration_blueprint/commit/cc39641717ee3c308131e86106a742ecc8b1b3bc))
* **config:** add config schema for integration and enhance error descriptions ([74c1420](https://github.com/jpawlowski/hacs.integration_blueprint/commit/74c1420baf5183bfb3fca948a59bb72ce92545a4))
* **coordinator:** implement data update coordinator with error handling and event listeners ([5133d2a](https://github.com/jpawlowski/hacs.integration_blueprint/commit/5133d2a4168bbc790db7c840195012ebd5765666))
* **copilot:** add GitHub Copilot Coding Agent setup workflow and update README instructions ([4958503](https://github.com/jpawlowski/hacs.integration_blueprint/commit/49585031efdc9178e32f4456a8249d7cd53eb573))
* **devcontainer:** expose npm binaries on PATH for AI agents ([59d690a](https://github.com/jpawlowski/hacs.integration_blueprint/commit/59d690ac1a83a49a6d1ba0ecb6d3decae9f0e89e))
* **devcontainer:** mount host gh CLI config for automatic auth ([31a4e1f](https://github.com/jpawlowski/hacs.integration_blueprint/commit/31a4e1f0e0512fa9013d8f87a35f44e46e6fbe89))
* **docs:** add comprehensive documentation for GitHub Copilot Coding Agent usage and testing ([10d4986](https://github.com/jpawlowski/hacs.integration_blueprint/commit/10d498678c668a01619dad31298faa16dfdc3b40))
* **docs:** add hassfest validation instructions and local validation script ([65b5bdd](https://github.com/jpawlowski/hacs.integration_blueprint/commit/65b5bdd5f203bda60da2a744312f6c7e88b8d3be))
* **docs:** enhance JSON formatting guidelines in translation instructions ([f0b09c3](https://github.com/jpawlowski/hacs.integration_blueprint/commit/f0b09c34a9441c5423b3c4db80c7aa57864fdd00))
* **docs:** update package structure guidelines and restrictions in Copilot and AGENTS documentation ([807e4d1](https://github.com/jpawlowski/hacs.integration_blueprint/commit/807e4d1a4f6fdc84a2999fd29ba066bc0bd1a5e2))
* **docs:** update translation instructions to clarify JSON formatting rules and placeholder usage ([cd0e1c3](https://github.com/jpawlowski/hacs.integration_blueprint/commit/cd0e1c3fafc0ac5b25c40beab17ac97407141b62))
* **entity:** add base entity class for ha_integration_domain with common functionality ([3dcb6ef](https://github.com/jpawlowski/hacs.integration_blueprint/commit/3dcb6ef851082dea66775894986068c9cbe787e0))
* **github:** add CODEOWNERS and auto-assign workflow ([f88df98](https://github.com/jpawlowski/hacs.integration_blueprint/commit/f88df986f0adc018fa14abdd087233674d6553f5))
* **gitignore:** enhance pruning logic to handle wildcard patterns and add hardcoded exclusions ([849d939](https://github.com/jpawlowski/hacs.integration_blueprint/commit/849d939d5e029862f6c9d28ba6f0c009fe4f448b))
* initial blueprint with modern Home Assistant patterns ([9625887](https://github.com/jpawlowski/hacs.integration_blueprint/commit/962588737809505c578d7cd0ae2d17b99ffe71fc))
* **initialize:** add parsing of .gitignore for prune paths and negations ([72b50c0](https://github.com/jpawlowski/hacs.integration_blueprint/commit/72b50c0c260aa44a62f63fc72475c086e128e58d))
* **initialize:** enhance repository handling in initialization script ([a7485e3](https://github.com/jpawlowski/hacs.integration_blueprint/commit/a7485e3e80aec42420af09d150283411eb013ac6))
* **pre-commit:** enhance Ruff and Codespell hooks for better virtual environment handling ([e3791ea](https://github.com/jpawlowski/hacs.integration_blueprint/commit/e3791ea263dc0e4b120ae13b99bb0d3a8c6861b5))
* **repairs:** add repair flow for deprecated API endpoint and missing configuration issues ([fe3f5f5](https://github.com/jpawlowski/hacs.integration_blueprint/commit/fe3f5f57213bcd0f138a073c49cc3e1cc5d920e7))
* **schema:** add JSON schema for icons.json and update file match settings ([ce5cc35](https://github.com/jpawlowski/hacs.integration_blueprint/commit/ce5cc3519d156ea5fbd571382ff43ec66de36cbd))
* **scripts:** improve virtual environment activation logic with error handling ([163d729](https://github.com/jpawlowski/hacs.integration_blueprint/commit/163d7291d5928c3d31b3708900913c78d1e816b3))
* **scripts:** update virtual environment handling for improved compatibility across environments ([3ebd694](https://github.com/jpawlowski/hacs.integration_blueprint/commit/3ebd694649d25302287e0d965d67d2b36a2878c2))
* **setup:** enhance symlink creation for virtual environments and HACS integrations ([05abb6e](https://github.com/jpawlowski/hacs.integration_blueprint/commit/05abb6ea54948cc62c2d5404d48bd5ea220e9d25))
* **tooling:** add Prettier and markdownlint-cli2 for Markdown linting ([ac71c4f](https://github.com/jpawlowski/hacs.integration_blueprint/commit/ac71c4fa581777124099325acf7175c8fb30ae8e))
* **workflows:** add pull_request trigger for copilot setup workflow ([1f1d499](https://github.com/jpawlowski/hacs.integration_blueprint/commit/1f1d499896a12db6383e5eb150b228fcdaf44f9e))
* **workflows:** refine cache restore keys for Home Assistant installation ([26a2cae](https://github.com/jpawlowski/hacs.integration_blueprint/commit/26a2caefde78ae8a7b76342a09f4af1dd9bd2b83))
* **workflows:** synchronize HA_VERSION across workflow files and enhance caching for dependencies ([0f7ed00](https://github.com/jpawlowski/hacs.integration_blueprint/commit/0f7ed008219a09eeaaca5876a7bf14d50400ec82))
* **workflows:** update cache actions for improved performance and reliability ([58a1678](https://github.com/jpawlowski/hacs.integration_blueprint/commit/58a16782b3d56c3304f2b4c4aee19e7a9037d0a2))


### Bug Fixes

* **air_quality.py, diagnostic.py:** replace hardcoded units with constants for better maintainability ([3e9b52e](https://github.com/jpawlowski/hacs.integration_blueprint/commit/3e9b52ece5aba7e0720c088ea41d28f1475b1c35))
* **ci:** resolve broken venv symlinks in GitHub Actions ([7469114](https://github.com/jpawlowski/hacs.integration_blueprint/commit/746911485e35c3c02746d1c9bbe55cef190dea5b))
* **config_flow:** use description placeholders for documentation URL ([17e4b0c](https://github.com/jpawlowski/hacs.integration_blueprint/commit/17e4b0c24acb00ffec16516a4dca706c70e0ae43))
* **config:** enable dual-stack IPv4/IPv6 and remote access ([8d918fb](https://github.com/jpawlowski/hacs.integration_blueprint/commit/8d918fb1bf5215ef6db44211fa87ee5a259aaa3a))
* **configuration.yaml:** change server_host to 0.0.0.0 for better accessibility ([4737431](https://github.com/jpawlowski/hacs.integration_blueprint/commit/47374315989ce877877f97393671686689f33033))
* **devcontainer.json:** update container name for clarity ([e965fc5](https://github.com/jpawlowski/hacs.integration_blueprint/commit/e965fc56e21c94a906f28c350e8d76b4196609ff))
* **dev:** ensure clean restart by killing debugpy process ([d204f0b](https://github.com/jpawlowski/hacs.integration_blueprint/commit/d204f0b01056fb65c35df317f908c3eef2618e62))
* **diagnostics.py:** improve security by redacting sensitive data in diagnostics ([f6cf9a8](https://github.com/jpawlowski/hacs.integration_blueprint/commit/f6cf9a8b53aea40f548f8f7c376e34c8be8d6d2d))
* **docs:** enhance test instructions with detailed examples and best practices for mocking and registry testing ([5530503](https://github.com/jpawlowski/hacs.integration_blueprint/commit/5530503cb189680ebc44f00019759faf13524e73))
* **docs:** update architecture documentation to reflect coordinator package structure and functionality ([dffd8e1](https://github.com/jpawlowski/hacs.integration_blueprint/commit/dffd8e1050e8bfecbe1478b3b5d37d4bb40a068b))
* **hacs.json:** update Home Assistant version to 2025.11.3 ([c39962b](https://github.com/jpawlowski/hacs.integration_blueprint/commit/c39962b8cf7d91debf93d3f599fe46fc16cb7300))
* **initialize.sh:** remove unused README template exclusion and related dry-run messages ([81b8721](https://github.com/jpawlowski/hacs.integration_blueprint/commit/81b8721804d68f6d8c7d11d28dc0efcf115d0ad9))
* **init:** prevent false "uncommitted changes" warning in containers ([e5bcbbf](https://github.com/jpawlowski/hacs.integration_blueprint/commit/e5bcbbf426d1ecdcf60adf781df63ea17778df4a))
* **manifest.json:** add integration type ([9d5ed64](https://github.com/jpawlowski/hacs.integration_blueprint/commit/9d5ed64c444a484a2cda7be8db933bf281f1fab5))
* **schemas:** use inline YAML schema declarations ([2b7e1a1](https://github.com/jpawlowski/hacs.integration_blueprint/commit/2b7e1a1d7367067514e762911ec7dae594460d9a))
* **services:** improve service registration and add logging for missing config entries ([0c0bcb4](https://github.com/jpawlowski/hacs.integration_blueprint/commit/0c0bcb4e0e55bdc179d18dd7acc01bd95979e65f))
* **setup:** update symlink creation for external venv to use absolute path for reliability ([f4f8c30](https://github.com/jpawlowski/hacs.integration_blueprint/commit/f4f8c30a74b671d8daece9222d0585d840444abb))
* **translations:** replace plain URL with markdown link in config flow ([8bd713c](https://github.com/jpawlowski/hacs.integration_blueprint/commit/8bd713c70f156c886f438fa1d31174535ce09c8f))


### Performance

* **devcontainer:** move node_modules off workspace bind mount ([f32d778](https://github.com/jpawlowski/hacs.integration_blueprint/commit/f32d77800eaee64f4a683539d1853ecd187f088d))
