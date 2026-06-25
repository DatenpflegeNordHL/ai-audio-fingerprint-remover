# Project Reborn Top-5 Manual Review Plan

Current active package: `audio-quality-humanizer`

Current version target: `0.10.0`

Internal drawer: `Project Reborn`

Source audit: `project_reborn/audit/project_reborn_audit_map.json`

This plan is based on static audit data plus manual text-only review of five selected Project Reborn files. No Project Reborn code was executed, imported, copied into `audio_quality_humanizer/`, packaged, or exposed through the CLI. Planning notes are future-review inputs only, not product claims. A selected entry is still inert reference material and remains outside the active package boundary.

Old filenames are historical labels only. Future work must inspect behavior, design a new implementation, rename concepts into the current product language, add tests, and pass the Project Reborn check and safety scan before any useful idea can move into active code.

## Selection Summary

| Rank | Reborn ID | Planning Direction | Future Module | Next Step |
| --- | --- | --- | --- | --- |
| 1 | `reborn_008` | Processing guardrails and signal hygiene | `audio_quality_humanizer.processing` | `candidate_for_v0_10_design` |
| 2 | `reborn_015` | Workflow performance harness design | `audio_quality_humanizer.validation` | `candidate_for_v0_10_design` |
| 3 | `reborn_022` | Audio-quality regression test ideas | `audio_quality_humanizer.validation` | `candidate_for_v0_10_design` |
| 4 | `reborn_025` | Comparison report metrics review | `audio_quality_humanizer.compare` | `needs_deeper_manual_review` |
| 5 | `reborn_005` | Metadata privacy and analysis stats review | `audio_quality_humanizer.metadata` | `needs_deeper_manual_review` |

## v0.10.0 Status

- Candidate 1, `reborn_008`, moved into the v0.10.0 safe-core implementation.
- Candidate 2, `reborn_015`, moved into the v0.10.0 minimal implementation.
- Candidate 3, `reborn_022`, moved into v0.10.0 synthetic regression scaffolding.
- Candidate 4, `reborn_025`, is deferred for deeper manual review.
- Candidate 5, `reborn_005`, is deferred for deeper manual review.
- Project Reborn remains reference-only, non-installed, unpackaged, and hidden from the CLI.

## v0.10.3 Planning Gate

- Candidate Reality Gate is required before future feature candidates move into active package work.
- Deep Search stop rule is required when current external information is needed.
- `reborn_025` has a deep-review design-only document and remains deferred.
- Future implementation must include real local audio validation and a no-op check before user-facing audio behavior ships.
- Generated local validation outputs must stay ignored and uncommitted.

## v0.11.0 Status

- `reborn_025` safe read-only compare metric ideas were rewritten from first principles inside the active package.
- The v0.11.0 implementation extends the existing `compare` workflow only.
- No Project Reborn source code was copied, imported, executed, packaged, or exposed.
- `reborn_005` remains deferred pending separate deep manual review.

## Manual Review Notes

### 1. `reborn_008`

Path: `project_reborn/source_drawer/reborn_008_reference.py`

Historical filename: `audio_processing_fixes.py`

Why it is promising:

- The static audit marked it high priority and found audio-quality cleanup, conservative repair, mix diagnostics, performance, release-readiness, and sound-relief candidates.
- Text-only review found guard-oriented helper names such as `validate_audio_content`, `safe_filter_design`, `safe_filter_apply`, `safe_nan_cleanup`, `safe_time_stretch`, `safe_stft_processing`, and `harmonic_enhancement`.
- The reusable direction is a newly written set of conservative validation and signal-hygiene helpers, not the legacy feature framing.

Safe observed ideas to consider:

- Validate signal arrays before and after processing.
- Bound filter parameters by sample rate, audio length, and filter stability.
- Clean NaN and infinite values with explicit fallback behavior.
- Add short-audio and STFT guardrails for unusual inputs.
- Explore harmonic enhancement as a conservative quality-control idea only.

Parts to ignore:

- Legacy functions and class names tied to watermark removal or suspicious-tone behavior.
- Any logic intended to change recognizability, attribution, provenance, or detector behavior.
- Any behavior that treats detection results as a processing target.

### 2. `reborn_015`

Path: `project_reborn/source_drawer/reborn_015_reference.py`

Historical filename: `performance_optimization.py`

Why it is promising:

