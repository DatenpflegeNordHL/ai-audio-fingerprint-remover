# Project Reborn Audit Map

## Purpose

This is a static audit only. No Project Reborn code was executed, imported, packaged, or exposed through CLI.

## Principle

The old filename is not the package. Historical filenames are traceability labels only.

Audit terms are review flags, not product claims. No audit result makes a file safe to import.

## Summary

- Total files: 27
- Parsed AST: 21
- Text only: 6
- Parse errors: 0
- Binary/unreadable: 0

## Priority Counts

| Priority | Count |
| --- | --- |
| high | 25 |
| low | 2 |

## Category Counts

| Category | Count |
| --- | --- |
| audio_quality_reference | 3 |
| comparison_reference | 11 |
| documentation_reference | 1 |
| metadata_privacy_reference | 3 |
| performance_reference | 3 |
| report_reference | 1 |
| test_reference | 5 |

## Candidate Counts

| Candidate | Count |
| --- | --- |
| audio_quality_cleanup | 25 |
| comparison | 16 |
| conservative_repair | 16 |
| documentation_notes | 3 |
| metadata_privacy_cleanup | 3 |
| mix_diagnostics | 25 |
| performance | 14 |
| release_readiness | 13 |
| reporting | 12 |
| sound_relief | 15 |
| test_ideas | 5 |

## Entries

