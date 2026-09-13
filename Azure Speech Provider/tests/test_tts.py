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
            self.speech_synthesis_voice_name = ""

        def set_speech_synthesis_output_format(self, fmt):
            self.output_format = fmt

    class FakeAudioOutputConfig:
        def __init__(self, filename: str):
            self.filename = filename

    class FakeAudioConfig:
        def __init__(self, filename: str):
            self.filename = filename

    class FakeSynthesisResult:
        def __init__(self, reason):
            self.reason = reason
            self.cancellation_details = types.SimpleNamespace(
                reason="unknown",
                error_details="",
            )

    class FakeSpeechSynthesizer:
        last_payload = None

        def __init__(self, speech_config, audio_config):
            self.speech_config = speech_config
            self.audio_config = audio_config
            self.last_timeout = None
            FakeSpeechSynthesizer.last_payload = None

        def speak_ssml_async(self, payload):
            FakeSpeechSynthesizer.last_payload = payload
            return self

        def speak_text_async(self, text):
            FakeSpeechSynthesizer.last_payload = text
            return self

        def get(self, timeout=None):
            self.last_timeout = timeout
            Path(self.audio_config.filename).write_text("audio-bytes", encoding="utf-8")
            return FakeSynthesisResult("completed")

    class FakeSpeechRecognizer:
        def __init__(self, speech_config, audio_config):
            self.speech_config = speech_config
            self.audio_config = audio_config

        def recognize_once_async(self):
            return self

        def get(self):
            return FakeSynthesisResult("recognized")

    fake_speech_module.SpeechSynthesisOutputFormat = types.SimpleNamespace(
        Audio24Khz160KBitRateMonoMp3="mp3",
        Riff24Khz16BitMonoPcm="wav",
    )
    fake_speech_module.ResultReason = types.SimpleNamespace(
        SynthesizingAudioCompleted="completed",
        Canceled="canceled",
        RecognizedSpeech="recognized",
        NoMatch="no-match",
    )
    fake_speech_module.SpeechConfig = FakeSpeechConfig
    fake_speech_module.audio = types.SimpleNamespace(
        AudioOutputConfig=FakeAudioOutputConfig,
        AudioConfig=FakeAudioConfig,
    )
    fake_speech_module.SpeechSynthesizer = FakeSpeechSynthesizer
    fake_speech_module.SpeechRecognizer = FakeSpeechRecognizer
    fake_speech_module.SpeechSynthesisResult = FakeSynthesisResult

    fake_azure.cognitiveservices = fake_cognitiveservices
    fake_cognitiveservices.speech = fake_speech_module

    monkeypatch.setitem(sys.modules, "azure", fake_azure)
    monkeypatch.setitem(sys.modules, "azure.cognitiveservices", fake_cognitiveservices)
    monkeypatch.setitem(sys.modules, "azure.cognitiveservices.speech", fake_speech_module)

    import provider.config as config_module
    import provider.tts as tts_module

    importlib.reload(config_module)
    importlib.reload(tts_module)

    return tts_module


def test_synthesize_to_file_writes_output_and_uses_ssml(fake_speech_sdk, tmp_path):
    config = fake_speech_sdk.AzureSpeechConfig(
        speech_key="key",
        speech_region="westeurope",
        voice="de-DE-KatjaNeural",
        language="de-DE",
    )
    engine = fake_speech_sdk.AzureSpeechTTS(config=config)

    output_path = tmp_path / "hello.mp3"
    result = engine.synthesize_to_file("Hallo Welt", output_path)

    assert result == output_path
    assert output_path.exists()
    assert output_path.read_text(encoding="utf-8") == "audio-bytes"


def test_synthesize_to_file_accepts_format_without_leading_dot(fake_speech_sdk, tmp_path):
    config = fake_speech_sdk.AzureSpeechConfig(
        speech_key="key",
        speech_region="westeurope",
        voice="de-DE-KatjaNeural",
        language="de-DE",
    )
    engine = fake_speech_sdk.AzureSpeechTTS(config=config)

    output_path = tmp_path / "hello.mp3"
    result = engine.synthesize_to_file(
        "Hallo Welt",
        output_path,
        options=fake_speech_sdk.AzureSpeechTTSOptions(output_format="mp3"),
    )

    assert result == output_path
    assert output_path.exists()


def test_synthesize_to_file_uses_configured_timeout(fake_speech_sdk, tmp_path):
    config = fake_speech_sdk.AzureSpeechConfig(
        speech_key="key",
        speech_region="westeurope",
        voice="de-DE-KatjaNeural",
        language="de-DE",
    )
    engine = fake_speech_sdk.AzureSpeechTTS(config=config)

    output_path = tmp_path / "hello.mp3"
    result = engine.synthesize_to_file(
        "Hallo Welt",
        output_path,
        options=fake_speech_sdk.AzureSpeechTTSOptions(timeout_seconds=12),
    )

    assert result == output_path
    assert output_path.exists()


