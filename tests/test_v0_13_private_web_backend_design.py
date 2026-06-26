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

    assert "Deep Search decision for v0.14.0: `not_needed_internal_repo_only`" in text
    assert design["version_target"] == "0.14.0"
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
    assert design["processing_execution"] == "synchronous_safe_single_file_modes"
    assert set(design["supported_modes"]) == {"analyze", "release-check", "inspect-metadata", "visualize"}
    assert set(design["deferred_modes"]) == {"clean-metadata", "visualize-compare", "compare", "humanize"}
    assert design["generated_artifacts"]["analyze"] == "analysis.json"
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
    assert "No fake metrics are added" in readme
    assert "private beta only" in readme.casefold()
    assert "There is no frontend framework" in readme
    assert "safe single-file read-only modes" in safety
    assert "sanitizes embedded images and long metadata fields" in safety
    assert "no frontend ui, deployment, dns config, or public launch" in safety.casefold()
    assert "bearer-token auth" in safety.casefold()
    assert "must not use user filenames as storage paths" in safety


def test_v0_13_generated_outputs_are_ignored():
    text = GITIGNORE.read_text(encoding="utf-8")

    assert ".var/" in text
    assert "v013_web_outputs/" in text
