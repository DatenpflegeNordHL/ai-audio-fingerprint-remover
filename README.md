# audio-quality-humanizer

`audio-quality-humanizer` is a local CLI for metadata inspection, ordinary metadata cleaning, provenance-risk inspection, future audio quality analysis, future release-readiness checking, and future authorized rebuild workflows for owned/licensed tracks only.

The v0.1 MVP is intentionally narrow. It helps you see what editable metadata is present, identify metadata keys that may be related to provenance or generation context, and create a copied audio file with ordinary user-editable tags removed where supported by local metadata libraries.

## Safety Boundary

This tool does not remove audio watermarks.

This tool does not remove audio fingerprints.

This tool does not bypass detectors.

This tool does not remove provenance markers or origin markers.

Metadata cleaning may remove ordinary user-editable tags such as title, artist, album, comments, or similar container metadata. Metadata keys that look potentially provenance-related are reported as a risk signal and are not silently removed by default.

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

Each command runs locally and writes a JSON report when `--report` is provided.

## Roadmap

- v0.1 metadata cleaner
- v0.2 analyze
- v0.3 release-check
- v0.4 compare
- v0.5 conservative humanize
- later authorized rebuild for owned/licensed tracks only

## License

This project is licensed under the MIT License. See `LICENSE` for details.
