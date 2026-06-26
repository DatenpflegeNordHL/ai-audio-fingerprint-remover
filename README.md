# audio-quality-humanizer

`audio-quality-humanizer` is a local CLI for metadata inspection, ordinary metadata cleaning, provenance-risk inspection, audio quality analysis, release-readiness checking, conservative audio-quality processing, and workflow reporting for owned/licensed tracks only.

The v0.1 MVP helps you see what editable metadata is present, identify metadata keys that may be related to provenance or generation context, and create a copied audio file with ordinary user-editable tags removed where supported by local metadata libraries.

The v0.2 and v0.3 commands add read-only audio quality analysis and release-readiness preflight checks. These checks are pragmatic technical reports, not official distributor or platform certification.

The v0.4 compare command checks whether a candidate file introduces technical quality or release-readiness regressions relative to a reference file.

The v0.5 humanize command adds conservative audio-quality processing presets guarded by before/after analysis, compare, and safety gates.

The v0.6 workflow commands add `doctor` for one-file release preflights and `batch` for running existing commands across folders.

The v0.7 milestone adds CI hardening and safety automation across tests, help output, public wording, smoke workflows, and legacy import guards.

The v0.8 `preset-eval` command runs existing conservative presets on processed copies, compares the results, writes per-preset reports, and recommends an eligible preset based on quality preflight metrics.

The v0.9 `validate-samples` command runs local real-world validation over user-supplied audio samples without committing those audio files to Git.

The v0.11 compare workflow adds neutral read-only `comparison_metrics` for before/after quality deltas. These metrics are additive report fields and do not modify audio, change release-check scoring, or add a new CLI command.

The v0.14 private web dashboard adds generated artifact previews, metric cards from real report fields, waveform and spectrogram previews from visualization JSON, and sanitized metadata display for embedded images and long fields. It has no frontend framework, deployment config, DNS config, or public launch.

The v0.16 local web hardening adds safe auth feedback, response headers, retention visibility, cleanup controls, recent job summaries, and per-job artifact-list enforcement. It still has no deployment config, DNS config, public launch, frontend framework, or `humanize` web workflow.

The v0.17 deployment prep adds private side-project beta documentation and examples for `beta.datenpflege-nord.de` behind the already configured Cloudflare Tunnel. It is not an official public DatenpflegeNord product and must not be advertised or linked from the DatenpflegeNord dashboard.

The v0.18 rollout prep adds home-server runbooks, preflight/post-deploy checklists, rollback notes, and an optional smoke-test helper for the existing Cloudflare Tunnel deployment path. It still does not add public launch features or production infrastructure automation.

## v0.10.0 safe core

v0.10.0 adds signal guardrails, optional performance metadata, and synthetic regression scaffolding. These features were designed from Project Reborn planning notes but rewritten from first principles inside the active package. Project Reborn remains non-installed and inert.

## v0.10.0 guardrail reports

v0.10.0 adds signal guardrail reporting to analysis and release-readiness workflows.

Example:

```bash
ai-humanizer analyze path/to/audio.wav \
  --report analysis.json \
  --markdown analysis.md
```

Reports may include a `Signal Guardrails` section showing whether the input had NaN values, infinite values, full-scale peaks, shape changes, length changes, or sample-rate issues.

These guardrails are audio-quality and workflow-safety checks. They are not attribution, recognition, watermark, fingerprint, provenance, detector, bypass, or evasion tools.

## Safety Boundary

This tool does not remove audio watermarks.

This tool does not remove audio fingerprints.

This tool does not bypass detectors.

This tool does not remove provenance markers or origin markers.

Metadata cleaning may remove ordinary user-editable tags such as title, artist, album, comments, or similar container metadata. Metadata keys that look potentially provenance-related are reported as a risk signal and are not silently removed by default.

Analyze and release-check do not alter audio. They do not evaluate or alter watermarks, fingerprints, provenance markers, origin markers, or detector signals. LUFS is currently approximate and RMS-based, not EBU/ITU compliant integrated loudness.

Compare is also read-only. It checks technical regressions only and does not check watermark, fingerprint, provenance, origin-marker, or detector behavior.

Humanize may alter audible audio quality, but it does not target watermark, fingerprint, provenance, origin-marker, detector, C2PA, or attribution-system behavior. It does not use time-stretch, pitch-shift, neural resynthesis, stem separation, phase randomization, or legacy remover modules.

