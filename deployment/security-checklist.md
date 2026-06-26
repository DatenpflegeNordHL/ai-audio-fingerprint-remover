# Private Beta Security Checklist

## Local Service

- Uvicorn binds to `127.0.0.1`.
- Suggested local target is `http://localhost:8017`.
- No direct internet exposure for Uvicorn.
- No router port forwarding.
- Cloudflare Tunnel is the only public entry.

## Secrets

- Do not commit the real `AQH_WEB_TOKEN`.
- Do not commit the real beta password or beta password hash.
- Do not pass `AQH_WEB_TOKEN` through query parameters.
- Do not log token or beta password values.

## Uploads And Artifacts

- Enforce upload size inside the app.
- Reject oversized uploads with HTTP `413`.
- Keep artifact downloads restricted to artifacts listed in each job status.
- Do not back up temporary upload or artifact directories.
- Delete jobs and artifacts after the configured TTL.

## Public Surface

- `/health` stays minimal and non-sensitive.
- `/docs` and `/redoc` remain disabled.
- Do not cache upload endpoints.
- Do not cache artifact endpoints.
- Keep public launch, official product positioning, SEO, analytics, and dashboard integration out of scope.

## Before Official Launch

- Replace shared beta password access with Cloudflare Access OTP or equivalent stronger access control.
- Re-check upload limits, timeout limits, rate limiting, abuse prevention, auth hardening, log retention, and privacy deletion behavior.
