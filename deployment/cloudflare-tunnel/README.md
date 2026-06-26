# Cloudflare Tunnel Routing Notes

The Cloudflare Tunnel already exists. This project only documents the intended manual routing for the private beta.

## Public Hostname

`beta.datenpflege-nord.de`

## Local Service

`http://localhost:8017`

## Boundary

- Cloudflare Tunnel is the only public entry.
- Do not expose local ports publicly.
- Do not configure router port forwarding.
- Do not expose Uvicorn directly to the internet.
- Do not require local Certbot, Caddy, or Nginx by default.
- Keep `/api/*` protected by `AQH_WEB_TOKEN`.
- Keep the dashboard protected by the temporary beta password gate for the private beta.

## Caching

- Do not cache upload endpoints.
- Do not cache artifact endpoints.
- Keep Cloudflare upload limits at or below the configured app upload limit.

## Future Access Control

Cloudflare Access OTP or equivalent identity-based access remains deferred until an official launch milestone.
