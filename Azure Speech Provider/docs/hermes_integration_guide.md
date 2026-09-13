# Hermes AI Agent Integration Guide

This project is designed to be used as a Hermes speech provider / extension backend, not as a generic skill.

The integration model is:

- Hermes manages the agent workflow and orchestration
- this package provides the Azure Speech backend for STT and TTS
- a small bridge layer or Python wrapper calls the provider logic
- optional `.env` or environment variables provide Azure credentials

---

## 1. What this package provides

This repository exposes reusable Python components for:

- Azure Speech configuration
- text-to-speech synthesis
- speech-to-text transcription
- SSML generation
- structured errors and clean runtime failure handling

The main entry points are:

- `AzureSpeechConfig`
- `AzureSpeechTTS`
- `AzureSpeechSTT`
- `HermesTTSProvider`
- `HermesSTTProvider`
- `AzureTTSProvider`
- `AzureTranscriptionProvider`

For Hermes bridge code, the wrapper classes are the preferred contract because they now support:

- `from_env()` for same-runtime bootstrap
- `describe()` for stable provider metadata
- `run()` for a uniform execution surface

For Hermes integration code that wants a single importable entrypoint, use `HermesAzureSpeechAdapter`.

---

## 2. Recommended Hermes integration model

For Hermes AI Agent, the current recommended pattern is:

1. install this package into the same Python environment as Hermes
2. load Azure credentials via environment variables or `.env`
3. enable the `azure-speech` plugin entrypoint in Hermes
4. call the provider layer from Hermes through the registered TTS and transcription providers
5. use TTS for agent responses and STT for spoken input

This is a provider-style integration rather than a skill-style automation bundle.

---

## 3. Installation in a Hermes environment

Install this package into the same Python environment that runs Hermes. This is the required setup for a production or local Hermes deployment.

This repository supports two installation styles:

1. `uv` package install into the Hermes runtime environment
2. native Hermes repo-plugin install via the included `plugin.yaml` and root `__init__.py`

From the same Python environment used by Hermes:

```bash
uv pip install -e /path/to/Azure Speech Provider
```

If you are in the project folder itself:

```bash
uv pip install -e .
```

If Hermes is running in a dedicated virtual environment, install the package there instead of using a different global Python installation.

The package dependencies are defined in the project metadata and include:

- `azure-cognitiveservices-speech`
- `python-dotenv`

The install also exposes two Hermes-facing commands in that environment:

- `hermes-azure-speech-tts`
- `hermes-azure-speech-stt`

It also exposes a Hermes plugin entrypoint:

- `azure-speech -> provider:register`

---

## 4. Required environment variables

Add these values to the Hermes runtime environment or a local `.env` file:

```bash
AZURE_SPEECH_KEY="your-azure-speech-key"
AZURE_SPEECH_REGION="westeurope"
AZURE_SPEECH_VOICE="de-DE-KatjaNeural"
AZURE_SPEECH_LANGUAGE="de-DE"
```

A ready template is included in the repository as `.env.example`.

For Hermes, the recommended Variant A bootstrap is this local script:

```powershell
pwsh -File .\scripts\bootstrap_hermes_azure_env.ps1 -HermesHome "C:\AI\Hermes\home"
```

It creates or extends `C:\AI\Hermes\home\.env` with placeholder keys and safe defaults, but does not write real secrets.

If you want to copy the repo template manually instead:

```bash
copy .env.example .env
```

Then fill in your real Azure values. Do not commit real secrets.

---

## 5. Quick usage example from Python

```python
from provider import AzureSpeechConfig, AzureSpeechSTT, AzureSpeechTTS

config = AzureSpeechConfig.from_env()

# Example: transcribe audio input
transcript = AzureSpeechSTT(config).transcribe_file("input.wav")
print(transcript)

# Example: synthesize response audio
AzureSpeechTTS(config).synthesize_to_file(
    "Hallo, ich bin der Hermes Azure Speech Provider.",
    "response.mp3",
)
```

This is the simplest integration path when Hermes calls Python code directly.

---

## 6. Hermes provider wrapper usage

The project also exposes a Hermes-facing contract layer:

```python
from provider import HermesTTSProvider, HermesSTTProvider

# TTS provider wrapper
handler_tts = HermesTTSProvider.from_env()
handler_tts.synthesize("Hallo Welt", "agent_response.mp3")

# STT provider wrapper
handler_stt = HermesSTTProvider.from_env()
text = handler_stt.transcribe("voice_input.wav")
print(text)

print(handler_tts.describe())
```

This is useful when Hermes needs a consistent provider API for speech features without binding itself to Azure SDK internals.

The `describe()` output is designed for bridge-side routing and should be treated as the stable metadata contract for local Hermes integrations.

