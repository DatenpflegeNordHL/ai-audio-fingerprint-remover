# reborn_025 Deep Review

## Status

Manual text-only review. Design only. No implementation.

Implementation status: deferred

## Deep Search Decision

`not_needed_internal_repo_only`

Reason:
This review only inspects local Project Reborn reference material and current active compare boundaries.

## Stop Rule

If future implementation needs current external standards, current library behavior, current platform policies, or current third-party project behavior, stop and request a Codex update before continuing.

Source inspected as text only: `project_reborn/source_drawer/reborn_025_reference.py`

No Project Reborn source was executed, imported, copied, packaged, or exposed.

## What the Legacy File Appears To Do

Based on text-only inspection, the file appears to load original and processed audio, convert both inputs to mono for analysis, align length, calculate basic quality deltas, call a detector-dependent branch, calculate spectral-band and quality-metric deltas, and generate a textual before/after report.

The only reusable direction is a future read-only compare/report design around neutral audio-quality deltas. That future work remains deferred and must pass the Candidate Reality Gate before any active package work begins.

## Safe Ideas

- SNR-style comparison.
- RMSE-style comparison.
- Correlation-style comparison.
- Dynamic range delta.
- Spectral centroid delta.
- Spectral rolloff delta.
- Spectral bandwidth delta.
- RMS or approximate loudness delta.
- Frequency-band summary deltas.
- Structured before/after quality report sections.

## Unsafe or Rejected Ideas

Reject detector dependencies.

Reject watermark categories.

Reject attribution interpretation.

Reject recognition interpretation.

Reject provenance interpretation.

Reject any claim about detector success or failure.

Reject any score that implies bypass, evasion, concealment, removal, or reduced detectability.

## Candidate Reality Gate Plan

Future implementation must be tested before release.

### Synthetic Tests

- Synthetic tests for identical input, gain-only changes, clipped input, silence, mono/stereo shape handling, and sample-rate mismatch.

### Real Local Audio Validation

Require validation against local user-supplied audio files, but do not commit them.

Use placeholder paths only:

```bash
ai-humanizer compare local_input_original.wav local_input_processed.wav \
  --target club \
  --report local_compare.json \
  --markdown local_compare.md
```

### No-Op Check

The future compare metrics must show different values when comparing:

- identical files
- gain-changed files
- clipped files
- sanitized files
- stereo-width changed synthetic files

## Proposed v0.11.0 Scope

Design only:

- add neutral read-only compare metric expansion
- no new CLI command
- extend existing `compare`
- report metrics under safe names
- no detector/provenance/recognition language

## Deferred

Safe read-only implementation completed in v0.11.0 as a newly written active-package compare metric expansion.

No code, DSP, scoring, CLI, packaging, or report behavior changes are approved by this review.

The v0.11.0 implementation did not copy, import, execute, package, or expose Project Reborn source code.
