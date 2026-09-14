import pathlib

import tomllib
from packaging.requirements import Requirement


def test_project_metadata_has_no_placeholder_urls():
    pyproject_path = pathlib.Path(__file__).resolve().parents[1] / "pyproject.toml"
    payload = tomllib.loads(pyproject_path.read_text(encoding="utf-8"))

    project_urls = payload.get("project", {}).get("urls", {})

    assert project_urls == {}, (
        "Project URLs must be removed until real public metadata is available; "
        "placeholder repository URLs are not compliant for a public package."
    )


def test_dev_dependencies_include_security_audit_tool():
    pyproject_path = pathlib.Path(__file__).resolve().parents[1] / "pyproject.toml"
    payload = tomllib.loads(pyproject_path.read_text(encoding="utf-8"))

    dev_section = payload.get("project", {}).get("optional-dependencies", {})
    dev_dependencies = dev_section.get("dev", [])
    dependency_names = {Requirement(dependency).name.lower() for dependency in dev_dependencies}

    assert "pip-audit" in dependency_names, (
        "The development environment must include pip-audit so dependency "
        "security checks are part of the quality gate."
    )


def test_project_exposes_installed_cli_entrypoints():
    pyproject_path = pathlib.Path(__file__).resolve().parents[1] / "pyproject.toml"
    payload = tomllib.loads(pyproject_path.read_text(encoding="utf-8"))

    project_scripts = payload.get("project", {}).get("scripts", {})

    assert project_scripts.get("hermes-azure-speech-tts") == "provider.cli:tts_main"
    assert project_scripts.get("hermes-azure-speech-stt") == "provider.cli:stt_main"


def test_project_exposes_hermes_plugin_entrypoint():
    pyproject_path = pathlib.Path(__file__).resolve().parents[1] / "pyproject.toml"
    payload = tomllib.loads(pyproject_path.read_text(encoding="utf-8"))

    plugin_entrypoints = (
        payload.get("project", {}).get("entry-points", {}).get("hermes_agent.plugins", {})
    )

    assert plugin_entrypoints.get("azure-speech") == "provider:register"
