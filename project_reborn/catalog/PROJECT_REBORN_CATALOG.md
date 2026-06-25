# Project Reborn Catalog

Project Reborn is a non-installed reference drawer for historical experimental scripts. It exists only to preserve material for future safe review.

Safety boundary: nothing in Project Reborn is active product code, imported by `audio_quality_humanizer`, packaged into the wheel, or exposed through the CLI. No file in Project Reborn is trusted automatically.

Principle: the old filename is not the package. Historical filenames are traceability labels only and must not be used to infer behavior. Future review must inspect behavior, not names.

Any useful logic must be rewritten safely into the main package later, with tests, safety scan coverage, CLI smoke coverage, and build validation.

Static audit map: `project_reborn/audit/PROJECT_REBORN_AUDIT_MAP.md`.

| Reborn ID | Current Path | Historical Filename | Category | Status | Future Use Candidates | Audit Priority | Review Status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| reborn_001 | project_reborn/source_drawer/reborn_001_reference.py | advanced_steganography_detector.py | comparison_reference | reference only, not installed | audio_quality_cleanup, comparison, mix_diagnostics, sound_relief | high | candidate_for_safe_rewrite |
| reborn_002 | project_reborn/source_drawer/reborn_002_reference.py | advanced_watermark_analysis.py | comparison_reference | reference only, not installed | audio_quality_cleanup, comparison, mix_diagnostics, release_readiness, reporting | high | candidate_for_safe_rewrite |
| reborn_003 | project_reborn/source_drawer/reborn_003_reference.py | aggressive_watermark_remover.py | performance_reference | reference only, not installed | audio_quality_cleanup, conservative_repair, mix_diagnostics, performance, release_readiness, sound_relief | high | candidate_for_safe_rewrite |
| reborn_004 | project_reborn/source_drawer/reborn_004_backup_reference | aggressive_watermark_remover.py.backup_20250706_105051 | performance_reference | reference only, not installed | audio_quality_cleanup, conservative_repair, mix_diagnostics, performance, release_readiness, sound_relief | high | candidate_for_safe_rewrite |
| reborn_005 | project_reborn/source_drawer/reborn_005_reference.py | ai_audio_fingerprint_remover.py | metadata_privacy_reference | reference only, not installed | audio_quality_cleanup, comparison, conservative_repair, metadata_privacy_cleanup, mix_diagnostics, performance, release_readiness, reporting, sound_relief | high | candidate_for_safe_rewrite |
| reborn_006 | project_reborn/source_drawer/reborn_006_backup_reference | ai_audio_fingerprint_remover.py.backup_20250706_105051 | metadata_privacy_reference | reference only, not installed | audio_quality_cleanup, comparison, conservative_repair, metadata_privacy_cleanup, mix_diagnostics, performance, release_readiness, reporting, sound_relief | high | candidate_for_safe_rewrite |
| reborn_007 | project_reborn/source_drawer/reborn_007_reference.py | apply_comprehensive_fixes.py | comparison_reference | reference only, not installed | audio_quality_cleanup, comparison, conservative_repair, mix_diagnostics, performance, reporting, sound_relief | high | candidate_for_safe_rewrite |
| reborn_008 | project_reborn/source_drawer/reborn_008_reference.py | audio_processing_fixes.py | comparison_reference | reference only, not installed | audio_quality_cleanup, comparison, conservative_repair, mix_diagnostics, performance, release_readiness, sound_relief | high | candidate_for_safe_rewrite |
| reborn_009 | project_reborn/source_drawer/reborn_009_reference.py | enhanced_suno_detector.py | comparison_reference | reference only, not installed | audio_quality_cleanup, comparison, mix_diagnostics, performance, release_readiness, sound_relief | high | candidate_for_safe_rewrite |
| reborn_010 | project_reborn/source_drawer/reborn_010_sample_reference.html | file_example_WAV_1MG.html | documentation_reference | reference only, not installed | documentation_notes | low | static_audit_only |
| reborn_011 | project_reborn/source_drawer/reborn_011_reference.py | integrated_system.py | comparison_reference | reference only, not installed | audio_quality_cleanup, comparison, conservative_repair, mix_diagnostics, performance, release_readiness, reporting | high | candidate_for_safe_rewrite |
| reborn_012 | project_reborn/source_drawer/reborn_012_reference.py | next_gen_remover.py | comparison_reference | reference only, not installed | audio_quality_cleanup, comparison, conservative_repair, mix_diagnostics, performance, release_readiness, sound_relief | high | candidate_for_safe_rewrite |
| reborn_013 | project_reborn/source_drawer/reborn_013_reference.py | neural_watermark_detector.py | comparison_reference | reference only, not installed | audio_quality_cleanup, comparison, mix_diagnostics, performance, release_readiness, sound_relief | high | candidate_for_safe_rewrite |
| reborn_014 | project_reborn/source_drawer/reborn_014_reference.py | optimized_suno_detector.py | performance_reference | reference only, not installed | audio_quality_cleanup, mix_diagnostics, performance | high | candidate_for_safe_rewrite |
| reborn_015 | project_reborn/source_drawer/reborn_015_reference.py | performance_optimizer.py | comparison_reference | reference only, not installed | audio_quality_cleanup, comparison, mix_diagnostics, performance, release_readiness | high | candidate_for_safe_rewrite |
| reborn_016 | project_reborn/source_drawer/reborn_016_reference.py | quick_comparison.py | comparison_reference | reference only, not installed | audio_quality_cleanup, comparison, mix_diagnostics, reporting | high | candidate_for_safe_rewrite |
| reborn_017 | project_reborn/source_drawer/reborn_017_reference.py | quick_test_fixes.py | audio_quality_reference | reference only, not installed | audio_quality_cleanup, conservative_repair, mix_diagnostics | high | candidate_for_safe_rewrite |
| reborn_018 | project_reborn/source_drawer/reborn_018_reference.py | sota_watermark_remover.py | audio_quality_reference | reference only, not installed | audio_quality_cleanup, conservative_repair, mix_diagnostics, release_readiness, sound_relief | high | candidate_for_safe_rewrite |
| reborn_019 | project_reborn/source_drawer/reborn_019_backup_reference | sota_watermark_remover.py.backup_20250706_105051 | audio_quality_reference | reference only, not installed | audio_quality_cleanup, conservative_repair, mix_diagnostics, release_readiness, sound_relief | high | candidate_for_safe_rewrite |
| reborn_020 | project_reborn/source_drawer/reborn_020_notes.txt | suno_analysis.txt | report_reference | reference only, not installed | audio_quality_cleanup, documentation_notes, mix_diagnostics, reporting | high | candidate_for_safe_rewrite |
| reborn_021 | project_reborn/source_drawer/reborn_021_reference.py | test_all_methods.py | test_reference | reference only, not installed | test_ideas | low | static_audit_only |
| reborn_022 | project_reborn/source_drawer/reborn_022_reference.py | test_audio_fixes.py | test_reference | reference only, not installed | audio_quality_cleanup, comparison, conservative_repair, mix_diagnostics, performance, reporting, test_ideas | high | candidate_for_safe_rewrite |
| reborn_023 | project_reborn/source_drawer/reborn_023_reference.py | test_comprehensive_fixes.py | test_reference | reference only, not installed | audio_quality_cleanup, conservative_repair, mix_diagnostics, reporting, sound_relief, test_ideas | high | candidate_for_safe_rewrite |
| reborn_024 | project_reborn/source_drawer/reborn_024_reference.py | test_fixes.py | test_reference | reference only, not installed | audio_quality_cleanup, conservative_repair, mix_diagnostics, test_ideas | high | candidate_for_safe_rewrite |
| reborn_025 | project_reborn/source_drawer/reborn_025_reference.py | watermark_comparison.py | comparison_reference | reference only, not installed | audio_quality_cleanup, comparison, mix_diagnostics, reporting | high | candidate_for_safe_rewrite |
| reborn_026 | project_reborn/source_drawer/reborn_026_reference.py | watermark_effectiveness_tester.py | test_reference | reference only, not installed | audio_quality_cleanup, comparison, conservative_repair, mix_diagnostics, reporting, sound_relief, test_ideas | high | candidate_for_safe_rewrite |
| reborn_027 | project_reborn/source_drawer/reborn_027_notes.md | ENHANCEMENT_SUMMARY.md | metadata_privacy_reference | reference only, not installed | audio_quality_cleanup, comparison, conservative_repair, documentation_notes, metadata_privacy_cleanup, mix_diagnostics, performance, reporting, sound_relief | high | candidate_for_safe_rewrite |

No file in Project Reborn is active product code.

Any useful logic must be rewritten safely into the main package later.

Future review must inspect behavior, not names.
