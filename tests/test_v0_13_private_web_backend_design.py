from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MARKDOWN = ROOT / "docs" / "design" / "V0_13_0_PRIVATE_WEB_BACKEND_MVP.md"
DESIGN_JSON = ROOT / "docs" / "design" / "v0_13_0_private_web_backend_mvp.json"
DEPLOYMENT_CHECKLIST = ROOT / "docs" / "design" / "V0_16_0_DEPLOYMENT_READINESS_CHECKLIST.md"
DEPLOYMENT_ROOT = ROOT / "deployment"
SMOKE_SCRIPT = ROOT / "scripts" / "private-beta-smoke.sh"
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

    assert "Deep Search decision for v0.18.0: `not_needed_internal_repo_only`" in text
    assert design["version_target"] == "0.18.0"
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
    assert design["max_upload_mib"] == 50
    assert design["runtime_config"]["AQH_WEB_HOST"] == "127.0.0.1"
    assert design["runtime_config"]["AQH_WEB_PORT"] == 8017
    assert design["runtime_config"]["AQH_WEB_MAX_UPLOAD_MB"] == 50
    assert design["runtime_config"]["AQH_WEB_MAX_ACTIVE_JOBS"] == 1
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
    assert design["operator_page"]["local_exposure_warning"] is True
    assert design["operator_page"]["cleanup_control"] is True
    assert design["operator_page"]["retention_display"] is True
    assert design["operator_page"]["recent_jobs_display"] is True
    assert design["operator_page"]["fake_metrics"] is False
    assert design["operator_config_endpoint"]["requires_auth"] is True
    assert design["operator_config_endpoint"]["exposes_paths"] is False
    assert design["operator_config_endpoint"]["exposes_secrets"] is False
    assert design["job_listing_endpoint"]["requires_auth"] is True
    assert design["job_listing_endpoint"]["recent_summaries_only"] is True
    assert design["job_listing_endpoint"]["exposes_paths"] is False
    assert design["artifact_downloads"]["must_be_listed_in_status_json"] is True
    assert design["security_headers"]["x_content_type_options"] == "nosniff"
    assert design["auth"]["optional_dashboard_beta_password"] is True
    assert design["auth"]["beta_password_env_vars"] == ["AQH_BETA_PASSWORD_HASH", "AQH_BETA_PASSWORD"]
    assert design["deployment_prep"]["private_side_project_beta"] is True
    assert design["deployment_prep"]["target_hostname"] == "beta.datenpflege-nord.de"
    assert design["deployment_prep"]["local_service_target"] == "http://localhost:8017"
    assert design["deployment_prep"]["provider_comparison"] is False
    assert design["server_rollout"]["runbook"] == "deployment/server-rollout.md"
    assert design["server_rollout"]["rollback"] == "deployment/rollback.md"
    assert design["server_rollout"]["optional_smoke_script"] == "scripts/private-beta-smoke.sh"
    assert design["server_rollout"]["public_ci_cd"] is False
    assert design["server_rollout"]["infrastructure_automation"] is False
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
    assert "AQH_WEB_TOKEN=dev-token uvicorn audio_quality_humanizer.web.app:app --host 127.0.0.1 --reload" in readme
    assert "Open `http://127.0.0.1:8000/` for the local operator page." in readme
    assert "`analyze` writes `analysis.json`" in readme
    assert "The dashboard renders generated JSON artifacts" in readme
    assert "metadata display is sanitized" in readme
    assert "`clean-metadata` writes `cleaned_output.<ext>`" in readme
    assert "`compare` writes `compare.json`" in readme
    assert "`visualize-compare` writes `compare.json` and `visual_compare.json`" in readme
    assert "`GET /api/config` returns safe operator settings only" in readme
    assert "Artifact downloads require both a safe artifact name and membership in the job's `status.json` artifact list" in readme
    assert "beta.datenpflege-nord.de" in readme
    assert "AQH_BETA_PASSWORD_HASH" in readme
    assert "No fake metrics are added" in readme
    assert "private beta only" in readme.casefold()
    assert "There is no frontend framework" in readme
    assert "safe single-file read-only modes" in safety
    assert "fixed before/after upload fields" in safety
    assert "`clean-metadata` must not overwrite the uploaded input file" in safety
    assert "sanitizes embedded images and long metadata fields" in safety
    assert "no frontend framework, public launch, official product positioning" in safety.casefold()
    assert "bearer-token auth" in safety.casefold()
    assert "must not use user filenames as storage paths" in safety
    assert "Private web artifact downloads must require the requested artifact name to be listed in the job status." in safety
    assert "The temporary shared beta password must be configured outside Git." in safety


