from __future__ import annotations

import importlib
import pathlib
import re
import tomllib


SEMVER_RE = re.compile(r"^\d+\.\d+\.\d+$")


def test_package_version_is_semver_and_single_sourced():
    version_module = importlib.import_module("provider.version")
    pyproject_path = pathlib.Path(__file__).resolve().parents[1] / "pyproject.toml"
    payload = tomllib.loads(pyproject_path.read_text(encoding="utf-8"))

    assert SEMVER_RE.match(version_module.__version__)
    assert version_module.__version__ == ".".join(map(str, version_module.VERSION))
    assert payload["tool"]["setuptools"]["dynamic"]["version"] == {
        "attr": "provider.version.__version__"
    }


def test_changelog_contains_current_release_version():
    version_module = importlib.import_module("provider.version")
    changelog_path = pathlib.Path(__file__).resolve().parents[1] / "CHANGELOG.md"
    changelog = changelog_path.read_text(encoding="utf-8")

    assert f"## {version_module.__version__}" in changelog


def test_version_metadata_is_consistent():
    version_module = importlib.import_module("provider.version")

    assert version_module.TITLE == "hermes-provider-azure-speech"
    assert version_module.DESCRIPTION == "Azure Speech STT/TTS provider for Hermes"
    assert version_module.AUTHOR == "Ralf Rottmann"
    assert version_module.LICENSE == "MIT"