def test_synthesize_to_file_uses_positional_timeout_for_sdk_future(monkeypatch, fake_speech_sdk, tmp_path):
    config = fake_speech_sdk.AzureSpeechConfig(
        speech_key="key",
        speech_region="westeurope",
        voice="de-DE-KatjaNeural",
        language="de-DE",
    )
    engine = fake_speech_sdk.AzureSpeechTTS(config=config)

    output_path = tmp_path / "hello.mp3"
    captured: dict[str, object] = {}

    class StrictFuture:
        def __init__(self, audio_filename: str):
            self.audio_filename = audio_filename

        def get(self, *args, **kwargs):
            captured["args"] = args
            captured["kwargs"] = kwargs
            if args or kwargs:
                raise TypeError("no arguments supported")
            Path(self.audio_filename).write_text("audio-bytes", encoding="utf-8")
            return fake_speech_sdk.speechsdk.SpeechSynthesisResult("completed")

    class StrictSynthesizer:
        def __init__(self, speech_config, audio_config):
            self.speech_config = speech_config
            self.audio_config = audio_config

        def speak_ssml_async(self, payload):
            return StrictFuture(self.audio_config.filename)

        def speak_text_async(self, text):
            return StrictFuture(self.audio_config.filename)

    monkeypatch.setattr(fake_speech_sdk.speechsdk, "SpeechSynthesizer", StrictSynthesizer)

    result = engine.synthesize_to_file(
        "Hallo Welt",
        output_path,
        options=fake_speech_sdk.AzureSpeechTTSOptions(timeout_seconds=12),
    )

    assert result == output_path
    assert captured["args"] == ()
    assert captured["kwargs"] == {}


def test_synthesize_to_file_times_out_when_sdk_future_blocks(monkeypatch, fake_speech_sdk, tmp_path):
    config = fake_speech_sdk.AzureSpeechConfig(
        speech_key="key",
        speech_region="westeurope",
        voice="de-DE-KatjaNeural",
        language="de-DE",
    )
    engine = fake_speech_sdk.AzureSpeechTTS(config=config)

    output_path = tmp_path / "hello.mp3"

    class BlockingFuture:
        def get(self):
            import threading

            threading.Event().wait(0.2)
            return None

    class BlockingSynthesizer:
        def __init__(self, speech_config, audio_config):
            self.speech_config = speech_config
            self.audio_config = audio_config

        def speak_ssml_async(self, payload):
            return BlockingFuture()

        def speak_text_async(self, text):
            return BlockingFuture()

    monkeypatch.setattr(fake_speech_sdk.speechsdk, "SpeechSynthesizer", BlockingSynthesizer)

    with pytest.raises(fake_speech_sdk.AzureSpeechTimeoutError):
        engine.synthesize_to_file(
            "Hallo Welt",
            output_path,
            options=fake_speech_sdk.AzureSpeechTTSOptions(timeout_seconds=0),
        )


def test_synthesize_to_file_rejects_empty_text(fake_speech_sdk):
    config = fake_speech_sdk.AzureSpeechConfig(
        speech_key="key",
        speech_region="westeurope",
        voice="de-DE-KatjaNeural",
        language="de-DE",
    )
    engine = fake_speech_sdk.AzureSpeechTTS(config=config)

    with pytest.raises(fake_speech_sdk.AzureSpeechEmptyTextError):
        engine.synthesize_to_file("   ", Path("ignored.mp3"))


def test_synthesize_to_file_removes_partial_output_on_failure(monkeypatch, fake_speech_sdk, tmp_path):
    config = fake_speech_sdk.AzureSpeechConfig(
        speech_key="key",
        speech_region="westeurope",
        voice="de-DE-KatjaNeural",
        language="de-DE",
    )
    engine = fake_speech_sdk.AzureSpeechTTS(config=config)
    output_path = tmp_path / "partial.mp3"

    class FailingSynthesizer:
        def speak_ssml_async(self, payload):
            return self

        def get(self, timeout=None):
            output_path.write_text("partial-data", encoding="utf-8")
            raise RuntimeError("boom")

    monkeypatch.setattr(
        fake_speech_sdk.speechsdk.SpeechSynthesizer,
        "speak_ssml_async",
        FailingSynthesizer.speak_ssml_async,
    )
    monkeypatch.setattr(
        fake_speech_sdk.speechsdk.SpeechSynthesizer,
        "get",
        None,
    )

    with pytest.raises(fake_speech_sdk.AzureSpeechSynthesisError):
        engine.synthesize_to_file("Hallo Welt", output_path)

    assert not output_path.exists()


def test_missing_speech_sdk_raises_dependency_error(monkeypatch):
    import provider.tts as tts_module

    monkeypatch.setattr(tts_module, "speechsdk", None)

    engine = tts_module.AzureSpeechTTS(
        config=tts_module.AzureSpeechConfig(
            speech_key="key",
            speech_region="westeurope",
            voice="de-DE-KatjaNeural",
            language="de-DE",
        )
    )

    with pytest.raises(tts_module.AzureSpeechDependencyError):
        engine.synthesize_to_file("Hallo Welt", "ignored.mp3")
