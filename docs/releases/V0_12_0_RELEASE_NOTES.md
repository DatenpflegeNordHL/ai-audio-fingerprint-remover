# v0.12.0 Release Notes

Tag: `v0.12.0`

v0.12.0 added read-only visualization artifacts for future UI rendering. No web app, web server, frontend bundle, deployment config, or runtime frontend dependency was added.

## CLI Commands

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

Both commands are read-only. They inspect audio and write JSON reports when `--report` is provided. They do not modify input audio.

## Artifact Contents

Single-file artifacts include:

- `schema_version`
- `source`
- `waveform_peaks`
- `spectrogram`
- `metric_cards`
- `tooltip_regions`
- `safety_notes`

Before/after artifacts include:

- `schema_version`
- `reference`
- `candidate`
- `comparison_metrics`
- `compatibility`
- `difference_map`
- `tooltip_regions`
- `safety_notes`

Waveform peaks are bounded min/max/absolute-peak windows. Spectrogram artifacts are bounded UI preview matrices with summaries. Difference maps report bounded energy deltas and summary statistics for aligned files with matching sample rates.

## Synthetic JSON Examples

Minimal single-file shape:

```json
{
  "action": "visualize",
  "schema_version": "1.0",
  "waveform_peaks": {
    "window_count": 1,
    "peaks": [
      {
        "time_start_seconds": 0.0,
        "time_end_seconds": 0.1,
        "min": -0.2,
        "max": 0.2,
        "abs_peak": 0.2
      }
    ]
  },
  "spectrogram": {
    "time_bins": [0.0],
    "frequency_bins_hz": [0.0],
    "energy_db": [[-60.0]],
    "summary": {
      "time_bin_count": 1,
      "frequency_bin_count": 1,
      "official_standard": false
    }
  },
  "tooltip_regions": [],
  "safety_notes": [
    "Visualization artifacts show measured technical audio features only."
  ]
}
```

Minimal comparison difference-map shape:

```json
{
  "action": "visualize-compare",
  "schema_version": "1.0",
  "difference_map": {
    "time_bins": [0.0],
    "frequency_bins_hz": [0.0],
    "energy_delta_db": [[0.0]],
    "summary": {
      "comparison_available": true,
      "mean_abs_delta_db": 0.0,
      "max_abs_delta_db": 0.0,
      "changed_bin_count": 0,
      "changed_bin_ratio": 0.0,
      "delta_threshold_db": 1.0
    }
  },
  "tooltip_regions": []
}
```

These examples are synthetic and intentionally minimal.

## Real Local Validation

Real local validation covered:

- a single-file visualization report for a local audio sample
- a no-op comparison of the same local sample against itself
- a before/after comparison of local original and processed exports

The no-op comparison produced zero mean delta, zero max delta, zero changed bins, and no tooltip labels. The before/after comparison produced measured waveform, metric, and spectral-energy changes. Generated validation reports remained ignored and uncommitted.

## Limitations

Visualization artifacts are not mastering certification.

Visualization artifacts do not predict platform or distributor acceptance.

Visualization artifacts do not evaluate or remove watermarks, fingerprints, provenance, C2PA markers, source-attribution markers, detector signals, or platform acceptance.

Spectrogram matrices are downsampled UI preview data, not an official measurement standard.

## Project Reborn Boundary

Project Reborn source was not copied, imported, executed, packaged, or exposed.
