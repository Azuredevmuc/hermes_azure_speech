# provider/tts.py

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional

try:
    import azure.cognitiveservices.speech as speechsdk
except ImportError:  # pragma: no cover - optional dependency at runtime
    speechsdk = None

from .config import AzureSpeechConfig
from .exceptions import (
    AzureSpeechAudioError,
    AzureSpeechCancellationError,
    AzureSpeechDependencyError,
    AzureSpeechEmptyTextError,
    AzureSpeechSynthesisError,
    AzureSpeechTimeoutError,
    AzureSpeechUnsupportedFormatError,
)
from .common import wait_for_sdk_future
from .ssml import build_ssml

if speechsdk is not None:
    DEFAULT_OUTPUT_FORMAT = (
        speechsdk.SpeechSynthesisOutputFormat.Audio24Khz160KBitRateMonoMp3
    )
else:  # pragma: no cover - only used when the Azure SDK is absent
    DEFAULT_OUTPUT_FORMAT = None
SUPPORTED_OUTPUT_SUFFIXES = {".mp3", ".wav", ".wave", ""}


@dataclass(frozen=True)
class AzureSpeechTTSOptions:
    voice: Optional[str] = None
    language: Optional[str] = None
    rate: str = "0%"
    pitch: str = "0%"
    volume: str = "0%"
    style: Optional[str] = None
    style_degree: Optional[str] = None
    use_ssml: bool = True
    output_format: Optional[str] = None
    timeout_seconds: int = 180


class AzureSpeechTTS:
    """
    Azure Speech text-to-speech backend.

    This class is intentionally independent from Hermes so it can be reused by:
    - Hermes command provider wrappers
    - standalone CLI tools
    - future MCP adapters
    """

    def __init__(self, config: AzureSpeechConfig) -> None:
        self.config = config

    @staticmethod
    def _resolve_output_format(output_path: Path, requested: Optional[str]) -> speechsdk.SpeechSynthesisOutputFormat:
        suffix = (requested or output_path.suffix or ".mp3").strip().lower()
        if suffix and not suffix.startswith("."):
            suffix = f".{suffix}"

        if suffix not in SUPPORTED_OUTPUT_SUFFIXES:
            raise AzureSpeechUnsupportedFormatError(
                f"Unsupported TTS output format requested: {suffix}. "
                f"Supported: mp3, wav."
            )

        if suffix in {".wav", ".wave"}:
            return speechsdk.SpeechSynthesisOutputFormat.Riff24Khz16BitMonoPcm

        return DEFAULT_OUTPUT_FORMAT

    @staticmethod
    def _extract_cancellation_details(result: speechsdk.SpeechSynthesisResult) -> str:
        cancellation = result.cancellation_details
        details = [
            f"reason={getattr(cancellation, 'reason', 'unknown')}",
            f"error_details={getattr(cancellation, 'error_details', '')}",
        ]
        return ", ".join(details)

    def synthesize_to_file(
        self,
        text: str,
        output_path: str | Path,
        *,
        options: Optional[AzureSpeechTTSOptions] = None,
    ) -> Path:
        if speechsdk is None:
            raise AzureSpeechDependencyError(
                "Azure Speech SDK is not installed. Please install azure-cognitiveservices-speech."
            )

        opts = options or AzureSpeechTTSOptions()
        text = (text or "").strip()

        if not text:
            raise AzureSpeechEmptyTextError("Cannot synthesize empty text.")

        out_path = Path(output_path)
        out_path.parent.mkdir(parents=True, exist_ok=True)

        voice = (opts.voice or self.config.voice).strip()
        language = (opts.language or self.config.language).strip()

        speech_config = speechsdk.SpeechConfig(
            subscription=self.config.speech_key,
            region=self.config.speech_region,
        )
        speech_config.speech_synthesis_voice_name = voice
        speech_config.set_speech_synthesis_output_format(
            self._resolve_output_format(out_path, opts.output_format)
        )

        audio_config = speechsdk.audio.AudioOutputConfig(filename=str(out_path))
        synthesizer = speechsdk.SpeechSynthesizer(
            speech_config=speech_config,
            audio_config=audio_config,
        )

        try:
            if opts.use_ssml:
                payload = build_ssml(
                    text,
                    language=language,
                    voice=voice,
                    rate=opts.rate,
                    pitch=opts.pitch,
                    volume=opts.volume,
                    style=opts.style,
                    style_degree=opts.style_degree,
                )
                result = wait_for_sdk_future(
                    synthesizer.speak_ssml_async(payload),
                    opts.timeout_seconds,
                )
            else:
                result = wait_for_sdk_future(
                    synthesizer.speak_text_async(text),
                    opts.timeout_seconds,
                )

            if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
                return out_path

            if result.reason == speechsdk.ResultReason.Canceled:
                details = self._extract_cancellation_details(result)
                raise AzureSpeechCancellationError(f"Speech synthesis canceled: {details}")

            raise AzureSpeechSynthesisError(f"Unexpected synthesis result: {result.reason}")

        except TimeoutError as exc:
            if out_path.exists():
                out_path.unlink(missing_ok=True)
            raise AzureSpeechTimeoutError(
                f"Azure Speech TTS timed out after {opts.timeout_seconds} seconds."
            ) from exc
        except OSError as exc:
            if out_path.exists():
                out_path.unlink(missing_ok=True)
            raise AzureSpeechAudioError(f"Audio output failed: {exc}") from exc
        except (AzureSpeechCancellationError, AzureSpeechSynthesisError):
            if out_path.exists():
                out_path.unlink(missing_ok=True)
            raise
        except Exception as exc:
            if out_path.exists():
                out_path.unlink(missing_ok=True)
            raise AzureSpeechSynthesisError(f"Unexpected Azure Speech TTS failure: {exc}") from exc


def synthesize_text_to_file(
    text: str,
    output_path: str | Path,
    *,
    config: AzureSpeechConfig,
    voice: Optional[str] = None,
    language: Optional[str] = None,
    rate: str = "0%",
    pitch: str = "0%",
    volume: str = "0%",
    style: Optional[str] = None,
    style_degree: Optional[str] = None,
    use_ssml: bool = True,
    output_format: Optional[str] = None,
) -> Path:
    """
    Convenience wrapper for callers that want a one-shot TTS invocation.
    """
    engine = AzureSpeechTTS(config=config)
    return engine.synthesize_to_file(
        text,
        output_path,
        options=AzureSpeechTTSOptions(
            voice=voice,
            language=language,
            rate=rate,
            pitch=pitch,
            volume=volume,
            style=style,
            style_degree=style_degree,
            use_ssml=use_ssml,
            output_format=output_format,
        ),
    )