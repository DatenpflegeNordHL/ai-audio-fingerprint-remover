# v0.11.0 Release Notes

Version: `0.11.0`

Tag: `v0.11.0`

Release type: safe read-only compare metrics

## Summary

The existing `compare` workflow now includes `comparison_metrics`.

No new CLI command was added.

No audio modification was added.

Release-check scoring did not change.

Humanize behavior did not change.

## Implemented Metrics

- `rmse`
- `mean_absolute_error`
- `correlation`
- `snr_db_approx`
- peak before/after/delta
- RMS before/after/delta
- dynamic range before/after/delta
- spectral centroid before/after/delta
- spectral rolloff before/after/delta
- stereo correlation before/after/delta
- side energy ratio before/after/delta

## Validation Summary

Synthetic tests passed.

Real local validation passed with a user-supplied local track.

No generated validation outputs are committed.

## Safety Boundary

This release is read-only quality comparison.

This release does not add watermark removal.

This release does not add fingerprint removal.

This release does not add provenance removal.

This release does not add origin marker removal.

This release does not add C2PA marker removal.

This release does not add source-attribution removal.

This release does not add detector APIs.

This release does not add recognition APIs.

This release does not add bypass or evasion APIs.

This release does not make platform-certification claims.

## Project Reborn Boundary

`reborn_025` was used only as a design reference after review.

The active implementation was rewritten from first principles.

Project Reborn source was not copied, imported, executed, packaged, or exposed.

## Known Limitations

`snr_db_approx` is approximate and internal.

Loudness-related values are not official EBU/ITU LUFS certification.

Metrics are comparison and reporting aids, not mastering certification.
