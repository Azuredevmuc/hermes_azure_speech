# Changelog

All notable changes to the Hermes Azure Speech Provider will be documented in this file.

## Unreleased

- no unreleased changes yet

## 1.0.0

### Added
- public-ready project documentation
- secure configuration guidance
- contribution and security policies
- environment example template
- Hermes provider contract layer for speech integration
- Hermes plugin entrypoint for TTS and STT registration
- native repo-plugin files (`plugin.yaml` and root `__init__.py`)
- Windows bootstrap script for local Hermes `.env` initialization
- installed CLI entrypoints for Azure Speech compatibility flows
- regression tests for versioning, plugin registration, repo-plugin layout, and Azure SDK future handling

### Changed
- improved secret redaction and `.env` auto-discovery
- hardened runtime error handling and cleanup for TTS/STT paths
- clarified project framing as Hermes provider/extension backend
- normalized TTS output format handling for Hermes plugin calls
- replaced direct Azure future timeout arguments with external timeout control
- aligned local Hermes installation and repo-plugin deployment guidance

### Security
- added explicit guidance to avoid secret leakage in logs and examples
- dependency audit is part of release validation

## 0.1.0

- initial Azure Speech provider implementation for STT/TTS
- SSML generation support
- environment-based configuration and tests
