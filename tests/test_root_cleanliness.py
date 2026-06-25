from __future__ import annotations

from pathlib import Path

from tools.root_cleanliness_check import ROOT, find_offending_root_files


def test_root_cleanliness_check_passes_current_repo():
    assert find_offending_root_files(ROOT) == []


def test_root_cleanliness_helper_catches_bad_root_filenames(tmp_path):
    bad_path = tmp_path / "legacy_watermark_remover.py"
    bad_path.write_text("# historical placeholder\n", encoding="utf-8")
    (tmp_path / "README.md").write_text("# Allowed root file\n", encoding="utf-8")

    offenders = find_offending_root_files(tmp_path)

    assert offenders == [bad_path]
