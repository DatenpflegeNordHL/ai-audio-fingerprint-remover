# Private Beta Preflight Checklist

## Release

- `git fetch --tags`
- `git checkout v0.18.0`
- `git status --short` is clean
- `.venv/bin/ai-humanizer --version` reports `audio-quality-humanizer 0.18.0`

## Server Directory

- deployment path is outside any public web root
- server-only `.env` or `web.env` exists outside Git
- temporary jobs directory is writable by the service
- temporary jobs directory is not included in backups

## Required Environment

- `AQH_WEB_HOST=127.0.0.1`
- `AQH_WEB_PORT=8017`
- `AQH_WEB_MAX_UPLOAD_MB=50`
- `AQH_WEB_JOB_TTL_HOURS=24`
- `AQH_WEB_MAX_ACTIVE_JOBS=1`
- `AQH_WEB_TOKEN` is set outside Git
- `AQH_BETA_PASSWORD_HASH` or `AQH_BETA_PASSWORD` is set outside Git

## Cloudflare Tunnel

- existing tunnel is available
- public hostname is `beta.datenpflege-nord.de`
- service target is `http://localhost:8017`
- no router port forwarding
- no direct public Uvicorn port
- upload and artifact endpoints are not cached

## Boundaries

- no public launch
- no marketing
- no SEO
- no analytics
- no DatenpflegeNord dashboard integration
- no database
- no queue
- no user accounts
