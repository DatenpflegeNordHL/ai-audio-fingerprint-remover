# v0.16 Deployment Readiness Checklist

## Status

Not deployed yet.

This checklist is documentation only. It does not add deployment, DNS, HTTPS, reverse proxy, Docker, provider, or public launch configuration.

## Local Boundary

- Keep the private beta bound to `127.0.0.1` for local use.
- Do not bind directly to `0.0.0.0` for public exposure before a future deployment milestone.
- Keep bearer-token auth for all `/api/*` endpoints.
- Keep `/health` minimal and unauthenticated.
- Keep uploads and generated outputs temporary and ignored by Git.

## Required Research Before Deployment

Before any deployment milestone, research and document current requirements for:

- HTTPS
- reverse proxy behavior
- upload body limits
- timeout limits
- temporary storage permissions
- log retention
- auth hardening
- rate limiting
- abuse prevention
- privacy and data deletion
- backup and restore scope; persistent backup is not needed for temporary jobs

## Deep Search Required For Actual Deployment

Actual deployment work requires Deep Search with these reasons:

- `needed_external_standards`
- `needed_current_library_behavior`
- `needed_security_or_safety_policy_check`

## Provider Scope

No specific provider choice is approved yet.

Do not add Cloudflare, Vercel, Hetzner, Nginx, Docker, DNS, TLS, or reverse-proxy configuration until a separate deployment milestone approves that scope.

## Safety Boundary

Deployment planning must not change the product boundary. Reports remain measured technical audio reports only and must not claim platform acceptance, distributor acceptance, or changes to watermark, fingerprint, provenance, detector, C2PA, source-attribution, evasion, or detectability behavior.
