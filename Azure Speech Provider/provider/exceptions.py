# provider/exceptions.py

from __future__ import annotations


class AzureSpeechError(Exception):
    """Base class for all Azure Speech provider errors."""


class AzureSpeechConfigError(AzureSpeechError):
    """Raised when required configuration is missing or invalid."""


class AzureSpeechTTSConfigurationError(AzureSpeechError):
    """Raised when TTS configuration is invalid."""


class AzureSpeechSTTConfigurationError(AzureSpeechError):
    """Raised when STT configuration is invalid."""


class AzureSpeechSynthesisError(AzureSpeechError):
    """Raised when Azure Speech TTS synthesis fails."""


class AzureSpeechRecognitionError(AzureSpeechError):
    """Raised when Azure Speech STT recognition fails."""


class AzureSpeechAudioError(AzureSpeechError):
    """Raised when audio input/output handling fails."""


class AzureSpeechDependencyError(AzureSpeechError):
    """Raised when required runtime dependencies are missing."""


class AzureSpeechTimeoutError(AzureSpeechError):
    """Raised when a speech operation times out."""


class AzureSpeechUnsupportedFormatError(AzureSpeechError):
    """Raised when an unsupported audio format is requested."""


class AzureSpeechEmptyTranscriptError(AzureSpeechError):
    """Raised when STT returns no transcript and that is treated as an error."""


class AzureSpeechEmptyTextError(AzureSpeechError):
    """Raised when TTS is asked to synthesize empty text."""


class AzureSpeechCancellationError(AzureSpeechError):
    """Raised when Azure cancels a synthesis or recognition operation."""


class AzureSpeechProviderNotEnabledError(AzureSpeechError):
    """Raised when a provider is called before it has been enabled or configured."""