| Reborn ID | Current Path | Historical Filename | Category | Priority | Review Status | Safe Future Use Candidates | Recommendation |
| --- | --- | --- | --- | --- | --- | --- | --- |
| reborn_001 | `project_reborn/source_drawer/reborn_001_reference.py` | advanced_steganography_detector.py | comparison_reference | high | candidate_for_safe_rewrite | audio_quality_cleanup, comparison, mix_diagnostics, sound_relief | Review manually for possible comparison or report ideas. |
| reborn_002 | `project_reborn/source_drawer/reborn_002_reference.py` | advanced_watermark_analysis.py | comparison_reference | high | candidate_for_safe_rewrite | audio_quality_cleanup, comparison, mix_diagnostics, release_readiness, reporting | Review manually for possible comparison or report ideas. |
| reborn_003 | `project_reborn/source_drawer/reborn_003_reference.py` | aggressive_watermark_remover.py | performance_reference | high | candidate_for_safe_rewrite | audio_quality_cleanup, conservative_repair, mix_diagnostics, performance, release_readiness, sound_relief | Review manually for possible performance ideas. |
| reborn_004 | `project_reborn/source_drawer/reborn_004_backup_reference` | aggressive_watermark_remover.py.backup_20250706_105051 | performance_reference | high | candidate_for_safe_rewrite | audio_quality_cleanup, conservative_repair, mix_diagnostics, performance, release_readiness, sound_relief | Review manually for possible performance ideas. |
| reborn_005 | `project_reborn/source_drawer/reborn_005_reference.py` | ai_audio_fingerprint_remover.py | metadata_privacy_reference | high | candidate_for_safe_rewrite | audio_quality_cleanup, comparison, conservative_repair, metadata_privacy_cleanup, mix_diagnostics, performance, release_readiness, reporting, sound_relief | Review manually for possible metadata/privacy cleanup ideas. |
| reborn_006 | `project_reborn/source_drawer/reborn_006_backup_reference` | ai_audio_fingerprint_remover.py.backup_20250706_105051 | metadata_privacy_reference | high | candidate_for_safe_rewrite | audio_quality_cleanup, comparison, conservative_repair, metadata_privacy_cleanup, mix_diagnostics, performance, release_readiness, reporting, sound_relief | Review manually for possible metadata/privacy cleanup ideas. |
| reborn_007 | `project_reborn/source_drawer/reborn_007_reference.py` | apply_comprehensive_fixes.py | comparison_reference | high | candidate_for_safe_rewrite | audio_quality_cleanup, comparison, conservative_repair, mix_diagnostics, performance, reporting, sound_relief | Review manually for possible comparison or report ideas. |
| reborn_008 | `project_reborn/source_drawer/reborn_008_reference.py` | audio_processing_fixes.py | comparison_reference | high | candidate_for_safe_rewrite | audio_quality_cleanup, comparison, conservative_repair, mix_diagnostics, performance, release_readiness, sound_relief | Review manually for possible comparison or report ideas. |
| reborn_009 | `project_reborn/source_drawer/reborn_009_reference.py` | enhanced_suno_detector.py | comparison_reference | high | candidate_for_safe_rewrite | audio_quality_cleanup, comparison, mix_diagnostics, performance, release_readiness, sound_relief | Review manually for possible comparison or report ideas. |
| reborn_010 | `project_reborn/source_drawer/reborn_010_sample_reference.html` | file_example_WAV_1MG.html | documentation_reference | low | static_audit_only | documentation_notes | Keep as notes only unless manual review identifies safe documentation value. |
| reborn_011 | `project_reborn/source_drawer/reborn_011_reference.py` | integrated_system.py | comparison_reference | high | candidate_for_safe_rewrite | audio_quality_cleanup, comparison, conservative_repair, mix_diagnostics, performance, release_readiness, reporting | Review manually for possible comparison or report ideas. |
| reborn_012 | `project_reborn/source_drawer/reborn_012_reference.py` | next_gen_remover.py | comparison_reference | high | candidate_for_safe_rewrite | audio_quality_cleanup, comparison, conservative_repair, mix_diagnostics, performance, release_readiness, sound_relief | Review manually for possible comparison or report ideas. |
| reborn_013 | `project_reborn/source_drawer/reborn_013_reference.py` | neural_watermark_detector.py | comparison_reference | high | candidate_for_safe_rewrite | audio_quality_cleanup, comparison, mix_diagnostics, performance, release_readiness, sound_relief | Review manually for possible comparison or report ideas. |
| reborn_014 | `project_reborn/source_drawer/reborn_014_reference.py` | optimized_suno_detector.py | performance_reference | high | candidate_for_safe_rewrite | audio_quality_cleanup, mix_diagnostics, performance | Review manually for possible performance ideas. |
| reborn_015 | `project_reborn/source_drawer/reborn_015_reference.py` | performance_optimizer.py | comparison_reference | high | candidate_for_safe_rewrite | audio_quality_cleanup, comparison, mix_diagnostics, performance, release_readiness | Review manually for possible comparison or report ideas. |
| reborn_016 | `project_reborn/source_drawer/reborn_016_reference.py` | quick_comparison.py | comparison_reference | high | candidate_for_safe_rewrite | audio_quality_cleanup, comparison, mix_diagnostics, reporting | Review manually for possible comparison or report ideas. |
| reborn_017 | `project_reborn/source_drawer/reborn_017_reference.py` | quick_test_fixes.py | audio_quality_reference | high | candidate_for_safe_rewrite | audio_quality_cleanup, conservative_repair, mix_diagnostics | Review manually for possible safe rewrite into audio_quality_humanizer.analysis. |
| reborn_018 | `project_reborn/source_drawer/reborn_018_reference.py` | sota_watermark_remover.py | audio_quality_reference | high | candidate_for_safe_rewrite | audio_quality_cleanup, conservative_repair, mix_diagnostics, release_readiness, sound_relief | Review manually for possible safe rewrite into audio_quality_humanizer.analysis. |
| reborn_019 | `project_reborn/source_drawer/reborn_019_backup_reference` | sota_watermark_remover.py.backup_20250706_105051 | audio_quality_reference | high | candidate_for_safe_rewrite | audio_quality_cleanup, conservative_repair, mix_diagnostics, release_readiness, sound_relief | Review manually for possible safe rewrite into audio_quality_humanizer.analysis. |
| reborn_020 | `project_reborn/source_drawer/reborn_020_notes.txt` | suno_analysis.txt | report_reference | high | candidate_for_safe_rewrite | audio_quality_cleanup, documentation_notes, mix_diagnostics, reporting | Needs manual review; do not infer behavior from historical filename. |
| reborn_021 | `project_reborn/source_drawer/reborn_021_reference.py` | test_all_methods.py | test_reference | low | static_audit_only | test_ideas | Review manually for test ideas only. |
| reborn_022 | `project_reborn/source_drawer/reborn_022_reference.py` | test_audio_fixes.py | test_reference | high | candidate_for_safe_rewrite | audio_quality_cleanup, comparison, conservative_repair, mix_diagnostics, performance, reporting, test_ideas | Review manually for test ideas only. |
| reborn_023 | `project_reborn/source_drawer/reborn_023_reference.py` | test_comprehensive_fixes.py | test_reference | high | candidate_for_safe_rewrite | audio_quality_cleanup, conservative_repair, mix_diagnostics, reporting, sound_relief, test_ideas | Review manually for test ideas only. |
| reborn_024 | `project_reborn/source_drawer/reborn_024_reference.py` | test_fixes.py | test_reference | high | candidate_for_safe_rewrite | audio_quality_cleanup, conservative_repair, mix_diagnostics, test_ideas | Review manually for test ideas only. |
| reborn_025 | `project_reborn/source_drawer/reborn_025_reference.py` | watermark_comparison.py | comparison_reference | high | candidate_for_safe_rewrite | audio_quality_cleanup, comparison, mix_diagnostics, reporting | Review manually for possible comparison or report ideas. |
| reborn_026 | `project_reborn/source_drawer/reborn_026_reference.py` | watermark_effectiveness_tester.py | test_reference | high | candidate_for_safe_rewrite | audio_quality_cleanup, comparison, conservative_repair, mix_diagnostics, reporting, sound_relief, test_ideas | Review manually for test ideas only. |
| reborn_027 | `project_reborn/source_drawer/reborn_027_notes.md` | ENHANCEMENT_SUMMARY.md | metadata_privacy_reference | high | candidate_for_safe_rewrite | audio_quality_cleanup, comparison, conservative_repair, documentation_notes, metadata_privacy_cleanup, mix_diagnostics, performance, reporting, sound_relief | Review manually for possible metadata/privacy cleanup ideas. |
