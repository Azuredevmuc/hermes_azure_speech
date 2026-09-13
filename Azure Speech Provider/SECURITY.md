# Security Policy

## Supported versions

The project is currently in active development. Security fixes are prioritized for the current main branch and the latest release tag.

## Reporting a vulnerability

Please report security issues privately and do not disclose them in public issues or pull requests.

Use one of the following channels:

- open a private security advisory in the repository host
- contact the maintainer directly using a private channel
- send a detailed report including reproduction steps, impact, and affected versions

## Security expectations

- Never commit real Azure Speech keys or production credentials
- Use environment variables or a local `.env` file only for local development
- Treat all logs as sensitive output and ensure they do not contain raw secrets
- Run dependency audits before releases
- Review all changes affecting config loading, secret handling, or network I/O

## Secrets handling

This project expects Azure credentials through environment variables such as:

- `AZURE_SPEECH_KEY`
- `AZURE_SPEECH_REGION`

These values must not be printed in logs, exceptions, tracebacks, or CLI output.

## Dependency hygiene

Before publishing a release, validate:

- `python -m pytest`
- `python -m pip_audit`
- no known critical or high vulnerabilities in the dependency set

## Responsible disclosure

We appreciate responsible disclosure and will do our best to acknowledge and address security issues quickly.
