from __future__ import annotations

import importlib
import pathlib
import runpy


def test_plugin_registers_tts_and_stt_providers():
    plugin_module = importlib.import_module("provider")

    class FakeContext:
        def __init__(self):
            self.tts_provider = None
            self.stt_provider = None

        def register_tts_provider(self, provider):
            self.tts_provider = provider

        def register_transcription_provider(self, provider):
            self.stt_provider = provider

    ctx = FakeContext()

    plugin_module.register(ctx)

    assert ctx.tts_provider.name == "azure-speech"
    assert ctx.stt_provider.name == "azure-speech"


def test_tts_provider_exposes_setup_schema():
    plugin_module = importlib.import_module("provider")

    schema = plugin_module.AzureTTSProvider().get_setup_schema()

    assert schema["name"] == "Microsoft Azure Speech"
    assert schema["badge"] == "paid"
    assert schema["tag"] == "Azure Cognitive Services Speech"
    assert {item["key"] for item in schema["env_vars"]} >= {
        "AZURE_SPEECH_KEY",
        "AZURE_SPEECH_REGION",
    }


def test_stt_provider_exposes_forward_compatible_setup_schema():
    plugin_module = importlib.import_module("provider")

    schema = plugin_module.AzureSTTProvider().get_setup_schema()

    assert schema["name"] == "Microsoft Azure Speech"
    assert {item["key"] for item in schema["env_vars"]} == {
        "AZURE_SPEECH_KEY",
        "AZURE_SPEECH_REGION",
    }


def test_repo_plugin_manifest_exists_with_required_metadata():
    plugin_path = pathlib.Path(__file__).resolve().parents[1] / "plugin.yaml"

    assert plugin_path.exists()

    content = plugin_path.read_text(encoding="utf-8")

    assert "name: azure-speech" in content
    assert "version: 0.1.0" in content
    assert "description: Microsoft Azure Speech STT/TTS provider for Hermes Agent" in content
    assert "requires_env:" in content
    assert "AZURE_SPEECH_KEY" in content
    assert "AZURE_SPEECH_REGION" in content


def test_repo_root_exposes_register_entrypoint():
    root_init = pathlib.Path(__file__).resolve().parents[1] / "__init__.py"

    assert root_init.exists()

    namespace = runpy.run_path(str(root_init))

    assert callable(namespace["register"])
    assert "AzureTTSProvider" in namespace
    assert "AzureSTTProvider" in namespace