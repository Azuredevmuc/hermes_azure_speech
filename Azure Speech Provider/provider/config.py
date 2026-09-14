# provider/config.py
from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

try:
    from dotenv import find_dotenv, load_dotenv
except ImportError:  # optional dependency
    find_dotenv = None
    load_dotenv = None


DEFAULT_LANGUAGE = "de-DE"
DEFAULT_TTS_VOICE = "de-DE-KatjaNeural"


@dataclass(frozen=True)
class AzureSpeechConfig:
    speech_key: str
    speech_region: str
    voice: str = DEFAULT_TTS_VOICE
    language: str = DEFAULT_LANGUAGE

    def __repr__(self) -> str:
        return (
            "AzureSpeechConfig("
            "speech_key='***REDACTED***', "
            f"speech_region={self.speech_region!r}, "
            f"voice={self.voice!r}, "
            f"language={self.language!r})"
        )

    @classmethod
    def from_env(cls, dotenv_path: Optional[str | Path] = None) -> "AzureSpeechConfig":
        """
        Load Azure Speech settings from environment variables.
        Automatically loads a local `.env` file when present and also supports explicit paths.
        """
        if load_dotenv is not None:
            dotenv_file = str(dotenv_path) if dotenv_path is not None else None
            if dotenv_file is None and find_dotenv is not None:
                dotenv_file = find_dotenv(usecwd=True)
            if dotenv_file:
                load_dotenv(dotenv_path=dotenv_file, override=False)

        speech_key = os.getenv("AZURE_SPEECH_KEY", "").strip()
        speech_region = os.getenv("AZURE_SPEECH_REGION", "").strip()
        voice = os.getenv("AZURE_SPEECH_VOICE", DEFAULT_TTS_VOICE).strip()
        language = os.getenv("AZURE_SPEECH_LANGUAGE", DEFAULT_LANGUAGE).strip()

        if not speech_key:
            raise ValueError("AZURE_SPEECH_KEY is missing.")
        if not speech_region:
            raise ValueError("AZURE_SPEECH_REGION is missing.")

        return cls(
            speech_key=speech_key,
            speech_region=speech_region,
            voice=voice or DEFAULT_TTS_VOICE,
            language=language or DEFAULT_LANGUAGE,
        )

    @property
    def is_german(self) -> bool:
        return self.language.lower().startswith("de")

    @property
    def tts_voice(self) -> str:
        return self.voice

    @property
    def stt_language(self) -> str:
        return self.language

    def as_dict(self) -> dict[str, str]:
        return {
            "speech_key": "***REDACTED***",
            "speech_region": self.speech_region,
            "voice": self.voice,
            "language": self.language,
        }

    def as_dict_sensitive(self) -> dict[str, str]:
        """Return the full configuration, including the secret key for internal use only."""
        return {
            "speech_key": self.speech_key,
            "speech_region": self.speech_region,
            "voice": self.voice,
            "language": self.language,
        }