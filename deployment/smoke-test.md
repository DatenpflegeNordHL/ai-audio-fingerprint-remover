# Private Beta Smoke Test

Run these checks after starting the private beta service.

Do not paste real secrets into shell history if the server shell history is retained. Prefer temporary environment variables in a private shell session.

## Required Environment

```bash
export AQH_WEB_TOKEN="<server-only secret>"
export AQH_BETA_SMOKE_PASSWORD="<server-only beta password>"
export AQH_BASE_URL="https://beta.datenpflege-nord.de"
```

For local-only checks:

```bash
export AQH_BASE_URL="http://127.0.0.1:8017"
```

## Manual Checks

Health:

```bash
curl -i "$AQH_BASE_URL/health"
```

Dashboard gate:

```bash
curl -i "$AQH_BASE_URL/"
curl -i -u "beta:$AQH_BETA_SMOKE_PASSWORD" "$AQH_BASE_URL/"
```

API auth:

```bash
curl -i "$AQH_BASE_URL/api/config"
curl -i -H "Authorization: Bearer $AQH_WEB_TOKEN" "$AQH_BASE_URL/api/config"
```

Cleanup:

```bash
curl -i -X POST -H "Authorization: Bearer $AQH_WEB_TOKEN" "$AQH_BASE_URL/api/maintenance/cleanup"
```

Oversized upload:

Use a local temporary file larger than the configured `AQH_WEB_MAX_UPLOAD_MB` and verify HTTP `413`.

Active job limit:

If a job is intentionally held in an active state during a maintenance test, a second upload may return HTTP `429`.

## Scripted Check

Optional:

```bash
AQH_BASE_URL="https://beta.datenpflege-nord.de" \
AQH_WEB_TOKEN="$AQH_WEB_TOKEN" \
AQH_BETA_SMOKE_PASSWORD="$AQH_BETA_SMOKE_PASSWORD" \
scripts/private-beta-smoke.sh
```
