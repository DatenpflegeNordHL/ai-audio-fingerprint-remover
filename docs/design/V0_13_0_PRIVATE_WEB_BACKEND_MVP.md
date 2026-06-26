# v0.15 Private Dashboard and Web Backend MVP

## Status

Implemented working local dashboard and backend MVP with output and two-file workflows.

## Deep Search Summary

Deep Search decision for v0.15.0: `not_needed_internal_repo_only`.

The current milestone only extends the already-approved local backend. No new external frontend libraries or current external information were needed. The approved stack remains FastAPI, Uvicorn, and python-multipart as an optional `web` extra. The backend uses FastAPI `UploadFile`, bearer-token auth for private beta access, one uploaded file per single-file request or fixed before/after uploads for two-file requests, random job IDs from `secrets.token_urlsafe`, and temporary per-job directories under a controlled local root.

## Approved Dependencies

Runtime optional extra `web`:

- `fastapi>=0.138.1,<0.139.0`
- `uvicorn>=0.49.0,<0.50.0`
- `python-multipart>=0.0.32,<0.0.33`

No frontend dependencies are approved in this milestone.

## Dependency License Summary

No license concern was found in the supplied Deep Search summary for the approved direct backend and test dependency direction.

## Private-Beta Auth Plan

The API reads `AQH_WEB_TOKEN` and requires `Authorization: Bearer <token>` for all `/api/*` endpoints.

`GET /health` is unauthenticated.

Token comparison uses constant-time comparison.

## Endpoint Design

- `GET /health`
- `POST /api/jobs`
- `POST /api/compare-jobs`
- `GET /api/jobs/{job_id}`
- `GET /api/jobs/{job_id}/artifacts/{artifact_name}`
- `DELETE /api/jobs/{job_id}`
- `POST /api/maintenance/cleanup`

`GET /` returns a local private dashboard with a token field, upload form, mode selector, job status area, artifact actions, metric cards, visualization preview, metadata panel, raw JSON preview, supported/deferred mode lists, and safety note. The page uses plain HTML, inline CSS, and minimal vanilla JavaScript only.

The dashboard renders only generated JSON artifact data. It does not add fake metrics, fake percentages, or platform/distributor outcome language.

`POST /api/jobs` validates the requested single-file mode, validates and stores the uploaded file, executes the selected safe single-file mode synchronously, writes generated JSON artifacts, updates `status.json`, and returns job metadata.

`POST /api/compare-jobs` validates the requested two-file mode, validates and stores fixed `before_file` and `after_file` uploads, executes the selected safe two-file mode synchronously, writes generated JSON artifacts, updates `status.json`, and returns job metadata.

## Upload Validation Design

Allowed extensions:

- `.wav`
- `.flac`
- `.mp3`
- `.m4a`
- `.aac`
- `.ogg`
- `.opus`
- `.aif`
- `.aiff`

The default upload limit is `100 MiB`, read from `AQH_MAX_UPLOAD_MIB`. The backend enforces byte count while copying the upload to disk and returns `413` when the limit is exceeded.

MIME/content type is advisory only.

Basic magic-byte checks are implemented for common containers where practical:

- WAV: `RIFF....WAVE`
- FLAC: `fLaC`
- MP3: `ID3` or MPEG frame sync
- OGG/OPUS: `OggS`
- AIFF: `FORM....AIFF` or `FORM....AIFC`
- M4A/AAC: `ftyp` in the initial container header

The checks are conservative container sanity checks and are not full audio decoding.

## Storage Model

The default job root is `.var/private-web/jobs`, configurable with `AQH_WEB_JOB_ROOT`.

Each job uses a random URL-safe job ID and a per-job directory:

- `input/`
- `artifacts/`
- `status.json`

The uploaded single-file input is stored as `input/upload.<ext>`. Two-file inputs are stored as `input/before.<ext>` and `input/after.<ext>`. User filenames are never used as storage paths.

Path helpers resolve paths under the configured job root and reject traversal.

## Cleanup Model

Defaults:

- `AQH_JOB_TTL_HOURS=24`
- `AQH_PARTIAL_TTL_MINUTES=60`

The cleanup helper removes expired complete job directories and older partial job directories.

## Job State Model

Successful job state is `completed`.

Safe processing failure state is `failed`.

The status JSON includes:

- `job_id`
- `status`
- `mode`
- `created_at`
- sanitized input metadata for single-file jobs or sanitized before/after input metadata for two-file jobs
- `completed_at` or `failed_at`
- processing state
- artifact names
- safety notes

