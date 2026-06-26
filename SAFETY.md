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

Compare metrics must use neutral audio-quality names only.

Compare metrics must not use unsafe score names tied to watermark, fingerprint, detector, recognition, provenance, origin, source attribution, bypass, evasion, or detectability concepts.

v0.11 compare metrics are read-only.

v0.11 compare metrics do not modify audio.

Generated v0.11 local validation outputs remain ignored and uncommitted.

Real local audio is never committed.

Project Reborn remains inert after v0.11 compare metrics.

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

Every future feature candidate must document a Deep Search decision before active package work begins.

If current external information is required, implementation must stop until the user provides an update or approves a constrained internal-only scope.

Real local audio validation is required for future user-facing audio behavior.

Synthetic tests alone are not enough for future user-facing audio behavior.

No-op checks are required for future user-facing audio behavior.

Project Reborn remains inert.

Local validation outputs are intentionally ignored.

Generated reports and generated audio are not part of the repository.

Release notes may summarize validation outcomes without bundling user audio.

`reborn_005` remains deferred after design-only review.

High-risk legacy framing in `reborn_005` was reviewed only as text.

No Project Reborn source was copied, imported, executed, packaged, or exposed during the `reborn_005` review.

Future metadata/privacy/statistics behavior must avoid attribution, fingerprint, watermark, detector, provenance, bypass, evasion, and detectability claims.

Any future web upload interface must be private beta first.

Uploaded audio must be temporary.

Generated web outputs must not be committed.

Visualization must not imply watermark, fingerprint, provenance, detector, bypass, origin, C2PA, source-attribution, or detectability outcomes.

Highlighted spectrum areas must map to measured technical metrics only.

Web read-only modes must not modify files.

Web clean-metadata behavior must only affect documented standard metadata fields.

Visualization artifacts are read-only.

Visualization labels must map to measured technical metrics.

Difference maps must not imply watermark, fingerprint, provenance, detector, origin, C2PA, source-attribution, bypass, evasion, detectability, platform, or distributor outcomes.

Generated visualization reports from real user audio must not be committed.

The private web app is local and private beta only.

Visualization artifacts are preview data for measured technical review only.

Visualization artifacts are not mastering certification.

Visualization artifacts do not predict platform or distributor acceptance.

The v0.17 private web API is private beta only.

All private web API endpoints except `/health` require bearer-token auth.

Private web auth errors must use safe messages and must not expose configured tokens.

The private web dashboard must not store bearer tokens in browser storage or cookies.

Recommended private web local bind is `127.0.0.1`.

The private web app must not be bound directly to `0.0.0.0` for public exposure before a future deployment milestone validates proper proxy, rate-limit, upload-limit, logging, auth, and privacy controls.

Private web API responses should use lightweight local hardening headers.

Uploaded files are temporary.

The private web operator page is local and uses no frontend framework or external assets.

The private web operator page may show safe retention settings, max upload size, cleanup controls, and recent job summaries.

Private web safe config and recent job APIs must not expose server paths, environment values, or secrets.

The private web API may execute safe single-file read-only modes and write JSON artifacts.

The private web API may execute `clean-metadata` by writing a cleaned copy under the job artifacts directory.

Private web `clean-metadata` must not overwrite the uploaded input file.

The private web API may execute safe two-file compare and visualize-compare modes with fixed before/after upload fields.

Private web compare and visualize-compare artifacts must show measured technical deltas only.

Private web artifact downloads must require the requested artifact name to be listed in the job status.

The private web dashboard renders generated artifacts only and must not add fake metrics.

The private web dashboard sanitizes embedded images and long metadata fields for display.

Private web `humanize` and other output-audio processing modes remain deferred.

Private web storage must use random job IDs and must not use user filenames as storage paths.

Generated private web outputs must not be committed.

No frontend framework, public launch, official product positioning, SEO, analytics, or DatenpflegeNord dashboard integration is included in v0.17.

The v0.17 deployment prep is for a private side-project beta only.

The private beta hostname is `beta.datenpflege-nord.de`.

The private beta must not be advertised on `datenpflege-nord.de`.

The private beta must not be linked from the DatenpflegeNord dashboard.

Cloudflare Tunnel is the only intended public entry for the private beta.

Uvicorn must bind locally and must not be exposed directly to the internet.

The temporary shared beta password must be configured outside Git.

The real beta password, beta password hash, and `AQH_WEB_TOKEN` must not be committed.

Before any official launch, shared password access must be replaced by Cloudflare Access OTP or equivalent stronger access control.

The private web API must not make watermark, fingerprint, provenance, detector, C2PA, source-attribution, evasion, detectability, platform-certification, or distributor-guarantee claims.

CI enforces a public-claim safety scan.

CI enforces legacy import guards.

CI smoke-tests CLI workflows.

Safety automation is not legal certification or platform approval.

Contributors must not weaken safety tests to make unsafe features pass.