Doctor and batch workflow reports do not evaluate or alter watermark, fingerprint, provenance, origin-marker, detector, C2PA, or attribution-system behavior.

Preset evaluation creates processed copies only and never modifies the original input. It does not evaluate or alter watermark, fingerprint, provenance, origin-marker, detector, C2PA, or attribution-system behavior. Recommendations are based only on quality, compare, and release-readiness metrics; they are not legal clearance or platform certification.

Real-world validation uses local user-supplied audio only. Validation samples are ignored by Git by default, and validation never modifies original files. It does not evaluate or alter watermark, fingerprint, provenance, origin-marker, detector, C2PA, or attribution-system behavior. Validation results are technical reports, not legal clearance or platform certification.

## Installation

```bash
python -m pip install -e ".[dev,test]"
```

## Installation modes

Check Python first:

```bash
python3 --version
```

Python >=3.10 is required. If macOS system `python3` is 3.9, install a newer Python with pyenv, Homebrew, or python.org. Do not rely on `python` existing on macOS.

Editable development install:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev,test]"
ai-humanizer --version
pytest
python tools/safety_scan.py
python tools/cli_smoke.py
```

Editable development install with the optional private web backend:

```bash
python -m pip install -e ".[web,dev,test]"
```

Build and install a wheel locally:

```bash
python -m build
python -m pip install dist/*.whl
ai-humanizer --version
```

Run the build check:

```bash
python tools/build_check.py
```

Troubleshooting:

- If `python: command not found`, use `python3` or `.venv/bin/python`.
- If Python is 3.9, use a newer interpreter.
- If editable install has `.pth` quirks, build and install the wheel, then verify with `ai-humanizer --version`.

## Usage

Inspect ordinary metadata:

```bash
ai-humanizer inspect-metadata input.wav --report metadata.json
```

Inspect provenance-risk metadata:

```bash
ai-humanizer inspect-provenance input.wav --report provenance.json
```

Copy a file and clean ordinary metadata where supported:

```bash
ai-humanizer clean-metadata input.wav output.wav --report clean.json
```

Analyze audio quality metrics:

```bash
ai-humanizer analyze input.wav --report analysis.json --markdown analysis.md
```

Run release-readiness preflight checks:

```bash
ai-humanizer release-check input.wav --target streaming --report release.json --markdown release.md
ai-humanizer release-check input.wav --target club --report club_release.json
```

Compare a candidate file against a reference:

```bash
ai-humanizer compare before.wav after.wav --target streaming --report compare.json --markdown compare.md
ai-humanizer compare before.wav after.wav --target club --fail-on-regression
```

Compare is useful after metadata cleaning, future humanizing, mastering, or format conversion. It checks whether the candidate introduces technical regressions and can return a non-zero exit code with `--fail-on-regression`.

Compare reports include neutral `comparison_metrics` such as RMSE, mean absolute error, correlation, approximate signal-to-difference, peak/RMS deltas, dynamic-range deltas, spectral centroid deltas, spectral rolloff deltas, and optional stereo/side-energy deltas. Unavailable values are reported as `null`.

Example compare metrics report:

```bash
ai-humanizer compare before.wav after.wav \
  --target club \
  --report compare.json \
  --markdown compare.md
```

`comparison_metrics` are read-only before/after quality deltas. JSON outputs are safe to serialize and unavailable values are reported as `null`. These metrics do not certify distributor or platform acceptance, and they do not evaluate attribution, recognition, provenance, watermark, fingerprint, detector behavior, bypass, evasion, or source attribution.

Generate read-only visualization artifacts for future UI rendering:

```bash
ai-humanizer visualize input.wav \
  --report visualization.json
```

```bash
ai-humanizer visualize-compare before.wav after.wav \
  --report visual_compare.json
```

Visualization artifacts include waveform peaks, downsampled spectrogram summaries, metric cards, before/after difference maps, and safe tooltip-region metadata. They are read-only, do not modify audio, and difference maps show measured technical changes only. They do not make watermark, fingerprint, provenance, detector, platform, or distributor claims.

The visualization artifact schema is intentionally stable for future UI work. Reports include `schema_version`, bounded waveform and spectrogram arrays, JSON-safe numeric values, and safe tooltip labels only. The artifacts are preview data for technical review; they are not mastering certification and do not predict platform or distributor acceptance.

## Private web backend MVP

v0.17.0 prepares the private local web MVP for a private side-project beta on the existing DatenpflegeNord home server behind the already configured Cloudflare Tunnel.

Install the optional web extra before running it:

```bash
python -m pip install -e ".[web,dev,test]"
```

Local run example:

```bash
AQH_WEB_TOKEN=dev-token uvicorn audio_quality_humanizer.web.app:app --host 127.0.0.1 --reload
```

Open `http://127.0.0.1:8000/` for the local operator page.

Recommended local bind is `127.0.0.1`. Do not bind this private beta directly to `0.0.0.0` unless a future deployment milestone adds and validates proper auth, proxy, rate-limit, logging, upload-limit, and privacy controls.

Private beta deployment-prep docs are in `deployment/`. The intended manual Cloudflare Tunnel route is:

- public hostname: `beta.datenpflege-nord.de`
- local service: `http://localhost:8017`
- local Uvicorn bind: `127.0.0.1:8017`

The Cloudflare Tunnel already exists. No local router port forwarding, local Certbot/Caddy/Nginx, public launch, marketing, SEO, analytics, provider comparison, database, account system, Redis/Celery queue, or official DatenpflegeNord dashboard integration is added.

Runtime config names for the private beta:

- `AQH_WEB_HOST`
- `AQH_WEB_PORT`
- `AQH_WEB_TOKEN`
- `AQH_WEB_JOBS_DIR`
- `AQH_WEB_MAX_UPLOAD_MB`
- `AQH_WEB_JOB_TTL_HOURS`
- `AQH_WEB_MAX_ACTIVE_JOBS`
- `AQH_BETA_PASSWORD_HASH` preferred, or `AQH_BETA_PASSWORD` temporarily

Use `deployment/env/web.env.example` as a placeholder template only. Real token and password values must be set outside Git.

Implemented backend endpoints:

- `GET /health`
- `GET /api/config`
- `GET /api/jobs`
- `POST /api/jobs`
- `POST /api/compare-jobs`
- `GET /api/jobs/{job_id}`
- `GET /api/jobs/{job_id}/artifacts/{artifact_name}`
- `DELETE /api/jobs/{job_id}`
- `POST /api/maintenance/cleanup`

All API endpoints except `/health` require a bearer token. Missing server-token, missing request-token, and wrong request-token errors use safe messages and do not expose configured secrets. Single-file upload flow accepts one file per request. Two-file upload flow accepts fixed `before_file` and `after_file` fields. Both flows validate allowlisted audio extensions, check basic audio container headers where practical, store uploads under a random per-job directory, run safe processing synchronously, write JSON-safe artifacts, and update `status.json`.

`GET /api/config` returns safe operator settings only: upload limit, retention TTLs, supported modes, deferred modes, and private-beta status. It does not expose server paths or secrets. `GET /api/jobs` returns recent job summaries only and does not include raw server paths. Artifact downloads require both a safe artifact name and membership in the job's `status.json` artifact list.

The backend sets lightweight response headers for local hardening: `X-Content-Type-Options: nosniff`, `Referrer-Policy: no-referrer`, `X-Frame-Options: DENY`, and `Cache-Control: no-store` for API responses.

The dashboard renders generated JSON artifacts in-browser after job completion. It shows only fields that exist in the artifacts, keeps raw JSON available, and adds no fake metrics or fake improvement percentages. No fake metrics are added.

Generated artifacts:

- `analyze` writes `analysis.json`
- `release-check` writes `release_check.json`
- `inspect-metadata` writes `metadata.json`
- `clean-metadata` writes `cleaned_output.<ext>`, `metadata_before.json`, `clean_metadata.json`, and `metadata_after.json`
- `visualize` writes `visualization.json`
- `compare` writes `compare.json`
- `visualize-compare` writes `compare.json` and `visual_compare.json`

Dashboard previews:

- metric cards from existing analyze, release-check, and visualization report fields
- comparison metric cards from existing compare report fields
- waveform preview from `visualization.json` `waveform_peaks.peaks`
- spectrogram energy preview from `visualization.json` `spectrogram.energy_db`
- before/after visualization preview from `visual_compare.json` candidate waveform and spectrogram fields, with difference-map fallback
- metadata key/value panel from `metadata.json` `metadata_display`
- before/after metadata panels from `metadata_before.json` and `metadata_after.json`

Operator controls:

- local-private-beta exposure warning
- safe retention and max-upload display from `/api/config`
- cleanup button calling `POST /api/maintenance/cleanup`
- recent job summaries from `GET /api/jobs`

The metadata display is sanitized for embedded images and long fields. Embedded cover values such as `APIC:Cover` are summarized with `[embedded image omitted]`, optional MIME/type/size fields, and preserved metadata keys. Long text display values are truncated for dashboard use. `clean-metadata` writes a cleaned output copy under the job artifacts directory and does not overwrite the uploaded input.

Supported single-file MVP modes are `analyze`, `release-check`, `inspect-metadata`, `clean-metadata`, and `visualize`. Supported two-file MVP modes are `compare` and `visualize-compare`. `humanize` is deferred until a later safe flow covers output-audio generation.

This backend is private beta only. The operator page uses plain HTML, inline CSS, and minimal vanilla JavaScript. There is no frontend framework, static asset build chain, deployment config, DNS config, public launch, database, account system, background queue, analytics, billing, or multi-tenant storage in this milestone. Existing safety boundaries apply.

Apply conservative audio-quality processing:

```bash
ai-humanizer humanize input.wav output.wav --preset subtle --target streaming --report humanize.json --markdown humanize.md
ai-humanizer humanize input.wav output.wav --preset afro-club --target club --fail-on-safety
```

Humanize keeps the original input untouched. Safety gates analyze before/after metrics and compare the result; if safety gates fail, the output is reverted or not left as a misleading processed result.

Run a one-file workflow preflight:

```bash
ai-humanizer doctor input.wav --target streaming --report doctor.json --markdown doctor.md
```

Run workflows across folders:

```bash
ai-humanizer batch ./tracks --mode doctor --target streaming --pattern "*.wav" --report batch.json --markdown batch.md
ai-humanizer batch ./tracks --mode humanize --preset afro-club --target club --output-dir ./processed --recursive --report batch.json --markdown batch.md
```

Doctor combines metadata, provenance-risk inspection, analyze, and release-check for one file. Doctor is read-only. Batch applies existing commands across folders; read-only modes stay read-only, and batch humanize writes only to `output_dir` and never modifies originals. Batch does not use parallelism yet.

Evaluate conservative presets on output copies:

```bash
ai-humanizer preset-eval input.wav --target streaming --output-dir ./eval --report preset_eval.json --markdown preset_eval.md
ai-humanizer preset-eval input.wav --target club --presets subtle,balanced,afro-club --output-dir ./eval --fail-if-none
```

Preset evaluation runs `doctor` once, then evaluates each selected preset independently. A failed preset does not stop the full evaluation. The recommendation only considers eligible outputs that passed humanize, compare, release checks, and original-file integrity checks.

Run real-world validation on local user-supplied audio:

```bash
cp examples/validation_manifest.example.json validation_manifest.json
mkdir -p validation_samples validation_outputs
# Put your own WAV/FLAC files into validation_samples. Do not commit them.
ai-humanizer validate-samples validation_manifest.json --output-dir validation_outputs --default-target club --report validation.json --markdown validation.md
```

Validation runs doctor and preset-eval for each manifest sample, then recommends presets per real track when an eligible result exists. Real audio samples stay local, are ignored by Git by default, and originals are never modified. Validation does not evaluate or alter watermark, fingerprint, provenance, origin-marker, detector, C2PA, or attribution-system behavior, and validation reports are not legal clearance or platform certification.

## Local validation troubleshooting

```bash
pwd
ai-humanizer validation-status --find
ai-humanizer validation-status --root /Users/s4zander/Documents/ai-audio-fingerprint-remover --find --markdown validation_status.md
```

If `cat validation.md` says the file was not found, you are probably in the wrong folder or validation has not been run yet. On macOS, use `python3` or `.venv/bin/python`; `python` is not always installed as a command. Local validation files are ignored by Git by design, so use `validation-status --find` to locate generated reports before opening them.

## Project Reborn

Project Reborn is a non-installed reference drawer for historical experimental scripts. Old filenames are historical labels only and must not be used to infer behavior. Nothing in Project Reborn is imported, packaged, or exposed through the CLI. Useful ideas must be manually reviewed and safely rewritten into `audio_quality_humanizer/`.

Project Reborn now includes a static audit map at `project_reborn/audit/PROJECT_REBORN_AUDIT_MAP.md`. The audit is static only. It does not execute or import Project Reborn files.

The v0.10.0 design spec is available at `docs/design/V0_10_0_DESIGN_SPEC.md`.

The v0.11.0 compare metrics design is available at `docs/design/V0_11_0_COMPARE_METRICS.md`.

`reborn_005` now has a design-only deep review at `docs/design/REBORN_005_DEEP_REVIEW.md`. No active package behavior changed from that review.

The future web upload visualization MVP is documented as design-only at `docs/design/V0_11_3_WEB_UPLOAD_VISUALIZATION_MVP.md`. No web app is implemented yet. The candidate subdomain is `release.datenpflege-nord.de`; any future web version must keep the same safety boundary, and spectrum or difference views must show only measured technical changes.

The v0.18 private web dashboard MVP is documented at `docs/design/V0_13_0_PRIVATE_WEB_BACKEND_MVP.md`. Its deployment-readiness checklist is documented at `docs/design/V0_16_0_DEPLOYMENT_READINESS_CHECKLIST.md`, and private-beta rollout docs are in `deployment/`. It is private beta only, uses no external frontend libraries, supports documented one-file and two-file modes, and keeps public launch, official product positioning, dashboard integration, OTP, database, queues, and `humanize` deferred.

## Candidate Reality Gate

Future audio features must pass the Candidate Reality Gate: synthetic tests, real local audio validation, no-op check, safe wording check, and a documented Deep Search decision.

If external current information is required, work stops until the user provides a research update or approves a constrained internal-only scope.

See `docs/design/CANDIDATE_REALITY_GATE.md`. The deferred `reborn_025` deep review is documented at `docs/design/REBORN_025_DEEP_REVIEW.md`. The deferred `reborn_005` deep review is documented at `docs/design/REBORN_005_DEEP_REVIEW.md`.

See `project_reborn/catalog/PROJECT_REBORN_CATALOG.md`.

Each command runs locally and writes a JSON report when `--report` is provided. Analyze, release-check, compare, humanize, doctor, batch, preset-eval, and validate-samples can also write Markdown reports with `--markdown`.

## Release notes

- `v0.10.0`: `docs/releases/V0_10_0_RELEASE_NOTES.md`
- `v0.11.0`: `docs/releases/V0_11_0_RELEASE_NOTES.md`
- `v0.12.0`: `docs/releases/V0_12_0_RELEASE_NOTES.md`

## Developer troubleshooting

If editable install hangs in a local virtual environment because of stale package metadata, remove or move old `audio_quality_humanizer*.dist-info` and `__editable__audio_quality_humanizer*` files from the active venv `site-packages`, then rerun:

```bash
python -m pip install -e ".[dev,test]"
```

This is local environment cleanup, not a repository issue.

## Roadmap

- v0.1 metadata cleaner implemented
- v0.2 analyze implemented
- v0.3 release-check implemented
- v0.4 compare implemented
- v0.5 conservative humanize implemented
- v0.6 doctor/batch workflow implemented
- v0.7 CI hardening and safety automation implemented
- v0.8 preset evaluation and report polish implemented
- v0.9 real-world validation harness implemented
- v0.10 safe core guardrails and performance metadata implemented
- v0.11 read-only compare metrics implemented
- future: release packaging
- future: optional standards-compliant LUFS, optional true-peak approximation
- future: optional real-world benchmark docs
- later authorized rebuild for owned/licensed tracks only

## Development

```bash
python -m pip install -e ".[test]"
pytest
python tools/safety_scan.py
python tools/cli_smoke.py
```

## CI / Safety Automation

GitHub Actions runs the test suite on Python 3.10, 3.11, and 3.12. CI also runs CLI help smoke tests, an end-to-end CLI workflow smoke test, the public-claim safety scan, and legacy import guard tests so old remover/detector behavior is not reintroduced.

## License

This project is licensed under the MIT License. See `LICENSE` for details.
