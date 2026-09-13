# Changelog

All notable changes to the Hermes Azure Speech Provider will be documented in this file.

## Unreleased

- no unreleased changes yet

## 0.1.0

### Added
- initial public Hermes Azure Speech plugin release
- Azure Speech TTS and STT provider registration for Hermes Agent
- `uv` package installation support and native repo-plugin installation support
- local Hermes `.env` bootstrap script for non-secret setup
- public documentation for installation, configuration, migration, deployment, and release readiness

### Changed
- standardized provider packaging, versioning, and plugin metadata
- aligned Hermes integration around the external plugin/provider model
- improved runtime robustness for Azure Speech TTS and STT execution

### Security
- secret-safe configuration handling and redaction guidance
- release validation includes dependency-audit expectations
