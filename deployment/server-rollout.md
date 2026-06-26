# Private Beta Server Rollout

This runbook is for deploying the private side-project beta on the existing DatenpflegeNord home server behind the already configured Cloudflare Tunnel.

It is not an official public DatenpflegeNord product. Do not advertise it on `datenpflege-nord.de`, do not link it from the DatenpflegeNord dashboard, and do not add public launch, marketing, SEO, sitemap, analytics, or official product positioning.

## Target

- public hostname: `beta.datenpflege-nord.de`
- public entry: existing Cloudflare Tunnel
- local service: `http://localhost:8017`
- Uvicorn bind: `127.0.0.1:8017`
- no router port forwarding
- no direct Uvicorn internet exposure

## Manual Values Dustin Provides Outside Git

- real deployment path
- real beta password or password hash
- real `AQH_WEB_TOKEN`
- final Cloudflare Tunnel target
- final chosen runtime method
- final retention TTL if different from `24`

## 1. Confirm Clean Release

```bash
git fetch --tags
git checkout v0.17.0
git status --short
.venv/bin/ai-humanizer --version
```

Expected version for this rollout target:

```text
audio-quality-humanizer 0.17.0
```

## 2. Prepare Server Directory

Choose a server-only path outside any public web root.

```bash
mkdir -p /srv/audio-quality-humanizer-private-beta
cd /srv/audio-quality-humanizer-private-beta
```

Clone or update the repository according to the home-server convention, then check out `v0.17.0`.

## 3. Create Server-Only Environment File

Create a server-only `.env` or `web.env` file. Do not commit this file.

Required values:

```bash
AQH_WEB_HOST=127.0.0.1
AQH_WEB_PORT=8017
AQH_WEB_MAX_UPLOAD_MB=50
AQH_WEB_JOB_TTL_HOURS=24
AQH_WEB_MAX_ACTIVE_JOBS=1
AQH_WEB_TOKEN=<server-only secret>
AQH_BETA_PASSWORD_HASH=<server-only value>
```

Temporary private beta alternative:

```bash
AQH_BETA_PASSWORD=<server-only value>
```

Set the server jobs directory:

```bash
AQH_WEB_JOBS_DIR=/app/.var/private-web/jobs
```

For a non-container systemd-style deployment, use an absolute writable path on the home server instead.

## 4. Start Service

Docker Compose is preferred if it matches the existing home-server setup. Use the example as a template, not as a secret-bearing file:

```bash
docker compose -f deployment/docker/docker-compose.example.yml up -d
```

The published host mapping must stay local:

```text
127.0.0.1:8017:8017
```

systemd remains an optional alternative using `deployment/systemd/audio-quality-humanizer-web.service.example`.

## 5. Verify Local

```bash
curl -i http://127.0.0.1:8017/health
```

Expected: HTTP `200` with minimal OK status.

## 6. Verify Cloudflare Tunnel

Manual Cloudflare Tunnel route:

```text
Public hostname: beta.datenpflege-nord.de
Service: http://localhost:8017
```

Confirm:

- existing tunnel is running
- public hostname points to the existing tunnel
- service target is `http://localhost:8017`
- no local ports are public
- no router port forwarding exists
- upload and artifact endpoints are not cached
- Cloudflare upload limit is at or below the app limit

## 7. Verify Remote

Use `deployment/smoke-test.md` or `scripts/private-beta-smoke.sh`.

Required observations:

- dashboard without password returns `401`
- dashboard with password returns `200`
- `/health` returns minimal OK if intentionally public
- `/api/config` requires `AQH_WEB_TOKEN`
- oversized upload returns `413`
- active job limit can return `429`

## 8. Verify Logs

Review local service logs and Cloudflare-visible metadata according to the home-server process.

Confirm logs do not include:

- `AQH_WEB_TOKEN`
- beta password or password hash
- raw uploaded file content
- unnecessary original upload filenames

## 9. Verify Cleanup

Confirm:

- jobs and artifacts are temporary
- upload/output directories are not backed up
- TTL is configured, initially `24` hours
- cleanup endpoint stays authenticated

Manual cleanup check:

```bash
curl -sS -X POST \
  -H "Authorization: Bearer $AQH_WEB_TOKEN" \
  http://127.0.0.1:8017/api/maintenance/cleanup
```

## 10. Rollback

Use `deployment/rollback.md`.
