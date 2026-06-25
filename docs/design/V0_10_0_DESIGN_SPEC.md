# v0.10.0 Design Spec

Status: implemented safe core

Active package: `audio-quality-humanizer`

Source planning documents:

- `project_reborn/planning/PROJECT_REBORN_TOP5_PLAN.md`
- `project_reborn/audit/PROJECT_REBORN_AUDIT_MAP.md`

## Safety Boundary

The v0.10.0 safe core was rewritten from first principles inside `audio_quality_humanizer/`.

No Project Reborn source code was copied, imported, executed, packaged, or exposed through the CLI.

Project Reborn remains a non-installed internal reference drawer.

Signal guardrails are quality and workflow-safety checks. They are not attribution, recognition, provenance, detector, bypass, or evasion tools.

Performance metadata is operational metadata only.

Regression scaffolding uses synthetic audio only.

## Non-Goals

- Do not add watermark removal.
- Do not add fingerprint removal.
- Do not add detector bypass.
- Do not add recognition failure testing.
- Do not add provenance removal.
- Do not add origin marker removal.
- Do not add C2PA marker removal.
- Do not add source-attribution removal.
- Do not add detector APIs.
- Do not add recognition APIs.
- Do not add bypass or evasion APIs.
- Do not add claims about reduced detectability.
- Do not modify validation audio or final exports as part of guardrail reporting.

## Implemented Scope

Candidate 1, `reborn_008`, is implemented as newly written processing guardrails and signal-hygiene reporting in `audio_quality_humanizer.processing.guardrails`.

The implemented guardrails detect empty arrays, NaN values, infinite values, non-numeric arrays, silent arrays, peaks above full scale, shape changes, length changes, channel-count changes, and sample-rate problems. Sanitization is limited to replacing NaN and infinite values with `0.0` when explicitly requested by callers.

Candidate 2, `reborn_015`, is implemented minimally as lightweight operational performance metadata in `audio_quality_humanizer.validation.performance`. It records elapsed seconds, optional file sizes, Python version, and platform without `psutil`, multiprocessing, GPU, JIT, or real-time assumptions.

Candidate 3, `reborn_022`, is implemented as synthetic regression scaffolding in tests. The tests cover normal sine waves, silence, NaN values, infinite values, very short audio, mono/stereo shapes, invalid sample rates, output shape mismatch, output length mismatch, and output peaks above the safe threshold.

## Deferred Scope

Candidate 4, `reborn_025`, is deferred. Future read-only comparison metric expansion may review SNR, correlation, RMSE, dynamic-range delta, spectral summary deltas, and structured before/after quality reporting. It needs deeper review to avoid legacy comparison framing and unsafe interpretations.

Candidate 5, `reborn_005`, is deferred. Future metadata/privacy and analysis-stat expansion may review metadata inspection/reporting, changed-tag reporting, processing stats, spectral entropy, spectral flatness, and neutral complexity metrics. It needs deeper review because the source file has the highest legacy-framing risk.

## Report Field Changes

`analyze`, `humanize`, `doctor`, and `validate-samples` can include additive `guardrails` fields.

`doctor` and `validate-samples` can include additive `performance` fields.

Markdown reports can render a neutral `Signal Guardrails` section and optional `Performance Metadata` section.

No existing successful CLI output is intentionally changed.

## CLI Impact

No new CLI command is added.

Existing commands keep their current arguments.

Project Reborn is not exposed through CLI help.

## Test Plan

- Unit-test guardrail validation with synthetic numeric, non-numeric, silent, NaN, and infinite arrays.
- Unit-test samplerate validation and processing-result shape/length/peak checks.
- Unit-test sanitization to confirm NaN and infinite values are replaced without normalization.
- Unit-test performance helpers for elapsed seconds and platform metadata.
- Unit-test design JSON for implemented and deferred candidate status.
- Run the full test suite.
- Run root cleanliness, Project Reborn, safety scan, CLI smoke, and build checks.
- Confirm built wheels still exclude `project_reborn/`.

## Acceptance Criteria

- Version is `0.10.0`.
- Candidate 1 is implemented.
- Candidate 2 is implemented minimally.
- Candidate 3 is implemented as regression scaffolding.
- Candidate 4 is deferred.
- Candidate 5 is deferred.
- No Project Reborn source file is copied, imported, executed, packaged, or exposed.
- Project Reborn remains excluded from package discovery.
- Project Reborn has no `__init__.py`.
- Safety scan passes.
- CLI smoke passes.
- Build check passes.
