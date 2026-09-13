# Contributing

Thank you for helping improve the Hermes Azure Speech Provider.

## Development setup

```bash
python -m venv .venv
.
.venv\Scripts\activate
python -m pip install --upgrade pip
python -m pip install -e .[dev]
```

## Local configuration

Copy the example file and fill in your own values:

```bash
copy .env.example .env
```

Then configure your Azure values in `.env` before running local examples.

## Testing

Run the project tests before opening a pull request:

```bash
python -m pytest -q
```

Optional security check:

```bash
python -m pip_audit
```

## Pull request expectations

- keep changes focused and easy to review
- include or update tests for behavior changes
- avoid hardcoded secrets
- document new configuration values
- ensure no security regression is introduced
- keep the project framed as a Hermes provider/backend integration, not as a generic skill
- remove placeholder metadata or repository links before publishing

## Coding standards

- prefer explicit configuration validation
- keep secrets redacted in logs and repr output
- preserve the provider/extension-oriented architecture
- do not add test-only production APIs
