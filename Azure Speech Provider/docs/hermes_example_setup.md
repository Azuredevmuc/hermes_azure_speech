# Hermes Example Setup

This is a minimal example configuration for wiring the Azure Speech provider into a Hermes environment.

---

## 1. Install the package in the Hermes runtime environment

Install the package into the same Python environment that runs Hermes. This is the recommended setup because Hermes must resolve the provider from the same interpreter context it uses at runtime.

From a terminal in the Hermes runtime environment:

```bash
uv pip install -e "C:/AI/Hermes Extensions/Azure Speech Provider"
```

If Hermes uses a dedicated virtual environment, install the package there instead of a different global Python installation.

Then enable the plugin entrypoint in Hermes config:

```yaml
plugins:
	enabled:
		- azure-speech
```

---

## 2. Create a local environment file

Recommended Variant A:

```powershell
pwsh -File .\scripts\bootstrap_hermes_azure_env.ps1 -HermesHome "C:\AI\Hermes\home"
```

That creates or extends `C:\AI\Hermes\home\.env` with placeholders and defaults. Then fill in the blank Azure values locally.

The resulting file should contain:

```bash
AZURE_SPEECH_KEY="your-azure-key"
AZURE_SPEECH_REGION="westeurope"
AZURE_SPEECH_VOICE="de-DE-KatjaNeural"
AZURE_SPEECH_LANGUAGE="de-DE"
```

You can also copy the repo template:

```bash
copy "C:/AI/Hermes Extensions/Azure Speech Provider/.env.example" .env
```

---

## 3. Minimal Python integration example

```python
from provider import HermesAzureSpeechAdapter

providers = HermesAzureSpeechAdapter.load_from_env()
stt = providers["stt"]
tts = providers["tts"]

print(HermesAzureSpeechAdapter.describe_from_env())

transcript = stt.transcribe("input.wav")
print("Transcript:", transcript)

tts.synthesize("Hallo aus Hermes mit Azure Speech.", "response.mp3")
print("Audio written to response.mp3")
```

This is the preferred in-process integration pattern between Hermes and Azure Speech.

---

## 4. Legacy CLI flow

### Speech-to-text

```bash
python "C:/AI/Hermes Extensions/Azure Speech Provider/scripts/azure_speech_stt.py" --input input.wav --output transcript.txt
```

### Text-to-speech

```bash
python "C:/AI/Hermes Extensions/Azure Speech Provider/scripts/azure_speech_tts.py" --input prompt.txt --output response.mp3
```

These commands are kept only for older command-based Hermes setups.

---

## 5. Hermes config example

Use the plugin provider id in `config.yaml`:

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

This keeps Hermes on the Python plugin provider path for Azure Speech.

---

## 6. Legacy command fallback

If you intentionally stay on the command-provider path, use the installed commands instead of repo-local scripts:

```yaml
tts:
	provider: azure-speech-tts
	use_gateway: false
	providers:
		azure-speech-tts:
			type: command
			command: hermes-azure-speech-tts --input {input_path} --output {output_path}
			output_format: mp3
			timeout: 180

stt:
	enabled: true
	provider: azure-speech-stt
	use_gateway: false
	providers:
		azure-speech-stt:
			type: command
			command: hermes-azure-speech-stt --input {input_path} --output {output_path}
			format: txt
			timeout: 180
```

---

## 7. Recommended Hermes usage pattern

Use this package as a provider layer:

- Hermes decides the workflow
- the provider handles Azure STT/TTS
- an importable adapter or Python service calls the provider
- the service returns text or file output to Hermes

This is the correct architectural fit for Hermes AI Agent, not a generic “skill” implementation.

---

## 8. Security notes

- never hardcode Azure keys in source files
- keep secrets in environment variables or `.env`
- never print raw config values in logs
- do not commit real credentials to git

---

## 9. Typical runtime flow

```text
User speaks -> Hermes -> STT provider -> transcript -> Hermes logic -> TTS provider -> audio file -> playback
```

This keeps the Azure Speech logic cleanly separated from the speech orchestration layer.
