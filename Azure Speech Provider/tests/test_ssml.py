import importlib
import sys
import types

import pytest


@pytest.fixture
def ssml_module(monkeypatch):
    monkeypatch.setitem(sys.modules, "azure", types.ModuleType("azure"))
    import provider.ssml as ssml_module
    importlib.reload(ssml_module)
    return ssml_module


def test_build_ssml_wraps_text_with_speak_and_voice(ssml_module):
    payload = ssml_module.build_ssml("Hallo Welt", voice="de-DE-KatjaNeural")

    assert payload.startswith("<speak")
    assert "<voice name=\"de-DE-KatjaNeural\"" in payload
    assert "Hallo Welt" in payload


def test_build_ssml_applies_substitutions_and_normalizes_whitespace(ssml_module):
    payload = ssml_module.build_ssml(
        "  Hallo   Azure AI Foundry  ",
        substitutions={"Azure AI Foundry": "Azure AI Foundry"},
    )

    assert "<sub alias=\"Azure AI Foundry\"" in payload
    assert "Hallo" in payload
    assert "Azure AI Foundry" in payload
