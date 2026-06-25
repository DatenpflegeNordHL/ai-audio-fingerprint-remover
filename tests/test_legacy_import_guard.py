from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIRS = [
    ROOT / "audio_quality_humanizer" / "analysis",
    ROOT / "audio_quality_humanizer" / "processing",
    ROOT / "audio_quality_humanizer" / "workflows",
    ROOT / "audio_quality_humanizer" / "reports",
    ROOT / "audio_quality_humanizer" / "validation",
]
FORBIDDEN_REFERENCES = [
    "ai_audio_fingerprint_remover",
    "aggressive_watermark_remover",
    "sota_watermark_remover",
    "enhanced_suno_detector",
    "optimized_suno_detector",
    "watermark_effectiveness_tester",
    "advanced_watermark_analysis",
    "advanced_steganography_detector",
    "neural_watermark_detector",
    "next_gen_remover",
]


def test_new_source_packages_do_not_reference_legacy_modules():
    for directory in SOURCE_DIRS:
        for path in directory.glob("*.py"):
            source = path.read_text(encoding="utf-8")
            for reference in FORBIDDEN_REFERENCES:
                assert reference not in source, f"{path} references {reference}"
