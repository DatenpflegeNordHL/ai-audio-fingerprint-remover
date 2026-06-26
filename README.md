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

## Candidate Reality Gate

Future audio features must pass the Candidate Reality Gate: synthetic tests, real local audio validation, no-op check, safe wording check, and a documented Deep Search decision.

If external current information is required, work stops until the user provides a research update or approves a constrained internal-only scope.

See `docs/design/CANDIDATE_REALITY_GATE.md`. The deferred `reborn_025` deep review is documented at `docs/design/REBORN_025_DEEP_REVIEW.md`. The deferred `reborn_005` deep review is documented at `docs/design/REBORN_005_DEEP_REVIEW.md`.

See `project_reborn/catalog/PROJECT_REBORN_CATALOG.md`.

Each command runs locally and writes a JSON report when `--report` is provided. Analyze, release-check, compare, humanize, doctor, batch, preset-eval, and validate-samples can also write Markdown reports with `--markdown`.

## Release notes

- `v0.10.0`: `docs/releases/V0_10_0_RELEASE_NOTES.md`
- `v0.11.0`: `docs/releases/V0_11_0_RELEASE_NOTES.md`

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
