# v0.10.0 Release Notes

Version: `0.10.0`

Release type: safe core

Tag: `v0.10.0`

## Summary

- Added signal guardrails for analysis and workflow reporting.
- Added minimal performance metadata helpers.
- Added synthetic regression tests for edge-case audio handling.
- Kept Project Reborn reference-only, non-installed, unpackaged, and hidden from the CLI.

## Validation Summary

A local user-supplied validation track failed the release-readiness check because of clipping and a full-scale peak.

The final balanced export passed the release-readiness check and cleared clipping in the technical preflight.

No local audio, generated reports, or validation outputs are committed with this release.

## Safety Boundary

This release does not remove watermarks.

This release does not remove fingerprints.

This release does not remove provenance markers, origin markers, C2PA markers, or source-attribution systems.

This release does not bypass detectors.

This release does not add recognition failure testing.

Project Reborn was not imported, executed, packaged, or exposed through the CLI.

## Known Limitation

Club loudness warnings can remain because the preflight is a technical readiness check, not full mastering certification.

## Next Planned Area

- v0.10.1 documentation polish.
- Later deeper review for deferred Project Reborn candidates `reborn_025` and `reborn_005`.
