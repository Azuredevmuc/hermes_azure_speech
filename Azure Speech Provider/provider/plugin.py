from __future__ import annotations

from typing import Any

try:
    from agent.transcription_provider import TranscriptionProvider
except ImportError:  # pragma: no cover - Hermes runtime provides the real ABC.
    class TranscriptionProvider:  # type: ignore[no-redef]
        pass


try:
    from agent.tts_provider import TTSProvider
except ImportError:  # pragma: no cover - Hermes runtime provides the real ABC.
    class TTSProvider:  # type: ignore[no-redef]
        pass


from .config import AzureSpeechConfig
from .exceptions import AzureSpeechError
from .stt import AzureSpeechSTT, AzureSpeechSTTOptions
from .tts import AzureSpeechTTS, AzureSpeechTTSOptions


def _speed_to_rate(speed: Any) -> str:
    try:
        value = float(speed)
    except (TypeError, ValueError):
        return "0%"

    percentage = int(round((value - 1.0) * 100))
    if percentage >= 0:
        return f"+{percentage}%"
    return f"{percentage}%"


class AzureTTSProvider(TTSProvider):
    @property
    def name(self) -> str:
        return "azure-speech"

    @property
    def display_name(self) -> str:
        return "Microsoft Azure Speech"

    @property
    def voice_compatible(self) -> bool:
        return False

    def is_available(self) -> bool:
        try:
            AzureSpeechConfig.from_env()
        except Exception:
            return False
        return True

    def get_setup_schema(self) -> dict[str, Any]:
        return {
            "name": "Microsoft Azure Speech",
            "badge": "paid",
            "tag": "Azure Cognitive Services Speech",
            "env_vars": [
                {
                    "key": "AZURE_SPEECH_KEY",
                    "prompt": "Azure Speech API key",
                    "url": "https://portal.azure.com/",
                },
                {
                    "key": "AZURE_SPEECH_REGION",
                    "prompt": "Azure Speech region",
                },
                {
                    "key": "AZURE_SPEECH_VOICE",
                    "prompt": "Azure Speech voice",
                },
                {
                    "key": "AZURE_SPEECH_LANGUAGE",
                    "prompt": "Azure Speech language",
                },
            ],
        }

    def synthesize(
        self,
        text: str,
        output_path: str,
        *,
        voice: str | None = None,
        model: str | None = None,
        speed: Any = None,
        format: str = "mp3",
        **extra: Any,
    ) -> str:
        del model
        config = AzureSpeechConfig.from_env()
        options = AzureSpeechTTSOptions(
            voice=voice,
            language=extra.get("language"),
            rate=_speed_to_rate(speed),
            pitch=extra.get("pitch", "0%"),
            volume=extra.get("volume", "0%"),
            style=extra.get("style"),
            style_degree=extra.get("style_degree"),
            use_ssml=extra.get("use_ssml", True),
            output_format=format,
            timeout_seconds=int(extra.get("timeout_seconds", 180)),
        )
        return str(AzureSpeechTTS(config).synthesize_to_file(text, output_path, options=options))

    def warm(self) -> None:
        return None

    def release(self) -> None:
        return None


class AzureTranscriptionProvider(TranscriptionProvider):
    @property
    def name(self) -> str:
        return "azure-speech"

    @property
    def display_name(self) -> str:
        return "Microsoft Azure Speech"

    def is_available(self) -> bool:
        try:
            AzureSpeechConfig.from_env()
        except Exception:
            return False
        return True

    def get_setup_schema(self) -> dict[str, Any]:
        return {
            "name": "Microsoft Azure Speech",
            "badge": "paid",
            "tag": "Azure Cognitive Services Speech",
            "env_vars": [
                {
                    "key": "AZURE_SPEECH_KEY",
                    "prompt": "Azure Speech API key",
                    "url": "https://portal.azure.com/",
                },
                {
                    "key": "AZURE_SPEECH_REGION",
                    "prompt": "Azure Speech region",
                },
            ],
        }

    def transcribe(
        self,
        file_path: str,
        *,
        model: str | None = None,
        language: str | None = None,
        **extra: Any,
    ) -> dict[str, Any]:
        del model
        try:
            config = AzureSpeechConfig.from_env()
            options = AzureSpeechSTTOptions(
                language=language,
                timeout_seconds=int(extra.get("timeout_seconds", 180)),
                treat_empty_as_error=bool(extra.get("treat_empty_as_error", True)),
            )
            transcript = AzureSpeechSTT(config).transcribe_file(file_path, options=options)
            return {
                "success": True,
                "transcript": transcript,
                "provider": self.name,
            }
        except AzureSpeechError as exc:
            return {
                "success": False,
                "transcript": "",
                "error": str(exc),
                "provider": self.name,
            }
        except Exception as exc:
            return {
                "success": False,
                "transcript": "",
                "error": f"azure-speech failed: {exc}",
                "provider": self.name,
            }


AzureSTTProvider = AzureTranscriptionProvider


def register(ctx: Any) -> None:
    if hasattr(ctx, "register_tts_provider"):
        ctx.register_tts_provider(AzureTTSProvider())
    if hasattr(ctx, "register_transcription_provider"):
        ctx.register_transcription_provider(AzureTranscriptionProvider())