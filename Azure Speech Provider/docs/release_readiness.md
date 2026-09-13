# Release Readiness and Maintenance Plan

## Goal

Prepare the Hermes Azure Speech Provider for a stable public release and maintain it with repeatable quality and security controls.

## Hermes Compliance Status

Current status for Hermes AI Agent:

- compliant as an external Hermes speech plugin package
- compliant as a Python TTS provider via `register_tts_provider(...)`
- compliant as a Python STT provider via `register_transcription_provider(...)`
- compliant for `uv`-based installation into the Hermes runtime environment
- not a built-in Hermes core provider
- not dynamically added as a selectable row in the current static TTS/STT setup picker lists

This distinction matters: the package is valid for Hermes' external plugin/provider model, but Hermes' current setup UI still chooses from a core-owned static voice-provider list.

---

## Phase 5 — Release, quality gates, and maintenance

### 1. Release Criteria

A release is allowed only if all of the following are true:

- all automated tests pass
- dependency audit has no critical or high findings
- no secrets are contained in the repository history or release artifacts
- installation from a clean environment works
- docs and examples are valid for a fresh user setup
- Hermes provider contract remains compatible with the current integration model
- documentation accurately states the current Hermes picker limitation

### 2. Required checks before every release

#### Functional checks
- `python -m pytest -q`
- example scripts run in a clean environment
- TTS and STT smoke tests pass with valid Azure credentials
- configuration validation errors remain explicit and secure

#### Security checks
- `python -m pip_audit`
- secret scan on repository content and release draft
- review of all changed configuration and network-related logic
- verification that no secret appears in logs, tracebacks, or examples

#### Packaging checks
- `python -m pip install -e .`
- metadata and README render correctly
- version is increased intentionally and documented in the changelog

---

## CI and automation recommendations

### Minimum CI pipeline

1. install dependencies
2. run linting with Ruff
3. run the full pytest suite
4. run `pip-audit`
5. build the package with `python -m build`
6. publish only if all checks are green

### Suggested checks

- Python versions: 3.10, 3.11, 3.12
- test jobs on Linux and Windows
- secret scan in CI
- branch protection for main
- review requirement before merge to release branches

---

## Versioning strategy

Use semantic versioning:

- MAJOR: breaking API or provider contract changes
- MINOR: backward-compatible capabilities and integration additions
- PATCH: bug fixes, documentation changes, and security updates

Every release must update:

- `CHANGELOG.md`
- version metadata in the package
- docs for compatibility changes

---

## Maintenance model

### Routine operations

- run dependency audit monthly
- run test suite on every change
- review Azure SDK updates for compatibility
- review Hermes integration compatibility when upstream changes occur

### Support expectations

- triage security issues privately
- maintain backward compatibility where practical
- document breaking changes clearly
- fix release-blocking issues before public release promotion

---

## Risk controls

### High-priority risks

- leaked Azure credentials
- hanging speech calls due to missing timeouts
- invalid configuration silently accepted
- partial output files left behind on failure
- ambiguous Hermes provider contract causing bad integration assumptions

### Mitigations

- secret redaction in config outputs
- explicit timeout handling in TTS/STT paths
- validation before use
- cleanup of temp and output files on failure
- clear provider wrapper contract for Hermes integration

---

## Final release gate

Before publishing, confirm:

- [ ] tests are green
- [ ] security audit is green
- [ ] config and secrets are redacted
- [ ] installation is reproducible
- [ ] docs are clean and user ready
- [ ] release notes are written
- [ ] version is tagged and traceable

Only then should the package be published as a public Hermes speech provider.
