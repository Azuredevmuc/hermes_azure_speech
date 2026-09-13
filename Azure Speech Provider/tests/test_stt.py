import importlib
import sys
import types
from pathlib import Path

import pytest


@pytest.fixture
def fake_speech_sdk(monkeypatch):
    fake_azure = types.ModuleType("azure")
    fake_cognitiveservices = types.ModuleType("azure.cognitiveservices")
    fake_speech_module = types.ModuleType("azure.cognitiveservices.speech")

    class FakeSpeechConfig:
        def __init__(self, subscription: str, region: str):
            self.subscription = subscription
            self.region = region
            self.speech_recognition_language = ""

    class FakeAudioConfig:
        def __init__(self, filename: str):
            self.filename = filename

    class FakeRecognitionResult:
        def __init__(self, reason, text=""):
            self.reason = reason
            self.text = text
            self.cancellation_details = types.SimpleNamespace(
                reason="unknown",
                error_details="",
            )

    class FakeSpeechRecognizer:
        def __init__(self, speech_config, audio_config):
            self.speech_config = speech_config
            self.audio_config = audio_config
            self.last_timeout = None

        def recognize_once_async(self):
            return self

        def get(self, timeout=None):
            self.last_timeout = timeout
            return FakeRecognitionResult("recognized", "Hallo von Azure")

    fake_speech_module.ResultReason = types.SimpleNamespace(
        RecognizedSpeech="recognized",
        NoMatch="no-match",
        Canceled="canceled",
    )
    fake_speech_module.SpeechConfig = FakeSpeechConfig
    fake_speech_module.audio = types.SimpleNamespace(AudioConfig=FakeAudioConfig)
    fake_speech_module.SpeechRecognizer = FakeSpeechRecognizer

    fake_azure.cognitiveservices = fake_cognitiveservices
    fake_cognitiveservices.speech = fake_speech_module

    monkeypatch.setitem(sys.modules, "azure", fake_azure)
    monkeypatch.setitem(sys.modules, "azure.cognitiveservices", fake_cognitiveservices)
    monkeypatch.setitem(sys.modules, "azure.cognitiveservices.speech", fake_speech_module)

    import provider.config as config_module
    import provider.stt as stt_module

    importlib.reload(config_module)
    importlib.reload(stt_module)

    return stt_module


def test_transcribe_file_returns_transcript(fake_speech_sdk, tmp_path):
    audio_path = tmp_path / "input.wav"
    audio_path.write_text("fake-audio", encoding="utf-8")

    config = fake_speech_sdk.AzureSpeechConfig(
        speech_key="key",
        speech_region="westeurope",
        voice="de-DE-KatjaNeural",
        language="de-DE",
    )
    engine = fake_speech_sdk.AzureSpeechSTT(config=config)

    transcript = engine.transcribe_file(audio_path)

    assert transcript == "Hallo von Azure"


def test_transcribe_file_uses_configured_timeout(fake_speech_sdk, tmp_path):
    audio_path = tmp_path / "input.wav"
    audio_path.write_text("fake-audio", encoding="utf-8")

    config = fake_speech_sdk.AzureSpeechConfig(
        speech_key="key",
        speech_region="westeurope",
        voice="de-DE-KatjaNeural",
        language="de-DE",
    )
    engine = fake_speech_sdk.AzureSpeechSTT(config=config)

    result = engine.transcribe_file(
        audio_path,
        options=fake_speech_sdk.AzureSpeechSTTOptions(timeout_seconds=12),
    )

    assert result == "Hallo von Azure"


