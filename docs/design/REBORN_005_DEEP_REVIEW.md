# reborn_005 Deep Review

## Status

Manual text-only review. Design only. No implementation.

Implementation status: deferred.

## Deep Search Decision

`not_needed_internal_repo_only`

Reason:
This review only inspects local Project Reborn reference material and existing repository planning docs.

## Stop Rule

If future implementation needs current external standards, current library behavior, current platform policies, current legal guidance, current distributor behavior, or current third-party project behavior, stop and request a Codex update before continuing.

## Source Inspected

`project_reborn/source_drawer/reborn_005_reference.py`

Inspection method:
Manual text-only review.

No Project Reborn source was executed, imported, copied, packaged, or exposed.

## What the Legacy File Appears To Do

Based on text-only inspection, the file appears to combine metadata rewriting, broad audio analysis, processing statistics, chunked processing, detector-oriented analysis, spectral processing, statistical-pattern alteration, timing changes, directory processing, and legacy command-line behavior.

The metadata-related behavior appears to inspect and rewrite MP3, WAV, FLAC, and AIFF container metadata; track removed or changed tag categories; show metadata before or after processing; and search file bytes for matching text patterns in an aggressive mode.

The processing and statistics behavior appears to track files processed, metadata categories changed, operation timing, total runtime, memory usage when optional process information is available, cache counts, and chunk-processing flow.

The analysis-metric behavior appears to calculate spectral entropy, frequency-distribution summaries, spectral centroid, spectral spread, spectral skewness, spectral kurtosis, high-frequency energy ratio, sample entropy, and spectral flatness.

The chunking behavior appears to split long audio into overlapping chunks, run a passed processing function on each chunk, keep an original chunk on failure, and reconstruct chunks with cross-fades and weight normalization.

The legacy file also contains unsafe remover, detector, attribution, recognizability, and concealment framing. Those parts are rejected and are not product functionality.

## Safe Ideas For Possible Future Design

- Metadata inspection for ordinary container tags.
- Metadata change reporting with explicit before/after categories.
- Privacy-safe container tag cleanup summary limited to documented user-editable fields.
- Processing runtime statistics.
- Operation timing statistics.
- Basic analysis statistics for audio quality reports.
- Spectral entropy as a neutral audio texture metric.
- Spectral flatness as a neutral audio texture metric.
- Simple complexity metrics as neutral analysis aids.
- Chunked processing structure only if rewritten safely and only if needed.

## Unsafe or Rejected Ideas

- No fingerprint removal.
- No watermark removal.
- No pattern normalization for attribution targeting.
- No recognizability targeting.
- No detector targeting.
- No provenance removal.
- No origin marker removal.
- No C2PA marker removal.
- No source-attribution removal.
- No evasion or bypass framing.
- No legacy CLI behavior.
- No user-facing claims tied to concealment, removal, or detectability reduction.

## Candidate Reality Gate Plan

Any future implementation must pass the Candidate Reality Gate.

### Synthetic Tests

Future tests would need to cover:

- normal metadata-bearing file fixture
- file with no metadata
- malformed or unusual metadata
- silent or quiet audio for analysis stats
- short audio
- mono/stereo files
- JSON safety
- forbidden wording scan

### Real Local Audio Validation

Future user-facing metadata or analysis behavior must be validated with local user-supplied files.

Do not commit:

- real audio files
- generated metadata reports
- generated validation outputs

### No-Op Check

Future behavior must prove:

- inspect-only commands do not modify files
- cleanup commands only change documented metadata fields
- analysis stats are populated from real calculations
- reports do not invent changes
- JSON contains no NaN or Infinity

## Proposed Future Scope

Design only.

Possible future safe milestone:
`v0.12.0 metadata/privacy and analysis stats`

Allowed future directions:

- metadata inspection/reporting
- metadata change summary
- neutral processing statistics
- neutral analysis texture metrics

Not approved in this review:

- active implementation
- new CLI behavior
- metadata cleanup changes
- audio processing changes
- release-check scoring changes

## Deferred

Implementation remains deferred.

No active package code changes are approved by this review.
