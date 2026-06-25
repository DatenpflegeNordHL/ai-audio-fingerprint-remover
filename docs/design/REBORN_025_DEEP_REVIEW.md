# reborn_025 Deep Review

Status: deep review design-only

Implementation status: deferred

Deep Search decision: `not_needed_internal_repo_only`

Deep Search reason: this review only inspects local repository planning material and one local Project Reborn reference file as text. It makes no external factual claims and does not depend on current outside information.

Source inspected as text only: `project_reborn/source_drawer/reborn_025_reference.py`

No Project Reborn source was executed, imported, copied, packaged, or exposed.

## Review Summary

`reborn_025` contains a legacy comparison/report script with detector dependencies and unsafe report framing. Those parts remain rejected.

The only reusable direction is a future read-only compare/report design around neutral audio-quality deltas. That future work remains deferred and must pass the Candidate Reality Gate before any active package work begins.

## Safe Ideas For Future Design

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

## Rejected Ideas

Reject detector dependencies.

Reject watermark categories.

Reject attribution interpretation.

Reject recognition interpretation.

Reject provenance interpretation.

Reject any claim about detector success or failure.

Reject any score that implies bypass, evasion, concealment, removal, or reduced detectability.

## Deferred Future Scope

A future compare expansion may add neutral read-only metrics to the existing `compare` boundary. It must not add a new CLI command. It must not change current scoring without a separate approved design. It must not modify audio.

Future work must include:

- Synthetic tests for identical input, gain-only changes, clipped input, silence, mono/stereo shape handling, and sample-rate mismatch.
- Real local audio validation with user-supplied files before release.
- A no-op check proving identical input stays unchanged at the report boundary except for expected timestamps, paths, or runtime metadata.
- Safety wording review for JSON, Markdown, CLI help, README, and release notes.
- Confirmation that generated local validation reports and audio remain ignored and uncommitted.

## Current Decision

`reborn_025` stays deferred.

This document is planning and safety review only.

No code, DSP, scoring, CLI, packaging, or report behavior changes are approved by this review.
