from __future__ import annotations

import importlib

from audio_quality_humanizer.safety import assert_no_unsafe_public_claims


def test_safety_checker_allows_boundary_denials():
    text = """
    This tool does not remove audio watermarks.
    This project is not a watermark remover.
    This tool does not bypass detectors.
    This project is not a detector bypass tool.
    This tool does not remove provenance markers.
    Does it make AI music undetectable?
    No. It does not bypass detectors.
    """

    assert assert_no_unsafe_public_claims(text) == []


def test_safety_checker_blocks_unsafe_feature_claims():
    text = """
    This feature removes watermarks, offers fingerprint removal,
    includes detector bypass mode, can evade detection, is undetectable,
    can remove all traces, neutralize watermark, verify removal,
    perform watermarks detected and removed checks, spectral watermark detection,
    watermark elimination, origin marker removal, and provenance suppression.
    """

    matches = assert_no_unsafe_public_claims(text)

    assert "removes watermarks" in matches
    assert "fingerprint removal" in matches
    assert "detector bypass" in matches
    assert "evade detection" in matches
    assert "undetectable" in matches
    assert "remove all traces" in matches
    assert "neutralize watermark" in matches
    assert "verify removal" in matches
    assert "watermarks detected and removed" in matches
    assert "spectral watermark detection" in matches
    assert "watermark elimination" in matches
    assert "origin marker removal" in matches
    assert "provenance suppression" in matches


def test_safety_scan_module_can_be_imported():
    module = importlib.import_module("tools.safety_scan")

    assert hasattr(module, "main")
    assert hasattr(module, "scan_text")


def test_safety_scan_text_reports_matches():
    module = importlib.import_module("tools.safety_scan")

    findings = module.scan_text("sample", "This mode can remove all traces and evade detection.")

    assert ("sample", "remove all traces") in findings
    assert ("sample", "evade detection") in findings
