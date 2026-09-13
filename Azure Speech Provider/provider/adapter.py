from __future__ import annotations

from .hermes import HermesSTTProvider, HermesTTSProvider


class HermesAzureSpeechAdapter:
    """Importable adapter surface for Hermes speech integrations."""

    provider_name = "azure_speech"
    runtime = "python"
    capabilities = ("stt", "tts")

    @classmethod
    def load_from_env(cls) -> dict[str, object]:
        return {
            "stt": HermesSTTProvider.from_env(),
            "tts": HermesTTSProvider.from_env(),
        }

    @classmethod
    def describe_from_env(cls) -> dict[str, object]:
        cls.load_from_env()
        return {
            "provider_name": cls.provider_name,
            "runtime": cls.runtime,
            "capabilities": list(cls.capabilities),
        }