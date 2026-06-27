# Changelog

## Unreleased private beta

- Added a private beta workflow layer for quick scan, metadata clean, quality naturalize, and full release pass jobs.
- Exposed workflow definitions through the protected API config endpoint.
- Added step-level workflow status, grouped artifacts, and safe workflow summaries for the private dashboard.
- Fixed workflow artifact grouping and dashboard preview handling for audio, report, metadata, hash, and intermediate artifacts.
- Fixed stale private dashboard request errors so successful job status, config, and job list responses clear older failures.
- Kept this as a private beta change with no official release, no public launch, no tag, and no production-domain deployment.

## v0.18.1

- Fixed private beta rollout docs to consistently target `v0.18.0`.
- Clarified rollback examples so previous tags such as `v0.17.0` are only rollback targets.
- Added a documentation consistency test for rollout target versions.
- Ignored local ad-hoc generated humanize validation outputs.

## v0.18.0

- Added private beta home-server rollout runbook for `beta.datenpflege-nord.de` behind the existing Cloudflare Tunnel.
- Added preflight, post-deploy, rollback, and smoke-test documentation for the v0.18.0 private beta deployment.
- Added optional local smoke-test script for health, dashboard gate, API auth, upload limit, and cleanup checks.
- Kept runtime behavior, audio algorithms, `humanize`, public launch features, provider comparisons, databases, queues, analytics, and official product positioning deferred.

## v0.17.0

- Added private beta deployment-prep documentation for `beta.datenpflege-nord.de` behind the existing Cloudflare Tunnel.
- Added environment, Cloudflare Tunnel, security, privacy, Docker Compose, and optional systemd examples with placeholders only.
- Added optional shared beta-password dashboard gate loaded from environment config.
- Added v0.17 runtime config aliases for the intended private beta deployment.
- Kept public launch, official product positioning, provider comparisons, frontend frameworks, databases, queues, `humanize`, and audio algorithm changes deferred.

## v0.16.0

- Hardened private web auth feedback, security headers, retention visibility, cleanup controls, and recent job summaries.
- Added authenticated safe config and job-list endpoints without exposing server paths or secrets.
- Restricted artifact downloads to names listed in each job status.
- Added local exposure warnings and operator controls to the plain dashboard.
- Added docs-only deployment readiness checklist; no deployment, provider config, frontend framework, or `humanize` implementation was added.

## v0.15.0

- Added private web `clean-metadata` output workflow with cleaned audio and before/after metadata artifacts.
- Added private web `compare` two-file workflow with downloadable `compare.json`.
- Added private web `visualize-compare` two-file workflow with downloadable `compare.json` and `visual_compare.json`.
- Updated the local dashboard for one-file and two-file modes without adding frontend dependencies.
- Kept `humanize`, deployment, public launch, accounts, queueing, billing, analytics, and frontend frameworks deferred.

## v0.14.0

- Added private dashboard shell for local web MVP.
- Added artifact preview rendering for generated JSON reports.
- Added waveform and spectrogram previews from visualization artifacts.
- Added sanitized metadata display for embedded cover and long metadata fields.
- Kept external frontend libraries, deployment, public launch, file-modifying modes, and two-file modes deferred.

## v0.13.1

- Added execution for safe single-file private web backend modes.
- Added generated JSON artifacts for analyze, release-check, inspect-metadata, and visualize jobs.
- Added minimal local operator page.
- Kept file-modifying, two-file, frontend-framework, deployment, and public-launch work deferred.

## v0.13.0

- Added private-beta web backend MVP planning and skeleton.
- Added bearer-token auth, upload validation, job storage, artifact access, and cleanup tests.
- Kept frontend UI, deployment, and public launch deferred.

## v0.12.1

- Added release notes and schema hardening for visualization artifacts.
- Hardened tests for visualization JSON shape, CLI help wording, and forbidden labels.
- Added local editable-install troubleshooting note.

## v0.12.0

- Added read-only visualization artifact generation for future web UI use.
- Added waveform peaks, spectrogram summaries, and before/after difference-map reports.
- Added safe tooltip-region metadata based only on measured technical changes.
- Added tests and real local validation for visualization artifacts.

## v0.11.3

- Added design notes for a future safe web upload and spectrum visualization MVP.
- Documented proposed DatenpflegeNord subdomain flow, spectrum views, difference map, tooltip behavior, and FAQ.
- Reconfirmed web UI safety boundaries before implementation.

## v0.11.2

- Added deep-review design notes for deferred Project Reborn candidate `reborn_005`.
- Kept `reborn_005` implementation deferred pending separate approval.
- Reconfirmed Project Reborn remains inert and reference-only.

## v0.11.1

- Added v0.11.0 release notes.
- Improved README documentation for read-only compare metrics.
- Hardened report-shape and wording tests for `comparison_metrics`.
- Reconfirmed generated v0.11 validation outputs stay ignored.

## v0.11.0

- Added neutral read-only compare metrics under `comparison_metrics`.
- Added Markdown rendering for compare metric expansion.
- Added v0.11.0 compare metrics design documentation and validation policy.
- Validated compare metrics with synthetic tests and local real-audio no-op/comparison checks.

## v0.10.3

- Added Candidate Reality Gate for future feature candidates.
- Added Deep Search stop rule for current external information.
- Added deep review plan for deferred Project Reborn candidate `reborn_025`.
- Required real local audio validation and no-op checks for future user-facing audio behavior.

## v0.10.2

- Added Candidate Reality Gate for future feature candidates.
- Added deep review plan for deferred Project Reborn candidate `reborn_025`.
- Required real local audio validation and no-op checks for future user-facing audio behavior.

## v0.10.1

- Ignored local v0.10 validation outputs.
- Added v0.10.0 release notes.
- Added README usage notes for signal guardrail reports.

## v0.10.0

- Added signal guardrails and signal-hygiene reporting.
- Added minimal performance metadata helpers.
- Added synthetic regression tests for edge-case audio handling.
- Documented deferred Project Reborn candidates for future safe review.

## v0.9.4

- Added Project Reborn Top-5 manual review plan.
- Ranked five promising Project Reborn entries for future safe rewrite.
- Extended Project Reborn checks to validate planning files and planning safety statuses.

## v0.9.3

- Added static Project Reborn audit map.
- Added audit generation tool.
- Extended Project Reborn checks to cover audit completeness.

## v0.9.2

- Added Project Reborn as a non-installed reference drawer.
- Moved and neutrally renamed historical experimental scripts.
- Added Project Reborn catalog.
- Added root cleanliness and Project Reborn checks.

## v0.9.1

- Added version flag.
- Added wheel/source build validation.
- Improved install documentation.

## v0.9

- Added real-world validation harness for local user-supplied audio samples.

## v0.8

- Preset evaluation and report polish.

## v0.7

- Added CI hardening and safety automation.

## v0.6

- Added doctor and batch workflows.

## v0.5

- Added conservative humanize processing.

## v0.4

- Added compare.

## v0.3

- Added release-check.

## v0.2

- Added analyze.

## v0.1

- Added metadata cleaner.
