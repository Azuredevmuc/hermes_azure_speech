# Hermes Live Test Runbook

This runbook covers the first live validation of the Azure Speech provider inside a Hermes AI Agent environment.

---

## 1. Preconditions

Before the first live test, confirm:

- Hermes agent runtime is installed and running
- the Python environment is the same one used by Hermes
- Azure Speech credentials are valid
- an audio input file exists for STT testing
- the output directory is writable

---

## 2. Environment setup

Create the Hermes-local `.env` template first:

```powershell
pwsh -File .\scripts\bootstrap_hermes_azure_env.ps1 -HermesHome "C:\AI\Hermes\home"
```

Then set the required Azure values:

```bash
AZURE_SPEECH_KEY="<your-azure-speech-key>"
AZURE_SPEECH_REGION="westeurope"
AZURE_SPEECH_VOICE="de-DE-KatjaNeural"
AZURE_SPEECH_LANGUAGE="de-DE"
```

If you use a local `.env` file, make sure it is loaded from the Hermes working directory or pass the explicit path through `AzureSpeechConfig.from_env()`.

---

## 3. Package installation

Install the provider into the same Python environment used by Hermes before running the first live test.

```bash
uv pip install -e "C:/AI/Hermes Extensions/Azure Speech Provider"
```

If Hermes runs in its own virtual environment, install it there instead of into a different global Python installation.

---

## 4. Local smoke tests

### STT test

```python
from provider import AzureSpeechConfig, HermesSTTProvider

config = AzureSpeechConfig.from_env()
provider = HermesSTTProvider(config)
text = provider.transcribe("sample.wav")
print(text)
```

### TTS test

```python
from provider import AzureSpeechConfig, HermesTTSProvider

config = AzureSpeechConfig.from_env()
provider = HermesTTSProvider(config)
provider.synthesize("Testausgabe des Hermes Azure Speech Providers.", "demo_output.mp3")
print("done")
```

---

## 5. Hermes-facing validation flow

Use this validation path in order:

1. verify config loads correctly
2. verify `config.yaml` points to `hermes-azure-speech-tts` and `hermes-azure-speech-stt`
2. transcribe a sample audio file
3. check that the transcript text is non-empty
4. pass the transcript into Hermes logic
5. synthesize a short response into MP3
6. confirm the file is written successfully

---

## 6. Expected outcomes

The live test passes when all of the following are true:

- Azure Speech key is accepted
- STT returns a valid transcript
- TTS produces a valid output file
- no raw secret appears in logs or exceptions
- the Hermes workflow accepts the provider output without a crash

---

## 7. Failure checks

If the first live validation fails, check:

- Azure key and region are correct
- the voice name exists in the selected Azure region
- the input audio file is valid
- the output directory is writable
- the Hermes process uses the same Python environment

---

## 8. Operational checkpoints

Before declaring the integration ready, verify:

- logs are secret-safe
- the provider is being used as the speech backend layer
- no hardcoded credentials are present in code or config
- the bridge path is stable and documented

---

## 9. Go-live recommendation

Only proceed to live deployment when:

- STT and TTS smoke tests pass
- the provider is correctly loaded in Hermes
- no configuration or runtime exceptions remain
- the Azure Speech backend is working in a real flow

This marks the first “real” Hermes usage milestone for the provider.
