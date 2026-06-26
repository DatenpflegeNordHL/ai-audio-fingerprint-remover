# Private Beta Deployment Prep

This directory contains documentation-only deployment prep for the private side-project beta at `beta.datenpflege-nord.de`.

This is not an official public DatenpflegeNord product. Do not advertise it on `datenpflege-nord.de`, do not link it from the DatenpflegeNord dashboard, and do not add public launch, marketing, SEO, sitemap, analytics, or official product positioning.

## Intended Architecture

- Public hostname: `beta.datenpflege-nord.de`
- Public entry: existing Cloudflare Tunnel only
- Local service target: `http://localhost:8017`
- FastAPI/Uvicorn binds locally only
- No direct Uvicorn exposure to the internet
- No router port forwarding
- No local HTTPS termination required
- No Caddy, Nginx, or Certbot required by default

## Required Manual Values Outside Git

Dustin must set these outside the repository:

- final beta password or beta password hash
- `AQH_WEB_TOKEN`
- Cloudflare Tunnel public hostname
- Cloudflare Tunnel local service target
- actual deployment path on the home server
- final upload limit
- final retention TTL

## Runtime Config Names

Use `deployment/env/web.env.example` as a placeholder template only. Do not commit real values.

Required private beta settings:

- `AQH_WEB_HOST`
- `AQH_WEB_PORT`
- `AQH_WEB_TOKEN`
- `AQH_WEB_JOBS_DIR`
- `AQH_WEB_MAX_UPLOAD_MB`
- `AQH_WEB_JOB_TTL_HOURS`
- `AQH_WEB_MAX_ACTIVE_JOBS`
- `AQH_BETA_PASSWORD_HASH` preferred, or `AQH_BETA_PASSWORD` for a temporary private beta only

Before any official launch, replace shared password access with Cloudflare Access OTP or an equivalent stronger access-control layer.

## Rollout Documents

- `server-rollout.md`: practical home-server rollout steps
- `checklists/preflight.md`: release, server, env, and tunnel preflight
- `checklists/post-deploy.md`: local, remote, log, cleanup, and privacy checks
- `smoke-test.md`: manual and scripted smoke-test instructions
- `rollback.md`: manual rollback steps
- `scripts/private-beta-smoke.sh`: optional local smoke-test helper

## Deferred

- Cloudflare Access OTP until official launch
- public launch
- official product positioning
- DatenpflegeNord dashboard integration
- database
- user accounts
- external object storage
- worker queue
- autoscaling
- `humanize`
- audio algorithm changes