def test_transcribe_file_uses_positional_timeout_for_sdk_future(monkeypatch, fake_speech_sdk, tmp_path):
    audio_path = tmp_path / "input.wav"
    audio_path.write_text("fake-audio", encoding="utf-8")

    config = fake_speech_sdk.AzureSpeechConfig(
        speech_key="key",
        speech_region="westeurope",
        voice="de-DE-KatjaNeural",
        language="de-DE",
    )
    engine = fake_speech_sdk.AzureSpeechSTT(config=config)

    captured: dict[str, object] = {}

    class StrictRecognitionResult:
        def __init__(self):
            self.reason = "recognized"
            self.text = "Hallo von Azure"
            self.cancellation_details = types.SimpleNamespace(
                reason="unknown",
                error_details="",
            )

    class StrictFuture:
        def get(self, *args, **kwargs):
            captured["args"] = args
            captured["kwargs"] = kwargs
            if args or kwargs:
                raise TypeError("no arguments supported")
            return StrictRecognitionResult()

    class StrictRecognizer:
        def __init__(self, speech_config, audio_config):
            self.speech_config = speech_config
            self.audio_config = audio_config

        def recognize_once_async(self):
            return StrictFuture()

    monkeypatch.setattr(fake_speech_sdk.speechsdk, "SpeechRecognizer", StrictRecognizer)

    result = engine.transcribe_file(
        audio_path,
        options=fake_speech_sdk.AzureSpeechSTTOptions(timeout_seconds=12),
    )

    assert result == "Hallo von Azure"
    assert captured["args"] == ()
    assert captured["kwargs"] == {}


def test_transcribe_file_times_out_when_sdk_future_blocks(monkeypatch, fake_speech_sdk, tmp_path):
    audio_path = tmp_path / "input.wav"
    audio_path.write_text("fake-audio", encoding="utf-8")

    config = fake_speech_sdk.AzureSpeechConfig(
        speech_key="key",
        speech_region="westeurope",
        voice="de-DE-KatjaNeural",
        language="de-DE",
    )
    engine = fake_speech_sdk.AzureSpeechSTT(config=config)

    class BlockingFuture:
        def get(self):
            import threading

            threading.Event().wait(0.2)
            return None

    class BlockingRecognizer:
        def __init__(self, speech_config, audio_config):
            self.speech_config = speech_config
            self.audio_config = audio_config

        def recognize_once_async(self):
            return BlockingFuture()

    monkeypatch.setattr(fake_speech_sdk.speechsdk, "SpeechRecognizer", BlockingRecognizer)

    with pytest.raises(fake_speech_sdk.AzureSpeechTimeoutError):
        engine.transcribe_file(
            audio_path,
            options=fake_speech_sdk.AzureSpeechSTTOptions(timeout_seconds=0),
        )


def test_config_as_dict_redacts_speech_key():
    config = importlib.import_module("provider.config").AzureSpeechConfig(
        speech_key="super-secret-key",
        speech_region="westeurope",
        voice="de-DE-KatjaNeural",
        language="de-DE",
    )

    payload = config.as_dict()

    assert payload["speech_key"] == "***REDACTED***"
    assert payload["speech_region"] == "westeurope"


def test_transcribe_file_raises_for_missing_input(fake_speech_sdk):
    config = fake_speech_sdk.AzureSpeechConfig(
        speech_key="key",
        speech_region="westeurope",
        voice="de-DE-KatjaNeural",
        language="de-DE",
    )
    engine = fake_speech_sdk.AzureSpeechSTT(config=config)

    with pytest.raises(fake_speech_sdk.AzureSpeechAudioError):
        engine.transcribe_file(Path("does-not-exist.wav"))


