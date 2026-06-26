# v0.11.3 Web Upload and Spectrum Visualization MVP Design

## Status

Design only. No implementation.

## Goal

Create a future private-beta web interface for `release.datenpflege-nord.de` where users can upload audio, run safe `ai-humanizer` workflows, see a polished before/after visualization, and download processed outputs and reports.

## Recommended Subdomain

`release.datenpflege-nord.de`

Reason:
It communicates outcome and avoids unsafe AI-removal framing.

## User Flow

1. Upload audio file.
2. Run safe pre-analysis.
3. Show original waveform, metrics, and spectrum.
4. User chooses a safe mode.
5. Backend creates processing job.
6. Show job progress.
7. Show processed waveform, metrics, and spectrum.
8. Show difference map.
9. Allow download of processed audio, JSON report, Markdown report, and optional ZIP bundle.

## Visual Concept

The interface should feel premium, technical, and trustworthy.

Core visual elements:

- animated upload scanner
- waveform timeline
- original spectrum view
- processed spectrum view
- before/after toggle
- difference heatmap
- metric cards
- hover tooltips on changed regions
- download panel

## Spectrum and Difference Visualization

Design three synchronized views:

1. Original Spectrum
2. Processed Spectrum
3. Difference Map

The Difference Map must visualize only measurable changes from backend reports or generated spectrogram-difference data.

Allowed labels:

- clipping reduced
- peak adjusted
- RMS changed
- dynamic range changed
- spectral centroid changed
- spectral rolloff changed
- stereo correlation changed
- side energy changed
- metadata cleaned

Forbidden labels:

- No UI label may say `fingerprint removed`.
- No UI label may say `watermark removed`.
- No UI label may say `AI trace removed`.
- No UI label may say `detector bypassed`.
- No UI label may say `undetectable`.
- No UI label may say `hidden identifier removed`.
- No UI label may say `provenance removed`.
- No UI label may say `source attribution removed`.
- No UI label may say `C2PA removed`.

## Color Semantics

Use color only for measured technical status:

- blue: unchanged or neutral
- green: improved or stable
- yellow: noticeable change
- orange: warning
- red: critical issue detected before processing
- violet: processed/changed region

Do not use color to imply watermark, fingerprint, detector, provenance, origin, or source-attribution removal.

## Tooltip Concept

Hover tooltip examples:

Example 1:
Time: 01:24.8
Frequency band: 8-12 kHz
Change: -2.1 dB average energy
Related metric: spectral_rolloff_delta_hz
Note: High-frequency energy changed after processing.

Example 2:
Issue: Clipping detected before processing
Before: 53 clipped samples
After: 0 clipped samples
Status: improved

Example 3:
Metadata:
Standard metadata fields removed: 4
Audio samples changed: no
Status: metadata cleanup only

## Candidate Frontend Libraries

Document these as design candidates only. Do not add dependencies yet.

### wavesurfer.js

Use for:

- waveform
- timeline
- playback
- regions
- possible spectrogram plugin

License note:
BSD-3-Clause according to project documentation.

### Meyda

Use for:

- browser-side audio feature extraction experiments
- RMS
- spectral centroid
- spectral rolloff
- realtime or offline feature displays

License note:
MIT according to GitHub.

### three.js

Use only for optional hero animation, not core report correctness.

Possible use:

- animated spectral tunnel
- loading scanner
- background visual identity

License note:
MIT according to GitHub.

### audioMotion-analyzer

Use as visual inspiration only unless license is explicitly approved later.

Reason:
It is visually strong for spectrum animation, but its AGPL-3.0 license requires separate approval before dependency use.

## Recommended MVP Technical Approach

For the first implementation, prefer backend-generated visualization data over browser-side claims.

Backend should generate:

- JSON metrics
- Markdown report
- optional downsampled waveform peaks
- optional spectrogram matrix
- optional difference matrix

Frontend should render:

- waveform from peaks or audio file
- spectrum image/matrix
- difference overlay
- metric cards from report JSON
- hover tooltips from backend-provided region metadata

