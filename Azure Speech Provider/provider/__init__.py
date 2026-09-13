# provider/__init__.py

"""
Azure Speech Provider for Hermes.

This package provides reusable Azure Speech implementations for

* Text-to-Speech (TTS)
* Speech-to-Text (STT)

designed for Hermes command providers and future plugin integrations.
"""

from importlib import import_module

__all__ = [
    "AzureSpeechConfig",
    "AzureSpeechTTS",
    "AzureSpeechTTSOptions",
    "synthesize_text_to_file",
    "AzureSpeechSTT",
    "AzureSpeechSTTOptions",
    "transcribe_file_to_text",
    "AzureSSMLBuilder",
    "SSMLSettings",
    "build_ssml",
    "HermesSpeechProvider",
    "HermesTTSProvider",
    "HermesSTTProvider",
    "HermesAzureSpeechAdapter",
    "AzureTTSProvider",
    "AzureSTTProvider",
    "AzureTranscriptionProvider",
    "register",
    "VERSION",
    "__version__",
]


def __getattr__(name: str):
    """Lazily resolve public symbols so optional Azure dependencies do not break package import."""
    if name == "AzureSpeechConfig":
        return import_module(".config", __name__).AzureSpeechConfig
    if name == "AzureSpeechTTS":
        return import_module(".tts", __name__).AzureSpeechTTS
    if name == "AzureSpeechTTSOptions":
        return import_module(".tts", __name__).AzureSpeechTTSOptions
    if name == "synthesize_text_to_file":
        return import_module(".tts", __name__).synthesize_text_to_file
    if name == "AzureSpeechSTT":
        return import_module(".stt", __name__).AzureSpeechSTT
    if name == "AzureSpeechSTTOptions":
        return import_module(".stt", __name__).AzureSpeechSTTOptions
    if name == "transcribe_file_to_text":
        return import_module(".stt", __name__).transcribe_file_to_text
    if name == "AzureSSMLBuilder":
        return import_module(".ssml", __name__).AzureSSMLBuilder
    if name == "SSMLSettings":
        return import_module(".ssml", __name__).SSMLSettings
    if name == "build_ssml":
        return import_module(".ssml", __name__).build_ssml
    if name == "HermesSpeechProvider":
        return import_module(".hermes", __name__).HermesSpeechProvider
    if name == "HermesTTSProvider":
        return import_module(".hermes", __name__).HermesTTSProvider
    if name == "HermesSTTProvider":
        return import_module(".hermes", __name__).HermesSTTProvider
    if name == "HermesAzureSpeechAdapter":
        return import_module(".adapter", __name__).HermesAzureSpeechAdapter
    if name == "AzureTTSProvider":
        return import_module(".plugin", __name__).AzureTTSProvider
    if name == "AzureSTTProvider":
        return import_module(".plugin", __name__).AzureSTTProvider
    if name == "AzureTranscriptionProvider":
        return import_module(".plugin", __name__).AzureTranscriptionProvider
    if name == "register":
        return import_module(".plugin", __name__).register
    if name in {"VERSION", "__version__"}:
        return import_module(".version", __name__).__dict__[name]
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")