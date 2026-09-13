# Hermes Deployment Checklist

This checklist is intended for a real Hermes AI Agent deployment using the Azure Speech provider package as a speech backend.

---

## 1. Prerequisites

Before deployment, confirm:

- Hermes runtime is installed and running
- Python environment is available for the Hermes process
- Azure Speech subscription exists
- Azure region and voice are valid for the selected deployment
- the target system has write access to output folders

## Compliance Note

This package is compliant with Hermes' external plugin/provider integration model, but Hermes' current `hermes setup tts` and related picker flows still use a static built-in provider list. Treat Azure Speech as a configured external provider, not as a built-in picker option.

---

## 2. Package installation

Install the provider in the same Python environment used by Hermes. This is a required prerequisite for a stable Hermes deployment.

```bash
python -m pip install --upgrade pip
python -m pip install -e "C:/AI/Hermes Extensions/Azure Speech Provider"
```

If the package is published to a package index, use the package install variant instead. In either case, the provider must be installed into the Hermes runtime environment, not into a different interpreter that Hermes does not use.

---

## 3. Environment configuration

Set the required environment variables in the Hermes runtime environment:

```bash
AZURE_SPEECH_KEY="<your-azure-speech-key>"
AZURE_SPEECH_REGION="westeurope"
AZURE_SPEECH_VOICE="de-DE-KatjaNeural"
AZURE_SPEECH_LANGUAGE="de-DE"
```

Use a local `.env` file only in development. For production, prefer direct environment injection.

---

## 4. Files to keep in the Hermes environment

Keep or mirror the following items:

- the provider package installation
- the importable provider surface from `provider/`
- a `.env` or environment injection file with Azure values
- writable output folders for generated audio/text files

Only keep the CLI bridge scripts when you must support a legacy command-based Hermes configuration.

---

## 5. Hermes integration pattern

The recommended usage pattern is:

- Hermes receives user voice input
- STT adapter or wrapper calls `AzureSpeechSTT`
- the transcript is passed to Hermes logic
- the response is converted with `AzureSpeechTTS`
- the generated audio is returned to the user

This approach keeps the Azure provider separate from the agent orchestration logic.

---

## 6. Validator before first live test

Confirm all of the following:

- `AzureSpeechConfig.from_env()` loads values successfully
- Azure Speech SDK is installed and importable
- `HermesSTTProvider.validate_config()` returns `True`
- `HermesTTSProvider.validate_config()` returns `True`
- test audio file is readable
- output folder is writable

---

## 7. Minimal smoke test

Run a quick TTS smoke test:

```python
from provider import AzureSpeechConfig, HermesTTSProvider

config = AzureSpeechConfig.from_env()
provider = HermesTTSProvider(config)
provider.synthesize("Testausgabe", "test_output.mp3")
```

Run a quick STT smoke test:

```python
from provider import AzureSpeechConfig, HermesSTTProvider

config = AzureSpeechConfig.from_env()
provider = HermesSTTProvider(config)
text = provider.transcribe("input.wav")
print(text)
```

---

## 8. Operational safeguards

Before running live speech workflows, confirm:

- secrets are never printed in logs
- no raw Azure key appears in generated output or exceptions
- timeouts are configured for STT/TTS calls
- temporary output files are cleaned on failure
- cancelled Azure operations are surfaced as explicit errors

---

## 9. Release gate for deployment

A Hermes deployment is ready only when:

- tests pass
- `pip-audit` has no critical issues
- config and secrets are validated
- a successful TTS and STT smoke test has been run
- the output/audio directory is writable and monitored

---

## 10. Final deployment recommendation

Use this package as a Hermes speech backend provider, not as a generic skill bundle.

The most stable deployment model is:

- Hermes orchestrates the conversation
- provider handles Azure Speech operations
- importable adapter or wrapper provides the access boundary
- environment config is secure and explicit

This keeps the deployment maintainable, testable, and production-friendly.

For operator expectations:

- plugin discovery and registration should work after installation and enablement
- `tts.provider: azure-speech` and `stt.provider: azure-speech` are the authoritative activation path
- absence from the static setup picker does not mean the plugin is misconfigured
