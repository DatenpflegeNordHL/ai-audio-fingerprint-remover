from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MARKDOWN = ROOT / "docs" / "design" / "V0_12_0_VISUALIZATION_ARTIFACTS.md"
DESIGN_JSON = ROOT / "docs" / "design" / "v0_12_0_visualization_artifacts.json"
README = ROOT / "README.md"
SAFETY = ROOT / "SAFETY.md"


def _design() -> dict:
    return json.loads(DESIGN_JSON.read_text(encoding="utf-8"))


def test_v0_12_visualization_design_docs_exist():
    assert MARKDOWN.exists()
    assert DESIGN_JSON.exists()


def test_v0_12_visualization_design_json_status_and_gate():
    design = _design()

    assert design["version_target"] == "0.12.0"
    assert design["status"] == "implemented"
    assert design["deep_search_decision"] == "not_needed_internal_repo_only"
    assert design["deep_search_stop_required"] is True
    assert design["real_local_validation_required"] is True
    assert design["no_op_check_required"] is True


def test_v0_12_visualization_design_schemas_and_labels():
    design = _design()

    assert design["single_file_schema"]["action"] == "visualize"
    assert design["comparison_schema"]["action"] == "visualize-compare"
    assert "waveform peaks" in " ".join(design["implemented_artifacts"])
    assert "difference map reports" in " ".join(design["implemented_artifacts"])
    assert "spectral energy changed" in design["allowed_labels"]
    forbidden = " ".join(design["forbidden_labels"]).casefold()
    for expected in (
        "fingerprint",
        "watermark",
        "detector",
        "provenance",
        "source attribution",
        "c2pa",
        "detectability",
        "platform",
        "distributor",
    ):
        assert expected in forbidden


def test_v0_12_visualization_design_future_web_and_project_reborn_boundary():
    design = _design()
    future = design["future_web_use"]
    boundary = design["project_reborn_boundary"]

    assert future["supports_release_subdomain_design"] == "release.datenpflege-nord.de"
    assert future["web_app_implemented"] is False
    assert future["runtime_frontend_dependencies_added"] is False
    assert future["deployment_added"] is False
    assert boundary["reference_only"] is True
    assert boundary["executed"] is False
    assert boundary["imported"] is False
    assert boundary["copied"] is False
    assert boundary["packaged"] is False
    assert boundary["exposed"] is False


def test_v0_12_visualization_markdown_contains_required_sections():
    text = MARKDOWN.read_text(encoding="utf-8")

    for required in (
        "Implemented.",
        "`not_needed_internal_repo_only`",
        "Visualization artifacts show measured technical audio features only.",
        "Waveform Peaks Design",
        "Spectrogram Design",
        "Difference Map Design",
        "Tooltip Region Design",
        "No-Op Check Plan",
        "Real Local Audio Validation Plan",
        "Future Web Relationship",
    ):
        assert required in text


def test_v0_12_visualization_readme_and_safety_notes():
    readme = README.read_text(encoding="utf-8")
    safety = SAFETY.read_text(encoding="utf-8")

    assert "Visualization artifacts" in readme
    assert "ai-humanizer visualize input.wav" in readme
    assert "ai-humanizer visualize-compare before.wav after.wav" in readme
    assert "difference maps show measured technical changes only" in readme
    assert "visualization artifacts are read-only" in safety.casefold()
    assert "no web app exists yet" in safety.casefold()
