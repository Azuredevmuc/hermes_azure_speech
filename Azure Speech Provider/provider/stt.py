# provider/stt.py

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
    AzureSpeechEmptyTranscriptError,
    AzureSpeechRecognitionError,
    AzureSpeechTimeoutError,
)
from .common import wait_for_sdk_future

DEFAULT_LANGUAGE = "de-DE"


@dataclass(frozen=True)
class AzureSpeechSTTOptions:
    language: Optional[str] = None
    timeout_seconds: int = 180
    treat_empty_as_error: bool = True


class AzureSpeechSTT:
    """
    Azure Speech speech-to-text backend.

    This class is intentionally independent from Hermes so it can be reused by:
    - Hermes command provider wrappers
    - standalone CLI tools
    - future MCP adapters
    """

    def __init__(self, config: AzureSpeechConfig) -> None:
        self.config = config

    def transcribe_file(
        self,
        input_path: str | Path,
        *,
        options: Optional[AzureSpeechSTTOptions] = None,
    ) -> str:
        if speechsdk is None:
            raise AzureSpeechDependencyError(
                "Azure Speech SDK is not installed. Please install azure-cognitiveservices-speech."
            )

        opts = options or AzureSpeechSTTOptions()

        in_path = Path(input_path)
        if not in_path.exists():
            raise AzureSpeechAudioError(f"Audio input file does not exist: {in_path}")

        language = (opts.language or self.config.language or DEFAULT_LANGUAGE).strip()

        speech_config = speechsdk.SpeechConfig(
            subscription=self.config.speech_key,
            region=self.config.speech_region,
        )
        speech_config.speech_recognition_language = language

        audio_config = speechsdk.audio.AudioConfig(filename=str(in_path))
        recognizer = speechsdk.SpeechRecognizer(
            speech_config=speech_config,
            audio_config=audio_config,
        )

        try:
            result = wait_for_sdk_future(recognizer.recognize_once_async(), opts.timeout_seconds)
        except TimeoutError as exc:
            raise AzureSpeechTimeoutError(
                f"Azure Speech STT timed out after {opts.timeout_seconds} seconds."
            ) from exc
        except OSError as exc:
            raise AzureSpeechAudioError(f"Audio input failed: {exc}") from exc
        except Exception as exc:
            raise AzureSpeechRecognitionError(f"Unexpected Azure Speech STT failure: {exc}") from exc

        if result.reason == speechsdk.ResultReason.RecognizedSpeech:
            transcript = (result.text or "").strip()
            if transcript:
                return transcript

            if opts.treat_empty_as_error:
                raise AzureSpeechEmptyTranscriptError("Azure Speech returned an empty transcript.")

            return ""

        if result.reason == speechsdk.ResultReason.NoMatch:
            if opts.treat_empty_as_error:
                raise AzureSpeechEmptyTranscriptError("No speech could be recognized from the audio.")
            return ""

        if result.reason == speechsdk.ResultReason.Canceled:
            cancellation = result.cancellation_details
            raise AzureSpeechCancellationError(
                "Speech recognition canceled: "
                f"reason={getattr(cancellation, 'reason', 'unknown')}, "
                f"error_details={getattr(cancellation, 'error_details', '')}"
            )

        raise AzureSpeechRecognitionError(f"Unexpected recognition result: {result.reason}")


def transcribe_file_to_text(
    input_path: str | Path,
    *,
    config: AzureSpeechConfig,
    language: Optional[str] = None,
    treat_empty_as_error: bool = True,
) -> str:
    """
    Convenience wrapper for callers that want a one-shot STT invocation.
    """
    engine = AzureSpeechSTT(config=config)
    return engine.transcribe_file(
        input_path,
        options=AzureSpeechSTTOptions(
            language=language,
            treat_empty_as_error=treat_empty_as_error,
        ),
    )