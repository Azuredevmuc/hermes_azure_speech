from __future__ import annotations

from pathlib import Path


def test_tts_main_uses_hermes_provider_wrapper(monkeypatch, tmp_path):
    from provider import cli as cli_module

    input_path = tmp_path / "input.txt"
    output_path = tmp_path / "output.mp3"
    input_path.write_text("Hallo Hermes", encoding="utf-8")

    observed: dict[str, object] = {}

    class FakeTTSProvider:
        @classmethod
        def from_env(cls):
            observed["from_env_called"] = True
            return cls()

        def synthesize(self, text, output_path_arg):
            observed["text"] = text
            observed["output_path"] = str(output_path_arg)
            return Path(output_path_arg)

    monkeypatch.setattr(cli_module, "HermesTTSProvider", FakeTTSProvider)

    exit_code = cli_module.tts_main(["--input", str(input_path), "--output", str(output_path)])

    assert exit_code == 0
    assert observed["from_env_called"] is True
    assert observed["text"] == "Hallo Hermes"
    assert observed["output_path"] == str(output_path)


def test_stt_main_uses_hermes_provider_wrapper(monkeypatch, tmp_path):
    from provider import cli as cli_module

    input_path = tmp_path / "input.wav"
    output_path = tmp_path / "transcript.txt"
    input_path.write_text("fake-audio", encoding="utf-8")

    observed: dict[str, object] = {}

    class FakeSTTProvider:
        @classmethod
        def from_env(cls):
            observed["from_env_called"] = True
            return cls()

        def transcribe(self, input_path_arg):
            observed["input_path"] = str(input_path_arg)
            return "Hallo aus Azure"

    monkeypatch.setattr(cli_module, "HermesSTTProvider", FakeSTTProvider)

    exit_code = cli_module.stt_main(["--input", str(input_path), "--output", str(output_path)])

    assert exit_code == 0
    assert observed["from_env_called"] is True
    assert observed["input_path"] == str(input_path)
    assert output_path.read_text(encoding="utf-8") == "Hallo aus Azure"