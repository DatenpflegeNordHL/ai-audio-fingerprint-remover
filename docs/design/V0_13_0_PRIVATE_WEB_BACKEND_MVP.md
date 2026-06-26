# v0.13.0 Private Web Backend MVP

## Status

Implemented backend skeleton.

## Deep Search Summary

Deep Search decision: `needed_current_library_behavior`.

Deep Search was completed before implementation. The approved stack is FastAPI, Uvicorn, and python-multipart as an optional `web` extra. The backend uses FastAPI `UploadFile`, bearer-token auth for private beta access, one uploaded file per request, random job IDs from `secrets.token_urlsafe`, and temporary per-job directories under a controlled local root.

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
- `GET /api/jobs/{job_id}`
- `GET /api/jobs/{job_id}/artifacts/{artifact_name}`
- `DELETE /api/jobs/{job_id}`
- `POST /api/maintenance/cleanup`

`POST /api/jobs` validates the requested single-file mode, validates and stores the uploaded file, writes `status.json`, and returns job metadata. Processing execution is deferred in this skeleton.

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

The uploaded file is stored as `input/upload.<ext>`. User filenames are never used as storage paths.

Path helpers resolve paths under the configured job root and reject traversal.

## Cleanup Model

Defaults:

- `AQH_JOB_TTL_HOURS=24`
- `AQH_PARTIAL_TTL_MINUTES=60`

The cleanup helper removes expired complete job directories and older partial job directories.

## Job State Model

Initial job state is `uploaded`.

The status JSON includes:

- `job_id`
- `status`
- `mode`
- `created_at`
- sanitized input metadata
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

## Deferred Modes

Deferred until later safe flows:

- `visualize-compare`
- `compare`
- `humanize`

Two-file comparison and output-audio generation are not implemented in this skeleton.

## Safety Boundary

The backend is private beta only.

The backend stores uploads temporarily and must not commit uploaded audio or generated outputs.

The backend must not imply watermark, fingerprint, provenance, C2PA, source-attribution, detector, evasion, detectability, platform-certification, or distributor-guarantee outcomes.

Endpoint responses are technical job-status responses only.

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
- design and safety documentation

## Generated Artifact Policy

Do not commit uploaded audio, generated web reports, generated audio, local job directories, or `v013_web_outputs/`.

`.var/` and `v013_web_outputs/` are ignored by Git.

## Not Approved

- no frontend UI
- no React, Vite, Next, wavesurfer.js, Meyda, three.js, or audioMotion-analyzer
- no static asset build chain
- no deployment
- no DNS config
- no public launch
- no final legal, privacy, or GDPR public text
- no accounts, OAuth, database, Redis, Celery, billing, analytics, or multi-tenant storage
- no audio processing behavior changes

## Future Relationship

This backend skeleton is a private-beta foundation for a future upload interface at `release.datenpflege-nord.de`.

Public launch, hosting, deployment, frontend UI, and final legal/privacy copy remain deferred.

## Project Boundary

Historical reference files remain outside the active package and are not copied, imported, executed, packaged, or exposed.
