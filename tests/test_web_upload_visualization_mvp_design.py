from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
README = ROOT / "README.md"
SAFETY = ROOT / "SAFETY.md"
MARKDOWN = ROOT / "docs" / "design" / "V0_11_3_WEB_UPLOAD_VISUALIZATION_MVP.md"
DESIGN_JSON = ROOT / "docs" / "design" / "v0_11_3_web_upload_visualization_mvp.json"


def _design() -> dict:
    return json.loads(DESIGN_JSON.read_text(encoding="utf-8"))


def _flatten_strings(value: object) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, dict):
        strings: list[str] = []
        for item in value.values():
            strings.extend(_flatten_strings(item))
        return strings
    if isinstance(value, list):
        strings = []
        for item in value:
            strings.extend(_flatten_strings(item))
        return strings
    return []


def test_web_upload_visualization_design_files_exist():
    assert MARKDOWN.exists()
    assert DESIGN_JSON.exists()


def test_web_upload_visualization_design_status_and_subdomain():
    design = _design()

    assert design["version_target"] == "0.11.3"
    assert design["status"] == "design_only"
    assert design["recommended_subdomain"] == "release.datenpflege-nord.de"
    assert design["deep_search_decision"] == "not_needed_internal_repo_only"
    assert design["deep_search_stop_required"] is True


def test_web_upload_visualization_allowed_and_disallowed_modes():
    design = _design()
    allowed = set(design["allowed_modes"])
    disallowed = " ".join(design["disallowed_modes"]).casefold()

    assert {
        "analyze",
        "release-check",
        "inspect-metadata",
        "clean-metadata",
        "compare",
        "conservative humanize",
    } <= allowed

    for expected in (
        "watermark",
        "fingerprint",
        "detector",
        "provenance",
        "c2pa",
        "source-attribution",
        "bypass",
        "evasion",
    ):
        assert expected in disallowed


def test_web_upload_visualization_views_and_color_semantics():
    design = _design()
    views = set(design["visualization_views"])

    assert {"original spectrum", "processed spectrum", "difference map"} <= views
    assert design["difference_map_rules"]
    assert design["color_semantics"]["blue"] == "unchanged or neutral"
    assert design["color_semantics"]["green"] == "improved or stable"
    assert design["color_semantics"]["red"] == "critical issue detected before processing"


def test_web_upload_visualization_tooltips_and_libraries():
    design = _design()
    libraries = {item["name"]: item for item in design["candidate_frontend_libraries"]}

    assert design["tooltip_examples"]
    assert "wavesurfer.js" in libraries
    assert "Meyda" in libraries
    assert "three.js" in libraries
    assert "audioMotion-analyzer" in libraries
    assert "BSD-3-Clause" in libraries["wavesurfer.js"]["license_note"]
    assert "MIT" in libraries["Meyda"]["license_note"]
    assert "MIT" in libraries["three.js"]["license_note"]
    assert libraries["audioMotion-analyzer"]["status"] == "visual_inspiration_only_pending_license_approval"
    assert "AGPL-3.0" in libraries["audioMotion-analyzer"]["license_note"]
    assert "separate approval" in libraries["audioMotion-analyzer"]["license_note"]


def test_web_upload_visualization_retention_faq_and_future_milestone():
    design = _design()

    assert design["retention_policy"]["default_retention"] == "24 hours"
    assert design["retention_policy"]["automatic_deletion_required"] is True
    assert design["retention_policy"]["commit_uploaded_audio"] is False
    assert design["retention_policy"]["commit_generated_outputs"] is False
    assert design["faq"]
    assert design["future_implementation_milestone"] == "v0.13.1 Web Upload Visualization MVP Implementation"


def test_web_upload_visualization_does_not_approve_launch_or_unsafe_behavior():
    design = _design()
    not_approved = design["not_approved"]
    boundary = design["project_reborn_boundary"]
    all_strings = " ".join(_flatten_strings(design)).casefold()

    assert not_approved["web_implementation"] is False
    assert not_approved["deployment"] is False
    assert not_approved["new_runtime_dependencies"] is False
    assert not_approved["new_audio_features"] is False
    assert not_approved["public_launch"] is False
    assert not_approved["unsafe_claims"] is False
    assert boundary["reference_only"] is True
    assert boundary["executed"] is False
    assert boundary["imported"] is False
    assert boundary["copied"] is False
    assert boundary["packaged"] is False
    assert boundary["exposed"] is False
    assert "public_launch\": true" not in all_strings
    assert "web_implementation\": true" not in all_strings


def test_web_upload_visualization_readme_and_safety_constraints():
    readme = README.read_text(encoding="utf-8")
    safety = SAFETY.read_text(encoding="utf-8")

    assert "future web upload visualization MVP is documented as design-only" in readme
    assert "No web app is implemented yet." in readme
    assert "release.datenpflege-nord.de" in readme
    assert "spectrum or difference views must show only measured technical changes" in readme
    assert "Any future web upload interface must be private beta first." in safety
    assert "Uploaded audio must be temporary." in safety
    assert "Generated web outputs must not be committed." in safety
    assert "Highlighted spectrum areas must map to measured technical metrics only." in safety
    assert "Web read-only modes must not modify files." in safety
    assert "Web clean-metadata behavior must only affect documented standard metadata fields." in safety
