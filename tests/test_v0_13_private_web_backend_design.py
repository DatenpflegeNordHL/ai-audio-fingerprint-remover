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

    assert "Deep Search decision: `needed_current_library_behavior`" in text
    assert design["version_target"] == "0.13.0"
    assert design["deep_search_decision"] == "needed_current_library_behavior"
    assert design["deep_search_completed"] is True


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
    assert design["processing_execution"] == "deferred"
    assert set(design["supported_modes"]) == {"analyze", "release-check", "inspect-metadata", "clean-metadata", "visualize"}
    assert set(design["deferred_modes"]) == {"visualize-compare", "compare", "humanize"}
    assert "frontend UI" in design["not_approved"]
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
    assert "private beta only" in readme.casefold()
    assert "There is no frontend UI" in readme
    assert "no frontend ui, deployment, dns config, or public launch" in safety.casefold()
    assert "bearer-token auth" in safety.casefold()
    assert "must not use user filenames as storage paths" in safety


def test_v0_13_generated_outputs_are_ignored():
    text = GITIGNORE.read_text(encoding="utf-8")

    assert ".var/" in text
    assert "v013_web_outputs/" in text
