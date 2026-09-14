# Hermes Azure Speech Provider

This repository contains the Azure Speech STT/TTS provider for Hermes-based integrations.

## Project contents

- [Azure Speech Provider](Azure%20Speech%20Provider) — main Python package and implementation
- [Azure Speech Provider/README.md](Azure%20Speech%20Provider/README.md) — package documentation and usage guide
- [Azure Speech Provider/docs](Azure%20Speech%20Provider/docs) — architecture, deployment, migration, and runbooks
- [Azure Speech Provider/tests](Azure%20Speech%20Provider/tests) — automated verification suite

## Overview

The package provides reusable Azure Speech components for:

- speech-to-text transcription
- text-to-speech synthesis
- SSML generation for Azure voices
- environment-based configuration
- Hermes provider wrappers and plugin registration

## Quick start

```bash
cd "Azure Speech Provider"
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e ".[dev]"
.\.venv\Scripts\python.exe -m pytest -q
```

## Repository status

This project is published as a GitHub repository and includes a basic CI workflow for linting, testing, and release packaging.

## License

MIT
