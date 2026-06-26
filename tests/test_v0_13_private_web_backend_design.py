from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MARKDOWN = ROOT / "docs" / "design" / "V0_13_0_PRIVATE_WEB_BACKEND_MVP.md"
DESIGN_JSON = ROOT / "docs" / "design" / "v0_13_0_private_web_backend_mvp.json"
README = ROOT / "README.md"
SAFETY = ROOT / "SAFETY.md"
GITIGNORE = ROOT / ".gitignore"
PYPROJECT = ROOT / "pyproject.toml"


def _design() -> dict:
    return json.loads(DESIGN_JSON.read_text(encoding="utf-8"))


def test_v0_13_private_web_design_docs_exist_and_record_deep_search():
    assert MARKDOWN.exists()
    assert DESIGN_JSON.exists()
    text = MARKDOWN.read_text(encoding="utf-8")
    design = _design()

    assert "Deep Search decision for v0.15.0: `not_needed_internal_repo_only`" in text
    assert design["version_target"] == "0.15.0"
    assert design["deep_search_decision"] == "not_needed_internal_repo_only"
    assert design["deep_search_completed"] is False


def test_v0_13_private_web_dependencies_are_constrained():
    text = PYPROJECT.read_text(encoding="utf-8")

    assert "fastapi>=0.138.1,<0.139.0" in text
    assert "uvicorn>=0.49.0,<0.50.0" in text
    assert "python-multipart>=0.0.32,<0.0.33" in text
    assert "fastapi[standard]" not in text
    assert "uvicorn[standard]" not in text
    assert "starlette[full]" not in text


def test_v0_13_private_web_design_shape_and_boundaries():
    design = _design()

    assert design["auth"]["type"] == "bearer_token"
    assert design["auth"]["required_for_api_endpoints"] is True
    assert design["max_upload_mib"] == 100
    assert design["job_storage"]["user_filenames_as_paths"] is False
    assert design["processing_execution"] == "synchronous_safe_single_and_two_file_modes"
    assert set(design["supported_modes"]) == {
        "analyze",
        "release-check",
        "inspect-metadata",
        "clean-metadata",
        "visualize",
        "compare",
        "visualize-compare",
    }
    assert set(design["single_file_modes"]) == {"analyze", "release-check", "inspect-metadata", "clean-metadata", "visualize"}
    assert set(design["two_file_modes"]) == {"compare", "visualize-compare"}
    assert set(design["deferred_modes"]) == {"humanize"}
    assert design["generated_artifacts"]["analyze"] == "analysis.json"
    assert design["generated_artifacts"]["clean-metadata"] == [
        "cleaned_output.<ext>",
        "metadata_before.json",
        "clean_metadata.json",
        "metadata_after.json",
    ]
    assert design["generated_artifacts"]["compare"] == "compare.json"
    assert design["generated_artifacts"]["visualize-compare"] == ["compare.json", "visual_compare.json"]
    assert design["operator_page"]["path"] == "/"
    assert design["operator_page"]["external_assets"] is False
    assert design["operator_page"]["artifact_rendering"] is True
    assert design["operator_page"]["fake_metrics"] is False
    assert design["metadata_display"]["sanitized_embedded_images"] is True
    assert design["metadata_display"]["max_display_chars"] == 500
    assert "frontend framework" in design["not_approved"]
    assert "deployment" in design["not_approved"]
    assert design["project_reborn_boundary"]["copied"] is False
    assert design["project_reborn_boundary"]["imported"] is False
    assert design["project_reborn_boundary"]["executed"] is False
    assert design["project_reborn_boundary"]["packaged"] is False
    assert design["project_reborn_boundary"]["exposed"] is False


def test_v0_13_readme_and_safety_document_private_beta_only():
    readme = README.read_text(encoding="utf-8")
    safety = SAFETY.read_text(encoding="utf-8")

    assert "Private web backend MVP" in readme
    assert 'python -m pip install -e ".[web,dev,test]"' in readme
    assert "AQH_WEB_TOKEN=dev-token uvicorn audio_quality_humanizer.web.app:app --reload" in readme
    assert "Open `http://127.0.0.1:8000/` for the local operator page." in readme
    assert "`analyze` writes `analysis.json`" in readme
    assert "The dashboard renders generated JSON artifacts" in readme
    assert "metadata display is sanitized" in readme
    assert "`clean-metadata` writes `cleaned_output.<ext>`" in readme
    assert "`compare` writes `compare.json`" in readme
    assert "`visualize-compare` writes `compare.json` and `visual_compare.json`" in readme
    assert "No fake metrics are added" in readme
    assert "private beta only" in readme.casefold()
    assert "There is no frontend framework" in readme
    assert "safe single-file read-only modes" in safety
    assert "fixed before/after upload fields" in safety
    assert "`clean-metadata` must not overwrite the uploaded input file" in safety
    assert "sanitizes embedded images and long metadata fields" in safety
    assert "no frontend framework, deployment, dns config, or public launch" in safety.casefold()
    assert "bearer-token auth" in safety.casefold()
    assert "must not use user filenames as storage paths" in safety


def test_v0_13_generated_outputs_are_ignored():
    text = GITIGNORE.read_text(encoding="utf-8")

    assert ".var/" in text
    assert "v013_web_outputs/" in text
    assert "v015_web_outputs/" in text
