# Safety Policy

`audio-quality-humanizer` is a metadata inspection and ordinary metadata cleaning project.

This project is not a watermark remover.

This project is not a fingerprint remover.

This project is not a detector bypass tool.

This project does not claim to remove provenance markers, origin markers, or source attribution systems.

Future recognition/preflight checks do not grant rights to use, distribute, monetize, or transform an audio work.

No-match results in recognition systems do not mean that a work is rights-free, public domain, or cleared for release.

High-similarity rebuild workflows, if added later, are only for user-owned or properly licensed works.

A clean rebuild must not reuse original waveforms, stems, loops, phase data, spectral masks, or source-derived frequency reconstruction data.

Analyze and release-check are read-only.

Metrics are for audio quality and technical release readiness only.

Quality artifact terms such as harshness, mud, shimmer, stereo risk, and clipping are not watermark/fingerprint detection categories.

The tool must never optimize processing to reduce recognition, attribution, or detectability.

Compare is read-only.

Compare must never be used as proof that attribution, recognition, provenance, or detector behavior changed.

Compare must never optimize toward reduced recognizability or reduced detectability.

Compare is only for audio quality and release-readiness regression checks.

Humanize may alter audible audio quality.

Humanize must remain conservative and measurable.

Humanize must never be used to reduce recognizability, attribution, provenance, or detectability.

Humanize must never claim to remove or alter watermarks, fingerprints, origin markers, provenance markers, C2PA markers, detector signals, or source-attribution systems.

Humanize must keep original files untouched.

Safety gates must block output that clips, becomes silent, changes duration unexpectedly, changes sample rate/channel count, or introduces severe stereo/phase risk.

Humanize must not use old legacy remover/detector modules.

Doctor is read-only.

Batch read-only modes are read-only.

Batch humanize writes only to output_dir.

Originals must never be modified.

Batch must not be used to process toward reduced recognizability, attribution, provenance, or detectability.

Batch results are not proof of platform acceptance or legal clearance.

Preset eval creates processed copies only.

Preset eval must never modify the original input.

Preset eval must not optimize toward reduced recognizability, attribution, provenance, or detectability.

Preset eval recommendations must be based only on quality, compare, and release metrics.

Preset eval recommendations are not legal clearance or platform certification.

Real-world validation uses user-supplied local audio only.

Real-world validation outputs must stay out of git by default.

Validation must never be used to optimize toward reduced recognizability, attribution, provenance, or detectability.

Validation results are not legal clearance or platform certification.

Validation-status is diagnostic only.

Validation-status must not read or process audio content.

Validation-status must not evaluate watermark, fingerprint, provenance, or detector behavior.

Validation-status may list local report paths but must not upload or expose audio.

Packaging and build checks are safety-neutral.

Release artifacts must preserve the same safety boundary as the source tree.

Packaging must not weaken the safety scan or unsafe wording tests.

Project Reborn is not part of the active package boundary.

Project Reborn files are reference-only.

Old filenames are not behavior claims.

Future extraction from Project Reborn must inspect behavior, not names.

Future extraction from Project Reborn must pass tests, the root cleanliness check, the Project Reborn catalog check, the safety scan, CLI smoke, and the build check.

Project Reborn audit is static-only.

Project Reborn audit terms are review flags, not product claims.

No audit result makes a file safe to import.

Project Reborn Top-5 planning is manual text review only.

Project Reborn Top-5 planning notes are not product claims.

Project Reborn Top-5 planning does not make reference files importable, installable, packaged, or user-facing.

Project Reborn Top-5 planning must not copy code into the active package.

Future Project Reborn rewrites must ignore old unsafe behavior and preserve the current package safety boundary.

Future extraction from Project Reborn requires safe rewrite into `audio_quality_humanizer/`.

v0.10.0 safe core was rewritten from first principles inside the active package.

Project Reborn was not copied, imported, executed, packaged, or exposed for v0.10.0.

Signal guardrails are quality and workflow-safety checks, not attribution, recognition, provenance, detector, bypass, or evasion tools.

Performance metadata is operational metadata only.

v0.10.0 regression tests use synthetic audio only.

CI enforces a public-claim safety scan.

CI enforces legacy import guards.

CI smoke-tests CLI workflows.

Safety automation is not legal certification or platform approval.

Contributors must not weaken safety tests to make unsafe features pass.
