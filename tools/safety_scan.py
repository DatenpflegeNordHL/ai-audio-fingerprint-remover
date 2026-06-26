"""Scan public-facing surfaces for unsafe feature claims."""

from __future__ import annotations

import contextlib
import io
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from audio_quality_humanizer.cli import _build_parser
from audio_quality_humanizer.safety import assert_no_unsafe_public_claims


PUBLIC_FILES = (
    "README.md",
    "SAFETY.md",
    "CHANGELOG.md",
    "pyproject.toml",
    "audio_quality_humanizer/cli.py",
    "audio_quality_humanizer/safety.py",
    "audio_quality_humanizer/visualization_artifacts.py",
    "audio_quality_humanizer/web/app.py",
    "audio_quality_humanizer/web/auth.py",
    "audio_quality_humanizer/web/config.py",
    "audio_quality_humanizer/web/metadata_display.py",
    "audio_quality_humanizer/web/models.py",
    "audio_quality_humanizer/web/processing.py",
    "audio_quality_humanizer/web/storage.py",
    "audio_quality_humanizer/web/upload_validation.py",
    "audio_quality_humanizer/reports/markdown_report.py",
    "docs/design/V0_10_0_DESIGN_SPEC.md",
    "docs/design/v0_10_0_design_spec.json",
    "docs/design/CANDIDATE_REALITY_GATE.md",
    "docs/design/REBORN_025_DEEP_REVIEW.md",
    "docs/design/REBORN_005_DEEP_REVIEW.md",
    "docs/design/reborn_005_deep_review.json",
    "docs/design/V0_11_3_WEB_UPLOAD_VISUALIZATION_MVP.md",
    "docs/design/v0_11_3_web_upload_visualization_mvp.json",
    "docs/design/V0_12_0_VISUALIZATION_ARTIFACTS.md",
    "docs/design/v0_12_0_visualization_artifacts.json",
    "docs/design/V0_13_0_PRIVATE_WEB_BACKEND_MVP.md",
    "docs/design/v0_13_0_private_web_backend_mvp.json",
    "docs/design/V0_16_0_DEPLOYMENT_READINESS_CHECKLIST.md",
    "deployment/README.md",
    "deployment/cloudflare-tunnel/README.md",
    "deployment/cloudflare-tunnel/public-hostname.example.md",
    "deployment/env/web.env.example",
    "deployment/security-checklist.md",
    "deployment/privacy-beta-checklist.md",
    "deployment/docker/docker-compose.example.yml",
    "deployment/systemd/audio-quality-humanizer-web.service.example",
    "deployment/server-rollout.md",
    "deployment/rollback.md",
    "deployment/smoke-test.md",
    "deployment/checklists/preflight.md",
    "deployment/checklists/post-deploy.md",
    "scripts/private-beta-smoke.sh",
    "docs/design/V0_11_0_COMPARE_METRICS.md",
    "docs/design/v0_11_0_compare_metrics.json",
    "docs/releases/V0_10_0_RELEASE_NOTES.md",
    "docs/releases/V0_11_0_RELEASE_NOTES.md",
    "docs/releases/V0_12_0_RELEASE_NOTES.md",
    "project_reborn/README.md",
    "project_reborn/catalog/PROJECT_REBORN_CATALOG.md",
    "project_reborn/audit/PROJECT_REBORN_AUDIT_MAP.md",
)

CLI_COMMANDS = (
    "inspect-metadata",
    "inspect-provenance",
    "clean-metadata",
    "analyze",
    "release-check",
    "compare",
    "visualize",
    "visualize-compare",
    "humanize",
    "doctor",
    "batch",
    "preset-eval",
    "validate-samples",
    "validation-status",
)


def scan_text(label: str, text: str) -> list[tuple[str, str]]:
    """Return unsafe matches as ``(label, term)`` tuples."""

    return [(label, term) for term in assert_no_unsafe_public_claims(text)]


def scan_public_files() -> list[tuple[str, str]]:
    findings: list[tuple[str, str]] = []
    for relative_path in PUBLIC_FILES:
        path = ROOT / relative_path
        findings.extend(scan_text(relative_path, path.read_text(encoding="utf-8")))
    return findings


def scan_cli_help() -> list[tuple[str, str]]:
    parser = _build_parser()
    findings = scan_text("cli:root", parser.format_help())
    version_stdout = io.StringIO()
    with contextlib.redirect_stdout(version_stdout):
        try:
            parser.parse_args(["--version"])
        except SystemExit as exc:
            if exc.code != 0:
                raise
    findings.extend(scan_text("cli:version", version_stdout.getvalue()))
    for command in CLI_COMMANDS:
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            try:
                parser.parse_args([command, "--help"])
            except SystemExit as exc:
                if exc.code != 0:
                    raise
        findings.extend(scan_text(f"cli:{command}", stdout.getvalue()))
    return findings


def main() -> int:
    findings = scan_public_files() + scan_cli_help()
    if findings:
        print("Unsafe public feature claims found:")
        for label, term in findings:
            print(f"{label}: {term}")
        return 1
    print("Safety scan passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
