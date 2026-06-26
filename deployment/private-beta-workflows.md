# Private Beta Workflow Layer

This document describes the private beta workflow layer for `beta.datenpflege-nord.de`.

The workflow layer is available only through the existing private FastAPI app behind the Cloudflare Tunnel. It is not a public launch, not a marketing surface, and not an official public DatenpflegeNord product.

## Available Workflows

### Quick Scan

Checks audio quality, metadata, and release readiness without modifying the uploaded file.

Expected artifacts:

- `quick_scan_summary.md`
- `analysis.json`
- `metadata.json`
- `release_check.json`
- `visualization.json`

### Metadata Clean

Cleans supported standard metadata fields and non-essential visible container tags where technically supported, then compares before/after metadata state.

Expected artifacts:

- cleaned audio artifact
- `metadata_before.json`
- `metadata_after.json`
- `metadata_diff.md`
- `metadata_clean_summary.md`
- `hashes.json`

### Quality Naturalize

Applies conservative audio-quality micro-variations for less sterile playback characteristics, then compares before/after quality reports.

Expected artifacts:

- naturalized audio artifact
- `release_check_before.json`
- `release_check_after.json`
- `compare.json`
- `quality_naturalize_summary.md`
- `hashes.json`

### Full Release Pass

Runs cleanup, conservative naturalization, final checks, comparison, hashes, and workflow summaries in one private beta workflow.

Expected artifacts:

- final audio artifact
- `workflow_summary.md`
- `workflow_summary.json`
- `metadata_before.json`
- `metadata_after.json`
- `metadata_diff.md`
- `release_check_before.json`
- `release_check_final.json`
- `compare.json`
- `hashes.json`

## API Behavior

`GET /api/config` returns `workflow_modes` and `workflows` so the private dashboard can discover supported workflows.

`POST /api/jobs` accepts either an existing single-file mode or a workflow name in the `mode` form field. Workflow jobs are stored with:

- `mode: "workflow"`
- `workflow_name`
- `workflow_label`
- step-level `steps`
- grouped `artifact_groups`

All `/api/*` endpoints continue to require Bearer token auth.

The dashboard root remains protected by the beta password.

`/health` remains public for the private beta tunnel health check.

Artifact downloads remain limited to files listed in each job `status.json`.

## Server Notes

The intended private beta target remains:

- Hostname: `beta.datenpflege-nord.de`
- Local service: `127.0.0.1:8017`
- Service unit: `audio-quality-humanizer-web`
- Deploy path: `/srv/audio-quality-humanizer-private-beta`

Do not route this workflow layer to the root domain, `www`, or any public marketing page.
