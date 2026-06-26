"""Private beta workflow definitions for the web backend."""

from __future__ import annotations

from copy import deepcopy
from typing import Any


WORKFLOW_DEFINITIONS: dict[str, dict[str, Any]] = {
    "quick-scan": {
        "name": "quick-scan",
        "label": "Quick Scan",
        "description": "Check audio quality, metadata, and release readiness without modifying the file.",
        "steps": [
            {"name": "analyze", "label": "Analyze audio quality"},
            {"name": "inspect-metadata", "label": "Inspect metadata"},
            {"name": "release-check", "label": "Run release readiness check"},
            {"name": "visualize", "label": "Build visualization data"},
            {"name": "summary", "label": "Write workflow summary"},
        ],
        "options": {"visualization": True},
        "artifact_groups": {
            "Reports": ["quick_scan_summary.md", "analysis.json", "release_check.json"],
            "Metadata": ["metadata.json"],
            "Visuals": ["visualization.json"],
        },
    },
    "metadata-clean": {
        "name": "metadata-clean",
        "label": "Metadata Clean",
        "description": "Clean supported standard metadata fields and compare before/after metadata.",
        "steps": [
            {"name": "inspect-metadata-before", "label": "Inspect metadata before cleanup"},
            {"name": "clean-metadata", "label": "Clean metadata"},
            {"name": "inspect-metadata-after", "label": "Inspect metadata after cleanup"},
            {"name": "metadata-diff", "label": "Write metadata comparison"},
            {"name": "hashes", "label": "Write artifact integrity hashes"},
            {"name": "summary", "label": "Write workflow summary"},
        ],
        "options": {"metadata_scope": "supported-standard-fields"},
        "artifact_groups": {
            "Final Audio": ["cleaned_output.wav"],
            "Reports": ["metadata_clean_summary.md", "metadata_diff.md"],
            "Metadata": ["metadata_before.json", "metadata_after.json"],
            "Hashes": ["hashes.json"],
        },
    },
    "quality-naturalize": {
        "name": "quality-naturalize",
        "label": "Quality Naturalize",
        "description": "Apply conservative audio-quality micro-variations and compare before/after results.",
        "steps": [
            {"name": "release-check-before", "label": "Check release readiness before processing"},
            {"name": "quality-naturalize", "label": "Apply conservative audio-quality micro-variations"},
            {"name": "release-check-after", "label": "Check release readiness after processing"},
            {"name": "compare", "label": "Compare before and after audio"},
            {"name": "hashes", "label": "Write artifact integrity hashes"},
            {"name": "summary", "label": "Write workflow summary"},
        ],
        "options": {"preset": "subtle", "target": "streaming"},
        "artifact_groups": {
            "Final Audio": ["naturalized_output.wav"],
            "Reports": ["quality_naturalize_summary.md", "release_check_before.json", "release_check_after.json", "compare.json"],
            "Hashes": ["hashes.json"],
        },
    },
    "full-release-pass": {
        "name": "full-release-pass",
        "label": "Full Release Pass",
        "description": "Run cleanup, conservative naturalization, final checks, and reports in one private beta workflow.",
        "steps": [
            {"name": "inspect-metadata-before", "label": "Inspect metadata before cleanup"},
            {"name": "clean-metadata", "label": "Clean metadata"},
            {"name": "inspect-metadata-after", "label": "Inspect metadata after cleanup"},
            {"name": "release-check-before", "label": "Check release readiness after cleanup"},
            {"name": "quality-naturalize", "label": "Apply conservative audio-quality micro-variations"},
            {"name": "compare", "label": "Compare cleaned and final audio"},
            {"name": "release-check-final", "label": "Run final release readiness check"},
            {"name": "metadata-diff", "label": "Write metadata comparison"},
            {"name": "hashes", "label": "Write artifact integrity hashes"},
            {"name": "summary", "label": "Write workflow summary"},
        ],
        "options": {"preset": "subtle", "target": "streaming"},
        "artifact_groups": {
            "Final Audio": ["final_output.wav"],
            "Reports": ["workflow_summary.md", "workflow_summary.json", "release_check_before.json", "release_check_final.json", "compare.json", "metadata_diff.md"],
            "Metadata": ["metadata_before.json", "metadata_after.json"],
            "Hashes": ["hashes.json"],
        },
    },
}

WORKFLOW_NAMES = tuple(WORKFLOW_DEFINITIONS)


def workflow_status_steps(workflow_name: str) -> list[dict[str, Any]]:
    """Return pending status entries for a workflow."""

    return [
        {
            "name": step["name"],
            "label": step["label"],
            "status": "pending",
        }
        for step in WORKFLOW_DEFINITIONS[workflow_name]["steps"]
    ]


def workflow_config() -> list[dict[str, Any]]:
    """Return JSON-safe workflow config for the dashboard."""

    workflows = []
    for definition in WORKFLOW_DEFINITIONS.values():
        workflows.append(
            {
                "name": definition["name"],
                "label": definition["label"],
                "description": definition["description"],
                "steps": deepcopy(definition["steps"]),
                "options": deepcopy(definition["options"]),
                "artifact_groups": deepcopy(definition["artifact_groups"]),
            }
        )
    return workflows