- The static audit marked it high priority with performance, audio-quality cleanup, mix diagnostics, and release-readiness candidates.
- Text-only review found `PerformanceConfig`, `PerformanceOptimizer`, `MemoryMonitor`, `StreamingProcessor`, chunk splitting, chunk reconstruction, batch feature processing, and benchmark scaffolding.
- The reusable direction is operational structure for validation and performance checks, not a new audio effect.

Safe observed ideas to consider:

- Chunk size and overlap configuration for large-file workflows.
- Sequential chunk processing with fallback to the original chunk on failure.
- Reconstruction checks that preserve length and channel structure.
- Memory usage reporting as diagnostic metadata.
- Benchmark scaffolding for comparing workflow cost across presets or validation jobs.

Parts to ignore:

- GPU, JIT, multiprocessing, and `psutil` dependency assumptions unless a new design proves they are needed.
- Any chunk worker that calls legacy processing behavior.
- Any real-time workflow until the active CLI has a clear user need and safety gates.

### 3. `reborn_022`

Path: `project_reborn/source_drawer/reborn_022_reference.py`

Historical filename: `test_improvements.py`

Why it is promising:

- The static audit marked it high priority and found test ideas, audio-quality cleanup, mix diagnostics, conservative repair, release-readiness, and sound-relief candidates.
- Text-only review found synthetic-audio generation, audio metric helpers, SNR calculation, short-audio cases, edge cases, and preservation-style tests.
- The reusable direction is new regression coverage for existing quality workflows.

Safe observed ideas to consider:

- Small synthetic audio fixtures that avoid external media.
- Edge-case tests for NaN values, quiet input, short clips, and mono/stereo shapes.
- SNR and broad-quality metrics for regression assertions.
- Tests that verify conservative processing preserves core audio properties.

Parts to ignore:

- Legacy imports from old remover modules.
- Assertions about detection or removal outcomes.
- Any test naming that implies source-attribution or detector effects.

### 4. `reborn_025`

Path: `project_reborn/source_drawer/reborn_025_reference.py`

Historical filename: `watermark_comparison.py`

Why it is promising:

- The static audit marked it high priority with comparison, reporting, mix diagnostics, and audio-quality cleanup candidates.
- Text-only review found basic comparison metrics, spectral-content comparison, quality-metric calculation, and report generation structure.
- The reusable direction is a neutral comparison report that extends existing read-only compare behavior.

Safe observed ideas to consider:

- Basic metrics such as SNR, correlation, RMSE, and dynamic-range change.
- Spectral-content summaries by frequency band.
- Quality-metric deltas such as spectral centroid, rolloff, RMS, and bandwidth.
- A structured report layout for before/after quality checks.

Parts to ignore:

- The legacy analyzer class name and any detector dependency.
- Any category, score, or report section about watermark outcomes.
- Any interpretation that compare can prove attribution, recognition, provenance, or detector changes.

### 5. `reborn_005`

Path: `project_reborn/source_drawer/reborn_005_reference.py`

Historical filename: `ai_audio_fingerprint_remover.py`

Why it is promising:

- The static audit marked it high priority with metadata/privacy cleanup, reporting, performance, conservative repair, comparison, mix diagnostics, and release-readiness candidates.
- Text-only review found reusable structure names such as `ProcessingConfig`, `ProcessingStats`, `AudioProcessor`, `AdvancedAudioAnalysis`, `clean_metadata_comprehensive`, `calculate_spectral_entropy`, `calculate_complexity_measures`, and chunk reconstruction helpers.
- The reusable direction is a clean metadata/statistics and analysis-stats review, with a high safety bar because the file is dominated by legacy unsafe framing.

Safe observed ideas to consider:

- Processing configuration and timing statistics as product-neutral operational metadata.
- Metadata inspection and explicit reporting of changed container tags.
- Spectral entropy, flatness, and simple complexity metrics as audio-quality analysis candidates, after renaming and redefining their purpose.
- Chunked processing structure for long files, only if rewritten with current safety gates.

Parts to ignore:

- Any fingerprint, watermark, or remover behavior.
- Any pattern-normalization, attribution-targeting, or recognizability-targeting logic.
- Legacy CLI behavior and user-facing claims.

## Feature Direction

The strongest future direction is a v0.10 design pass around three safe areas:

- Conservative processing guardrails and signal hygiene.
- Read-only comparison and quality-report metrics.
- Validation and performance scaffolding for existing workflows.

`reborn_005` needs deeper review before design work because it contains high legacy unsafe framing. All Project Reborn source files remain reference-only unless a new implementation is designed, tested, safety-reviewed, and rewritten from first principles in the active package.
