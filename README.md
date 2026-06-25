# audio-quality-humanizer

`audio-quality-humanizer` is a local CLI for metadata inspection, ordinary metadata cleaning, provenance-risk inspection, future audio quality analysis, future release-readiness checking, and future authorized rebuild workflows for owned/licensed tracks only.

The v0.1 MVP helps you see what editable metadata is present, identify metadata keys that may be related to provenance or generation context, and create a copied audio file with ordinary user-editable tags removed where supported by local metadata libraries.

The v0.2 and v0.3 commands add read-only audio quality analysis and release-readiness preflight checks. These checks are pragmatic technical reports, not official distributor or platform certification.

The v0.4 compare command checks whether a candidate file introduces technical quality or release-readiness regressions relative to a reference file.

The v0.5 humanize command adds conservative audio-quality processing presets guarded by before/after analysis, compare, and safety gates.

The v0.6 workflow commands add `doctor` for one-file release preflights and `batch` for running existing commands across folders.

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

## Installation

```bash
pip install -e .[test]
```

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

Each command runs locally and writes a JSON report when `--report` is provided. Analyze, release-check, compare, humanize, doctor, and batch can also write Markdown reports with `--markdown`.

## Roadmap

- v0.1 metadata cleaner
- v0.2 analyze
- v0.3 release-check
- v0.4 compare implemented
- v0.5 conservative humanize implemented
- v0.6 doctor/batch workflow implemented
- future: CI hardening, optional standards-compliant LUFS, optional true-peak approximation
- later authorized rebuild for owned/licensed tracks only

## License

This project is licensed under the MIT License. See `LICENSE` for details.