def test_from_env_loads_default_dotenv_file(monkeypatch, tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text(
        "AZURE_SPEECH_KEY=dotenv-key\nAZURE_SPEECH_REGION=eastus\n"
        "AZURE_SPEECH_VOICE=en-US-JennyNeural\nAZURE_SPEECH_LANGUAGE=en-US\n",
        encoding="utf-8",
    )
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("AZURE_SPEECH_KEY", raising=False)
    monkeypatch.delenv("AZURE_SPEECH_REGION", raising=False)
    monkeypatch.delenv("AZURE_SPEECH_VOICE", raising=False)
    monkeypatch.delenv("AZURE_SPEECH_LANGUAGE", raising=False)

    config = importlib.import_module("provider.config").AzureSpeechConfig.from_env()

    assert config.speech_key == "dotenv-key"
    assert config.speech_region == "eastus"
    assert config.voice == "en-US-JennyNeural"
    assert config.language == "en-US"


def test_config_repr_redacts_secret_value():
    config = importlib.import_module("provider.config").AzureSpeechConfig(
        speech_key="super-secret-key",
        speech_region="westeurope",
        voice="de-DE-KatjaNeural",
        language="de-DE",
    )

    rendered = repr(config)

    assert "super-secret-key" not in rendered
    assert "***REDACTED***" in rendered


def test_hermes_provider_contract_is_exposed():
    provider_module = importlib.import_module("provider")

    assert hasattr(provider_module, "HermesSpeechProvider")
    assert hasattr(provider_module, "HermesTTSProvider")
    assert hasattr(provider_module, "HermesSTTProvider")

    cfg = provider_module.AzureSpeechConfig(
        speech_key="key",
        speech_region="westeurope",
        voice="de-DE-KatjaNeural",
        language="de-DE",
    )

    assert provider_module.HermesTTSProvider.validate_config(cfg) is True
    assert provider_module.HermesSTTProvider.validate_config(cfg) is True


def test_hermes_provider_contract_supports_env_bootstrap_and_metadata(monkeypatch):
    provider_module = importlib.import_module("provider")

    monkeypatch.setenv("AZURE_SPEECH_KEY", "key")
    monkeypatch.setenv("AZURE_SPEECH_REGION", "westeurope")
    monkeypatch.setenv("AZURE_SPEECH_VOICE", "de-DE-KatjaNeural")
    monkeypatch.setenv("AZURE_SPEECH_LANGUAGE", "de-DE")

    tts = provider_module.HermesTTSProvider.from_env()
    stt = provider_module.HermesSTTProvider.from_env()

    assert tts.describe()["provider_name"] == "azure_speech"
    assert tts.describe()["capability"] == "tts"
    assert tts.describe()["runtime"] == "python"
    assert tts.describe()["capabilities"] == ["tts"]
    assert stt.describe()["provider_name"] == "azure_speech"
    assert stt.describe()["capability"] == "stt"
    assert stt.describe()["runtime"] == "python"
    assert stt.describe()["capabilities"] == ["stt"]
    assert tts.config.speech_region == "westeurope"
    assert stt.config.language == "de-DE"


def test_provider_module_exposes_importable_hermes_adapter(monkeypatch):
    provider_module = importlib.import_module("provider")

    monkeypatch.setenv("AZURE_SPEECH_KEY", "key")
    monkeypatch.setenv("AZURE_SPEECH_REGION", "westeurope")
    monkeypatch.setenv("AZURE_SPEECH_VOICE", "de-DE-KatjaNeural")
    monkeypatch.setenv("AZURE_SPEECH_LANGUAGE", "de-DE")

    adapter = provider_module.HermesAzureSpeechAdapter
    providers = adapter.load_from_env()

    assert set(providers) == {"stt", "tts"}
    assert providers["tts"].supports("tts") is True
    assert providers["stt"].supports("stt") is True
    assert adapter.describe_from_env() == {
        "provider_name": "azure_speech",
        "runtime": "python",
        "capabilities": ["stt", "tts"],
    }


def test_hermes_provider_contract_exposes_capabilities():
    provider_module = importlib.import_module("provider")

    cfg = provider_module.AzureSpeechConfig(
        speech_key="key",
        speech_region="westeurope",
        voice="de-DE-KatjaNeural",
        language="de-DE",
    )

    tts = provider_module.HermesTTSProvider(cfg)
    stt = provider_module.HermesSTTProvider(cfg)

    assert tts.provider_name == "azure_speech"
    assert tts.supports("tts") is True
    assert tts.supports("stt") is False
    assert stt.supports("stt") is True
    assert stt.supports("tts") is False

    assert "capabilities" in tts.describe()
    assert "tts" in tts.describe()["capabilities"]
    assert "stt" in stt.describe()["capabilities"]
