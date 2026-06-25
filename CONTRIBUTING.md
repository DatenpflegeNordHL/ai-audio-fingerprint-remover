# Contributing

## Setup

```bash
python -m pip install -e ".[dev,test]"
```

## Checks

```bash
pytest
python tools/safety_scan.py
python tools/cli_smoke.py
python tools/build_check.py
```

Run the packaging build check before releases so the wheel install and `ai-humanizer` console script are verified outside editable mode.

## Safety Boundary

This project is an audio metadata, quality, release-readiness, compare, and conservative processing tool. It must not add detector, remover, bypass, provenance-removal, C2PA-removal, or source-attribution removal behavior.

Do not add features that claim or attempt to remove watermarks, remove fingerprints, bypass detectors, suppress provenance, remove origin markers, reduce attribution, or reduce detectability.

Original input files must never be modified. Any command that writes audio must write to an explicit output path and keep the original untouched.

All new write commands need before/after analysis or tests that prove the original input remains unchanged.

Documentation must not make unsafe public feature claims. Run the safety scan before opening a pull request.