## Supported Modes

Supported single-file MVP modes:

- `analyze`
- `release-check`
- `inspect-metadata`
- `clean-metadata`
- `visualize`

Supported two-file MVP modes:

- `compare`
- `visualize-compare`

Generated artifacts:

- `analyze` writes `analysis.json`
- `release-check` writes `release_check.json`
- `inspect-metadata` writes `metadata.json`
- `clean-metadata` writes `cleaned_output.<ext>`, `metadata_before.json`, `clean_metadata.json`, and `metadata_after.json`
- `visualize` writes `visualization.json`
- `compare` writes `compare.json`
- `visualize-compare` writes `compare.json` and `visual_compare.json`

## Dashboard Rendering

The dashboard can fetch and render generated JSON artifacts.

Metric cards are populated only from fields present in artifacts, including peak, RMS or loudness approximation, clipping sample count, duration, sample rate, channel count, release-check score, and comparison metrics.

Raw JSON remains available in a preview panel.

## Visualization Preview

For `visualize` mode, the dashboard renders:

- waveform preview from `waveform_peaks.peaks`
- spectrogram energy preview from `spectrogram.energy_db`

These previews are generated from artifact data and are not official mastering-standard displays.

For `visualize-compare` mode, the dashboard renders candidate waveform and spectrogram data from `visual_compare.json`, with difference-map energy data as a fallback.

## Metadata Display Cleanup

For `inspect-metadata` mode, the generated `metadata.json` includes a `metadata_display` object for dashboard use.

The display helper preserves detected metadata keys while summarizing embedded cover/image fields and long text values.

Embedded cover fields such as `APIC:Cover` use:

- `embedded_cover: true`
- `display_value: "[embedded image omitted]"`
- optional `mime`
- optional `type`
- optional `size_bytes`

Long text display values are truncated to 500 characters. The uploaded file is not modified.

For `clean-metadata` mode, the web workflow writes the cleaned copy to the artifacts directory and records sanitized before/after metadata reports. The uploaded input is not overwritten.

## Deferred Modes

Deferred until later safe flows:

- `humanize`

Humanize output-audio generation is not implemented in this MVP.

## Safety Boundary

The backend is private beta only.

The backend stores uploads temporarily and must not commit uploaded audio or generated outputs.

The backend must not imply watermark, fingerprint, provenance, C2PA, source-attribution, detector, evasion, detectability, platform-certification, or distributor-guarantee outcomes.

Endpoint responses are technical job-status responses only.

Failures must not expose tracebacks in status JSON or API responses.

## Test Plan

Tests cover:

- unauthenticated health
- missing and invalid bearer tokens
- valid bearer token
- valid tiny WAV upload
- uppercase extension handling
- disallowed and missing extensions
- empty files
- oversize uploads with `413`
- filename traversal protection
- random-looking job IDs
- storage under the configured root
- artifact traversal rejection
- cleanup of expired jobs
- JSON-safe status files
- endpoint response wording
- operator page rendering and safe wording
- dashboard artifact preview rendering
- sanitized metadata display for embedded images and long fields
- generated artifacts for analyze, release-check, inspect-metadata, clean-metadata, visualize, compare, and visualize-compare
- fixed before/after storage paths for two-file uploads
- downloadable cleaned output artifacts
- completed and failed job states
- design and safety documentation

## Generated Artifact Policy

Do not commit uploaded audio, generated web reports, generated audio, local job directories, or `v015_web_outputs/`.

`.var/`, `v013_web_outputs/`, and `v015_web_outputs/` are ignored by Git.

## Not Approved

- no frontend framework
- no React, Vite, Next, wavesurfer.js, Meyda, three.js, or audioMotion-analyzer
- no static asset build chain
- no deployment
- no DNS config
- no public launch
- no final legal, privacy, or GDPR public text
- no accounts, OAuth, database, Redis, Celery, billing, analytics, or multi-tenant storage
- no audio algorithm changes
- no `humanize` or other output-audio processing modes
- no fake metrics
- no platform or distributor guarantees

## Future Relationship

This working local backend MVP is a private-beta foundation for a future upload interface at `release.datenpflege-nord.de`.

Public launch, hosting, deployment, frontend framework work, and final legal/privacy copy remain deferred.

## Project Boundary

Historical reference files remain outside the active package and are not copied, imported, executed, packaged, or exposed.
