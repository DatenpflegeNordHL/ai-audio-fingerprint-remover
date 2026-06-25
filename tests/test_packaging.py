from __future__ import annotations

from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:  # Python 3.10
    import tomli as tomllib


ROOT = Path(__file__).resolve().parents[1]


def test_pyproject_packaging_metadata():
    metadata = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    project = metadata["project"]
    optional_dependencies = project["optional-dependencies"]

    assert project["name"] == "audio-quality-humanizer"
    assert ">=3.10" in project["requires-python"]
    assert project["scripts"]["ai-humanizer"] == "audio_quality_humanizer.cli:main"
    assert any(dependency.startswith("pytest") for dependency in optional_dependencies["test"])
    assert any(dependency.startswith("build") for dependency in optional_dependencies["dev"])


def test_setuptools_discovers_audio_quality_humanizer_packages():
    metadata = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    package_includes = metadata["tool"]["setuptools"]["packages"]["find"]["include"]

    assert "audio_quality_humanizer*" in package_includes
