# Contributing

## Setup

```bash
python -m pip install -e ".[test]"
```

## Checks

```bash
pytest
python tools/safety_scan.py
python tools/cli_smoke.py
```

## Safety Boundary

This project is an audio metadata, quality, release-readiness, compare, and conservative processing tool. It must not add detector, remover, bypass, provenance-removal, C2PA-removal, or source-attribution removal behavior.

Do not add features that claim or attempt to remove watermarks, remove fingerprints, bypass detectors, suppress provenance, remove origin markers, reduce attribution, or reduce detectability.

Original input files must never be modified. Any command that writes audio must write to an explicit output path and keep the original untouched.

All new write commands need before/after analysis or tests that prove the original input remains unchanged.

Documentation must not make unsafe public feature claims. Run the safety scan before opening a pull request.