Do not invent regions client-side unless they are clearly marked as visual-only.

## Architecture

Recommended MVP:

- Frontend: small private-beta upload interface
- Backend: Python API wrapper around existing `ai-humanizer` CLI
- Worker: job runner for processing
- Storage: temporary per-job folders
- Reports: JSON and Markdown
- Visualization artifacts: safe JSON matrices or PNG previews
- Download: processed file and reports
- Cleanup: automatic deletion after retention period

Suggested endpoints:

- `POST /jobs`
- `GET /jobs/{job_id}`
- `GET /jobs/{job_id}/visualization/original`
- `GET /jobs/{job_id}/visualization/processed`
- `GET /jobs/{job_id}/visualization/difference`
- `GET /jobs/{job_id}/download/{artifact}`
- `DELETE /jobs/{job_id}`

## Private Beta Requirement

Initial version must be password-protected.

Required protections:

- basic auth or simple login
- max upload size
- allowlisted file extensions
- MIME sniffing where practical
- random job IDs
- path traversal protection
- no public directory listing
- automatic deletion
- rate limiting
- server-side timeout
- no logging of full file contents
- no committing uploaded audio or generated outputs

## Generated Artifacts

Possible artifacts:

- processed audio
- JSON report
- Markdown report
- waveform peaks JSON
- original spectrogram preview
- processed spectrogram preview
- difference heatmap preview
- ZIP bundle

Generated outputs must stay temporary and uncommitted.

## Data Retention

Default proposed retention:
24 hours

All files should be deleted automatically after retention expires.

## FAQ Draft

### What does this tool do?

It checks audio files for technical quality, metadata, release-readiness, and safe before/after differences. Some modes can create a processed output using conservative audio-quality settings.

### What does the spectrum view show?

It shows measurable energy distribution over time and frequency. The difference view highlights measurable technical changes between original and processed audio.

### Does a highlighted area mean a watermark or fingerprint was removed?

No. Highlighted areas only show measured technical differences such as peak, RMS, clipping, spectral centroid, spectral rolloff, stereo correlation, side energy, or metadata changes.

### Does it change my audio?

Analyze, release-check, inspect-metadata, and compare are read-only. Clean-metadata changes metadata only. Conservative humanize can create a processed audio output.

### Does it remove AI fingerprints or watermarks?

No. The tool does not remove watermarks, fingerprints, provenance, C2PA markers, source-attribution markers, or detector signals.

### Does it make AI music undetectable?

No. The tool is not designed to bypass detectors or mislead recognition systems.

### Is this mastering?

No. It provides technical reports and conservative processing. It does not guarantee platform acceptance or replace professional mastering.

### What happens to uploaded files?

Files are processed temporarily and deleted automatically after the retention period.

### Are reports included?

Yes. Reports can be generated as JSON and Markdown.

## Safety Copy

Public UI must say:

This tool provides audio-quality checks, metadata privacy cleanup, conservative processing, before/after visualization, and technical reports. It does not remove watermarks, fingerprints, provenance, C2PA markers, or source-attribution markers. It does not bypass detection systems.

## Future Implementation Plan

Future implementation should be separate from this design milestone.

Possible future milestone:
`v0.13.1 Web Upload Visualization MVP Implementation`

Implementation requirements:

- real local upload validation
- no-op test for read-only modes
- file cleanup test
- forbidden wording test
- safe CLI mapping test
- basic auth test
- path traversal test
- upload size limit test
- generated artifact ignore test
- visualization artifact JSON-safety test
- tooltip data correctness test
- full project checks

## Not Approved In This Milestone

- no web implementation
- no deployment
- no new runtime dependencies
- no new audio features
- no public launch
- no unsafe claims

No web implementation is approved by this design milestone.

## Deep Search Decision

`not_needed_internal_repo_only`

Reason:
This milestone creates internal design documents for a future web wrapper and visualization layer around existing safe CLI behavior. It does not add dependencies or implement third-party libraries.

## Project Reborn Boundary

Project Reborn remains reference-only, non-installed, not imported, not executed, not packaged, and hidden from the CLI.
