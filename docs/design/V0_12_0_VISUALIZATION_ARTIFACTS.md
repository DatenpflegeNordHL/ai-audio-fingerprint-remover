# v0.12.0 Visualization Artifacts

## Status

Implemented.

## Deep Search Decision

`not_needed_internal_repo_only`

Reason:
This milestone creates internal visualization artifacts from local audio arrays and existing project analysis/compare behavior.

## Safety Boundary

Visualization artifacts are read-only.

Visualization artifacts show measured technical audio features only. They do not evaluate or remove watermarks, fingerprints, provenance, C2PA markers, source-attribution markers, detector signals, or platform acceptance.

Visualization labels and tooltips must map only to measured technical metrics.

Difference maps must not imply attribution, recognition, provenance, detector, origin, C2PA, source-attribution, bypass, evasion, detectability, platform, or distributor outcomes.

## Generated Artifact Schema

Single-file artifacts use action `visualize`.

Before/after artifacts use action `visualize-compare`.

Both schemas use `schema_version: "1.0"` and must serialize with `json.dumps(..., allow_nan=False)`.

## Waveform Peaks Design

Waveform peaks are compact browser-oriented data.

Each window records:

- start time
- end time
- minimum sample value
- maximum sample value
- absolute peak

The number of windows is capped for predictable report size.

## Spectrogram Design

Spectrogram artifacts include `time_bins`, `frequency_bins_hz`, `energy_db`, and `summary`.

The matrix is downsampled and capped by `--max-time-bins` and `--max-frequency-bins`.

Silence and short audio are handled with finite JSON-safe values.

The spectrogram is a UI preview artifact, not an official measurement standard.

## Difference Map Design

Before/after visualization artifacts include `time_bins`, `frequency_bins_hz`, `energy_delta_db`, and `summary`.

The difference map compares downsampled spectrogram energy for aligned audio when sample rates match.

Summary fields:

- `mean_abs_delta_db`
- `max_abs_delta_db`
- `changed_bin_count`
- `changed_bin_ratio`
- `delta_threshold_db`

Sample-rate mismatch is reported safely and does not produce invented difference values.

## Tooltip Region Design

Tooltip regions are generated from measured technical changes only.

Allowed labels:

- clipping reduced
- peak changed
- RMS changed
- dynamic range changed
- spectral centroid changed
- spectral rolloff changed
- stereo correlation changed
- side energy changed
- spectral energy changed
- metadata changed

Forbidden labels and claims:

- No tooltip may say `fingerprint removed`.
- No tooltip may say `watermark removed`.
- No tooltip may say `AI trace removed`.
- No tooltip may say `detector bypassed`.
- No tooltip may say `undetectable`.
- No tooltip may say `hidden identifier removed`.
- No tooltip may say `provenance removed`.
- No tooltip may say `source attribution removed`.
- No tooltip may say `C2PA removed`.
- No tooltip may say `origin removed`.
- No tooltip may say `detectability reduced`.
- No tooltip may say `platform certified`.
- No tooltip may say `distributor accepted`.

## CLI Usage

Single-file visualization:

```bash
ai-humanizer visualize input.wav \
  --report visualization.json
```

Before/after visualization:

```bash
ai-humanizer visualize-compare before.wav after.wav \
  --report visual_compare.json
```

Optional controls:

```bash
ai-humanizer visualize input.wav \
  --max-time-bins 128 \
  --max-frequency-bins 64 \
  --report visualization.json
```

## No-Op Check Plan

Compare an audio file to itself with `visualize-compare`.

Expected result:

- `mean_abs_delta_db` is `0.0`
- `max_abs_delta_db` is `0.0`
- `changed_bin_count` is `0`
- `changed_bin_ratio` is `0.0`
- tooltip labels remain safe

## Real Local Audio Validation Plan

Real local validation is required before tagging this milestone.

Use local user-supplied files only.

Generated validation artifacts must remain ignored and uncommitted.

Required local validation:

- single-file visualization for a local track
- no-op visualization comparison for the same local track
- before/after visualization comparison for local original and processed files when both exist

## Generated Artifact Policy

Do not commit:

- real audio files
- generated visualization reports
- generated validation outputs
- generated audio files

`v012_validation_outputs/` is ignored by Git.

## Future Web Relationship

These artifacts support the future `release.datenpflege-nord.de` UI design from v0.11.3.

This milestone does not implement a web app, web server, frontend bundle, deployment config, or runtime frontend dependency.

## Limitations

- Spectrogram matrices are downsampled UI preview data.
- Loudness remains approximate where inherited from existing analysis reports.
- Difference maps require matching sample rates to calculate matrix deltas.
- Tooltip regions are candidate regions for UI display, not certification statements.

## Project Reborn Boundary

Project Reborn remains reference-only, non-installed, not imported, not executed, not packaged, and hidden from the CLI.