def test_v0_16_deployment_readiness_checklist_is_docs_only():
    assert DEPLOYMENT_CHECKLIST.exists()
    text = DEPLOYMENT_CHECKLIST.read_text(encoding="utf-8")

    assert "Not deployed yet." in text
    assert "documentation only" in text
    assert "HTTPS" in text
    assert "reverse proxy" in text
    assert "upload body limits" in text
    assert "timeout limits" in text
    assert "temporary storage permissions" in text
    assert "log retention" in text
    assert "auth hardening" in text
    assert "rate limiting" in text
    assert "abuse prevention" in text
    assert "privacy and data deletion" in text
    assert "backup and restore scope" in text
    assert "`needed_external_standards`" in text
    assert "`needed_current_library_behavior`" in text
    assert "`needed_security_or_safety_policy_check`" in text
    assert "No specific provider choice is approved yet." in text


def test_v0_17_private_beta_deployment_docs_are_placeholder_only():
    expected = [
        "README.md",
        "cloudflare-tunnel/README.md",
        "cloudflare-tunnel/public-hostname.example.md",
        "env/web.env.example",
        "security-checklist.md",
        "privacy-beta-checklist.md",
        "docker/docker-compose.example.yml",
        "systemd/audio-quality-humanizer-web.service.example",
    ]
    for relative in expected:
        assert (DEPLOYMENT_ROOT / relative).exists()

    combined = "\n".join((DEPLOYMENT_ROOT / relative).read_text(encoding="utf-8") for relative in expected)
    assert "beta.datenpflege-nord.de" in combined
    assert "http://localhost:8017" in combined
    assert "127.0.0.1:8017:8017" in combined
    assert "AQH_WEB_TOKEN=replace-with-random-private-api-token" in combined
    assert "AQH_BETA_PASSWORD_HASH=sha256:replace-with-real-sha256-password-hash" in combined
    assert "audio-quality-humanizer-web:0.18.0-private" in combined
    assert "Cloudflare Tunnel already exists" in combined
    assert "Do not expose local ports publicly." in combined
    assert "No analytics." in combined
    for forbidden in ("Kubernetes", "Terraform", "Pulumi", "Ansible"):
        assert forbidden not in combined


def test_v0_18_server_rollout_docs_and_smoke_script_cover_required_steps():
    expected = [
        "server-rollout.md",
        "rollback.md",
        "smoke-test.md",
        "checklists/preflight.md",
        "checklists/post-deploy.md",
    ]
    for relative in expected:
        assert (DEPLOYMENT_ROOT / relative).exists()
    assert SMOKE_SCRIPT.exists()

    combined = "\n".join((DEPLOYMENT_ROOT / relative).read_text(encoding="utf-8") for relative in expected)
    script = SMOKE_SCRIPT.read_text(encoding="utf-8")

    assert "git fetch --tags" in combined
    assert "git checkout v0.18.0" in combined
    assert "AQH_WEB_HOST=127.0.0.1" in combined
    assert "AQH_WEB_PORT=8017" in combined
    assert "AQH_WEB_MAX_UPLOAD_MB=50" in combined
    assert "AQH_WEB_JOB_TTL_HOURS=24" in combined
    assert "AQH_WEB_MAX_ACTIVE_JOBS=1" in combined
    assert "AQH_WEB_TOKEN=<server-only secret>" in combined
    assert "AQH_BETA_PASSWORD_HASH=<server-only value>" in combined
    assert "curl -i http://127.0.0.1:8017/health" in combined
    assert "Public hostname: beta.datenpflege-nord.de" in combined
    assert "Service: http://localhost:8017" in combined
    assert "dashboard without password returns HTTP `401`" in combined
    assert "dashboard with beta password returns HTTP `200`" in combined
    assert "oversized upload returns HTTP `413`" in combined
    assert "active job limit can return HTTP `429`" in combined
    assert "no token values" in combined
    assert "no upload/output backups" in combined
    assert "docker compose down" in combined
    assert "AQH_WEB_TOKEN is required" in script
    assert "AQH_BETA_SMOKE_PASSWORD is required" in script
    assert "Private beta smoke checks passed." in script


def test_v0_18_1_rollout_docs_use_current_rollout_target():
    rollout = (DEPLOYMENT_ROOT / "server-rollout.md").read_text(encoding="utf-8")
    preflight = (DEPLOYMENT_ROOT / "checklists" / "preflight.md").read_text(encoding="utf-8")
    rollback = (DEPLOYMENT_ROOT / "rollback.md").read_text(encoding="utf-8")

    normal_rollout = "\n".join([rollout, preflight])
    assert "git checkout v0.18.0" in normal_rollout
    assert "audio-quality-humanizer 0.18.0" in normal_rollout
    assert "git checkout v0.17.0" not in normal_rollout
    assert "audio-quality-humanizer 0.17.0" not in normal_rollout
    assert "git checkout v0.17.0" in rollback
    assert "example rollback target" in rollback


def test_v0_13_generated_outputs_are_ignored():
    text = GITIGNORE.read_text(encoding="utf-8")

    assert ".var/" in text
    assert "v013_web_outputs/" in text
    assert "v015_web_outputs/" in text
    assert "v016_web_outputs/" in text
    assert "v017_web_outputs/" in text
    assert "v018_web_outputs/" in text
    assert "local_humanize_outputs/" in text
