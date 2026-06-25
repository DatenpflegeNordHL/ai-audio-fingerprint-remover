# v0.11.0 Compare Metrics Design

## Status

Implemented safe read-only compare metric expansion.

## Deep Search Decision

`not_needed_internal_repo_only`

Reason: this milestone uses internal math and existing project audio loading and analysis behavior. It does not require current external standards, current platform policies, current distributor rules, current external package behavior beyond already-installed dependencies, or third-party project behavior.

The Deep Search stop rule remains active. If future compare work needs current external information, implementation must stop until the user provides a research update or approves a constrained internal-only scope.

## Safety Boundary

Compare remains read-only.

Compare does not modify audio.

Compare does not add a new CLI command.

Compare does not change release-check scoring.

Compare does not change humanize processing.

Compare does not add watermark removal.

Compare does not add fingerprint removal.

Compare does not add detector bypass.

Compare does not add recognition APIs.

Compare does not add provenance logic.

Compare does not make platform-certification claims.

## Implemented Metrics

The existing `compare` workflow now adds a neutral `comparison_metrics` JSON object and a Markdown `Comparison Metrics` section.

Implemented fields:

- `rmse`
- `mean_absolute_error`
- `correlation`
- `snr_db_approx`
- `peak_before`
- `peak_after`
- `peak_delta`
- `rms_before`
- `rms_after`
- `rms_delta`
- `dynamic_range_before_db`
- `dynamic_range_after_db`
- `dynamic_range_delta_db`
- `spectral_centroid_before_hz`
- `spectral_centroid_after_hz`
- `spectral_centroid_delta_hz`
- `spectral_rolloff_before_hz`
- `spectral_rolloff_after_hz`
- `spectral_rolloff_delta_hz`
- `stereo_correlation_before`
- `stereo_correlation_after`
- `stereo_correlation_delta`
- `side_energy_ratio_before`
- `side_energy_ratio_after`
- `side_energy_ratio_delta`

Unavailable values are reported as `null`. JSON output must not contain NaN or Infinity.

## Rejected Metric Names

The implementation rejects unsafe metric names:

- `watermark_score`
- `fingerprint_score`
- `detector_score`
- `evasion_score`
- `bypass_score`
- `recognition_score`
- `provenance_score`
- `detectability_score`
- `origin_score`
- `source_attribution_score`

## Synthetic Test Plan

Synthetic tests cover:

- identical input
- gain-changed input
- clipped input
- silent input
- mono/stereo shape handling
- spectral change with different synthetic tones
- JSON safety
- forbidden wording and forbidden metric-name scan

## Real Local Validation Plan

Real local validation uses local user-supplied files only:

- `validation_samples/Dirty.wav`
- `final_exports/Dirty_D_Noir_balanced_release_check.wav`

Validation commands write ignored local artifacts under `v011_validation_outputs/`.

## No-Op Check Plan

The no-op check compares `validation_samples/Dirty.wav` to itself.

Expected result:

- near-zero difference metrics
- no invented changes
- no forbidden language
- no NaN or Infinity

## Generated Artifact Policy

Generated validation reports and generated audio must stay ignored and uncommitted.

Real audio files must not be committed.

## Project Reborn Boundary

`reborn_025` was used as a design reference only after manual text review.

No Project Reborn source code was copied, imported, executed, packaged, or exposed through the CLI.

The active implementation is newly written inside `audio_quality_humanizer/`.
