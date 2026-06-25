# Candidate Reality Gate

Status: required for future feature candidates

Deep Search decision: required per candidate

This gate applies before any future feature candidate can move from planning into active package work. It is a design, safety, and validation checklist. It does not add runtime behavior by itself.

## Required Decision Record

Every candidate must document:

- Candidate ID and source planning document.
- Whether Deep Search is needed.
- Deep Search decision value: `required_external_current_facts`, `not_needed_internal_repo_only`, or `not_needed_no_external_claims`.
- Reason for the Deep Search decision.
- Safety boundary and non-goals.
- Synthetic test plan.
- Real local audio validation plan for any user-facing audio behavior.
- No-op check plan for any processing or comparison workflow.
- Expected generated artifacts and why they stay ignored by Git.

## Required Validation

Synthetic tests are required for every candidate.

Synthetic tests alone are not enough for user-facing audio behavior.

Real local audio validation is required before user-facing audio behavior can ship.

No-op checks are required before user-facing audio behavior can ship.

Generated local validation outputs must stay ignored and uncommitted.

## Required No-Op Check

A no-op check must prove that unchanged input stays unchanged according to the candidate boundary.

At minimum, the check must document:

- Input fixture or local validation sample source.
- Command or callable boundary.
- Expected unchanged fields.
- Expected changed fields, if any.
- Failure behavior.

## Forbidden Claims

Reports must not imply watermark removal.

Reports must not imply fingerprint removal.

Reports must not imply detector bypass.

Reports must not imply recognition failure.

Reports must not imply provenance suppression.

Reports must not imply origin marker removal.

Reports must not imply C2PA marker removal.

Reports must not imply source-attribution removal.

Reports must not imply reduced detectability.

Reports must not imply legal clearance, distributor acceptance, or platform certification.

## Project Reborn Boundary

Project Reborn source files remain reference-only.

Future candidates may inspect Project Reborn files as text.

Future candidates must not execute, import, copy, package, or expose Project Reborn source.

Useful ideas must be rewritten from first principles inside the active package only after this gate passes.

## Done Criteria

- Candidate Reality Gate JSON exists and validates.
- Candidate planning document names the Deep Search decision.
- Candidate planning document names synthetic tests.
- Candidate planning document names real local audio validation when user-facing audio behavior is involved.
- Candidate planning document names no-op checks when user-facing audio behavior is involved.
- Safety scan passes.
- Project Reborn check passes.
- Generated audio and reports are ignored and uncommitted.