---

## 7. Preferred import-based adapter

The repository exposes an importable adapter for Hermes-facing integrations:

```python
from provider import HermesAzureSpeechAdapter

providers = HermesAzureSpeechAdapter.load_from_env()
metadata = HermesAzureSpeechAdapter.describe_from_env()

tts = providers["tts"]
stt = providers["stt"]
```

Use this path when Hermes can load Python integrations directly. It avoids shelling out to external command wrappers and keeps speech integration inside the provider package.

---

## 8. Config changes required in Hermes

Hermes can load Azure Speech as a Python plugin provider when the plugin is enabled. For TTS, `get_setup_schema()` can supply picker metadata in `hermes tools` / `hermes setup`. For STT, setup metadata is exposed for forward compatibility while the main routing path remains `stt.provider: azure-speech`.

Recommended configuration:

```yaml
plugins:
    enabled:
        - azure-speech

tts:
    provider: azure-speech
    use_gateway: false

stt:
    enabled: true
    provider: azure-speech
    use_gateway: false
    azure-speech:
        language: de-DE
```

Changes relative to the older repo-local setup:

1. Install the package with `uv pip install -e ...` in the Hermes runtime environment.
2. Add `azure-speech` to `plugins.enabled` so Hermes imports the plugin entrypoint.
3. Set `tts.provider` to `azure-speech`.
4. Set `stt.provider` to `azure-speech`.
5. Keep the installed command names only as a fallback for command-provider mode.

---

## 9. Legacy command bridge compatibility

The repository includes CLI bridge scripts for direct use in a Hermes-hosted environment:

- `scripts/azure_speech_stt.py`
- `scripts/azure_speech_tts.py`

### STT bridge

```bash
python scripts/azure_speech_stt.py --input audio.wav --output transcript.txt
```

### TTS bridge

```bash
python scripts/azure_speech_tts.py --input prompt.txt --output response.mp3
```

These scripts automatically add the project root to the Python path and read the configured environment values.

These scripts and installed CLI commands are a backward-compatibility path for older command-based setups. They are not the preferred Hermes integration model for this repository now that the Python plugin providers exist.

---

## 10. Typical speech flow in Hermes

A practical Hermes workflow looks like this:

1. Hermes receives spoken input
2. the provider wrapper calls `AzureSpeechSTT` to convert audio to text
3. Hermes resolves the intent or command from the transcript
4. Hermes decides on a textual response
5. the provider wrapper calls `AzureSpeechTTS` to generate `.mp3` output
6. the audio file is played back to the user

Example chain:

```python
from provider import AzureSpeechConfig, HermesSTTProvider, HermesTTSProvider

config = AzureSpeechConfig.from_env()

stt = HermesSTTProvider(config)
tts = HermesTTSProvider(config)

transcript = stt.transcribe("user_input.wav")
# ... Hermes agent logic ...
response_text = "Ich habe deine Anfrage verarbeitet."
tts.synthesize(response_text, "response.mp3")
```

---

## 11. Integration advice for Hermes deployments

Use this package when:

- you want Azure Speech as a backend for Hermes voice features
- you want a reusable provider layer instead of a hardcoded skill
- you need clean config handling and testable STT/TTS logic

Do not use this as a generic “skill” if your goal is to add Azure speech backend capabilities to a Hermes runtime. Instead, treat it as a provider/extension layer.

---

## 12. Recommended operational setup

For a stable deployment:

- keep Azure credentials in environment variables, not in source code
- store local development values in `.env` only
- keep all log output secret-safe
- validate config before calling Azure Speech
- set explicit timeouts on STT/TTS operations
- handle missing dependency and cancellation cases explicitly

---

## 13. Troubleshooting

### Missing Azure SDK

If you see an import or dependency error:

```bash
python -m pip install azure-cognitiveservices-speech python-dotenv
```

### Missing environment variables

Check whether these are set:

```bash
echo %AZURE_SPEECH_KEY%
```

or on Unix-like systems:

```bash
echo $AZURE_SPEECH_KEY
```

### `.env` not loaded

Ensure you are running the Hermes process from the same working directory where `.env` is located or pass the explicit path to `AzureSpeechConfig.from_env()`.

### TTS output not created

Check:

- Azure credentials are valid
- the output path is writable
- the selected voice is available in the Azure region
- the text is not empty

---

## 14. Summary

This package is best used in Hermes as a speech provider backend:

- STT for speech input
- TTS for spoken responses
- config and error handling abstraction
- clean integration point for external Hermes orchestration

If you want to integrate it into a Hermes runtime, use the importable adapter or provider wrappers as the main boundary between Hermes and Azure Speech. Keep the CLI scripts only for legacy compatibility.
