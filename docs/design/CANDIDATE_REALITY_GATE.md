# Candidate Reality Gate

## Status

Required for every future user-facing audio feature candidate.

## Rule

Synthetic tests are required, but not sufficient.

A candidate is not considered done until it has been checked against real local user-supplied audio data.

## Why

Synthetic tests prove edge-case behavior.

Real audio validation proves the feature is not placebo code.

## Required Gates

### 1. Candidate Behavior Description

Before implementation, describe what the candidate is supposed to do in measurable terms.

### 2. Safety Boundary

List what the candidate must not do.

### 3. Deep Search Decision

Record whether external research is needed.

Every candidate must document a Deep Search decision.

Allowed values:

- `not_needed_internal_repo_only`
- `needed_external_standards`
- `needed_current_library_behavior`
- `needed_platform_or_policy_claims`
- `needed_market_or_product_research`
- `needed_security_or_safety_policy_check`

If the decision is anything except `not_needed_internal_repo_only`, stop and request user update before continuing.

### 4. Synthetic Tests

Synthetic tests are required for every candidate.

Synthetic tests must cover:

- normal input
- quiet or silent input
- short input
- mono/stereo shape
- NaN/inf where relevant
- edge-case values

### 5. Real Local Audio Validation

A user-facing audio candidate must be tested with at least one local user-supplied audio file.

Validation must record:

- input command
- output command
- JSON report path
- Markdown report path if available
- expected measurable behavior
- actual measured behavior
- pass/fail decision

Do not commit the local audio file.

Do not commit generated local validation outputs unless they are tiny synthetic fixtures explicitly created for tests.

Generated local validation outputs must stay ignored and uncommitted.

### 6. No-Op Check

A no-op check must prove that unchanged input stays unchanged according to the candidate boundary.

The candidate must prove it is not just decorative JSON.

Examples:

- metric values change when comparing different files
- warnings appear for known problematic input
- report fields are populated from real calculations
- output validation catches actual shape, peak, or sample-rate issues

### 7. Safe Wording Check

Reports must not imply watermark removal.

Reports must not imply detector bypass.

Reports must not imply fingerprint removal.

Reports must not imply recognition failure.

Reports must not imply provenance removal.

Reports must not imply origin marker removal.

Reports must not imply C2PA marker removal.

Reports must not imply source-attribution removal.

Reports must not imply reduced detectability.

Reports must not imply legal clearance, distributor acceptance, or platform certification.

### 8. Done Criteria

A candidate is done only when:

- synthetic tests pass
- real local validation is documented
- no-op check passes
- safe wording check passes
- safety scan passes
- root cleanliness passes
- Project Reborn check passes
- CLI smoke passes
- build check passes

## Project Reborn Boundary

Project Reborn source files remain reference-only.

Future candidates may inspect Project Reborn files as text.

Future candidates must not execute, import, copy, package, or expose Project Reborn source.

Useful ideas must be rewritten from first principles inside the active package only after this gate passes.
