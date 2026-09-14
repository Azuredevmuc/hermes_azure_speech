from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

from .config import AzureSpeechConfig
from .stt import AzureSpeechSTT, AzureSpeechSTTOptions
from .tts import AzureSpeechTTS, AzureSpeechTTSOptions


class HermesSpeechProvider(ABC):
    """Base contract for Hermes speech integrations."""

    provider_name = "azure_speech"
    capability = "speech"
    runtime = "python"

    def __init__(self, config: AzureSpeechConfig) -> None:
        self.config = config

    @classmethod
    def from_env(cls) -> "HermesSpeechProvider":
        return cls(AzureSpeechConfig.from_env())

    @classmethod
    def validate_config(cls, config: Any) -> bool:
        if config is None:
            return False
        speech_key = getattr(config, "speech_key", "")
        speech_region = getattr(config, "speech_region", "")
        return bool(speech_key and speech_region)

    def describe(self) -> dict[str, str]:
        return {
            "provider_name": self.provider_name,
            "capability": self.capability,
            "runtime": self.runtime,
            "capabilities": [self.capability],
        }

    def supports(self, capability: str) -> bool:
        return capability.strip().lower() == self.capability

    @abstractmethod
    def run(self, *args: Any, **kwargs: Any) -> Any:
        """Execute the provider action for Hermes."""


class HermesTTSProvider(HermesSpeechProvider):
    """Hermes-facing TTS provider wrapper for Azure Speech."""

    capability = "tts"

    @classmethod
    def validate_config(cls, config: Any) -> bool:
        if not super().validate_config(config):
            return False
        return bool(getattr(config, "voice", "") or getattr(config, "language", ""))

    def synthesize(self, text: str, output_path: str | Path, **kwargs: Any) -> Path:
        if not self.validate_config(self.config):
            raise ValueError("AzureSpeechConfig is invalid for Hermes TTS use.")

        options = kwargs.pop("options", None)
        if options is None:
            options = AzureSpeechTTSOptions(
                voice=kwargs.pop("voice", None),
                language=kwargs.pop("language", None),
                rate=kwargs.pop("rate", "0%"),
                pitch=kwargs.pop("pitch", "0%"),
                volume=kwargs.pop("volume", "0%"),
                style=kwargs.pop("style", None),
                style_degree=kwargs.pop("style_degree", None),
                use_ssml=kwargs.pop("use_ssml", True),
                output_format=kwargs.pop("output_format", None),
                timeout_seconds=kwargs.pop("timeout_seconds", 180),
            )

        return AzureSpeechTTS(config=self.config).synthesize_to_file(
            text,
            output_path,
            options=options,
        )

    def run(self, *args: Any, **kwargs: Any) -> Path:
        return self.synthesize(*args, **kwargs)


class HermesSTTProvider(HermesSpeechProvider):
    """Hermes-facing STT provider wrapper for Azure Speech."""

    capability = "stt"

    @classmethod
    def validate_config(cls, config: Any) -> bool:
        if not super().validate_config(config):
            return False
        return bool(getattr(config, "language", "") or getattr(config, "voice", ""))

    def transcribe(self, input_path: str | Path, **kwargs: Any) -> str:
        if not self.validate_config(self.config):
            raise ValueError("AzureSpeechConfig is invalid for Hermes STT use.")

        options = kwargs.pop("options", None)
        if options is None:
            options = AzureSpeechSTTOptions(
                language=kwargs.pop("language", None),
                timeout_seconds=kwargs.pop("timeout_seconds", 180),
                treat_empty_as_error=kwargs.pop("treat_empty_as_error", True),
            )

        return AzureSpeechSTT(config=self.config).transcribe_file(
            input_path,
            options=options,
        )

    def run(self, *args: Any, **kwargs: Any) -> str:
        return self.transcribe(*args, **kwargs)
