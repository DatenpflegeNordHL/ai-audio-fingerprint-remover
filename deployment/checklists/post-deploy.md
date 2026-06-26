# Private Beta Post-Deploy Checklist

## Local Checks

- `curl http://127.0.0.1:8017/health` returns HTTP `200`
- dashboard without password returns HTTP `401`
- dashboard with beta password returns HTTP `200`
- `/api/config` without token returns HTTP `401`
- `/api/config` with token returns safe config
- oversized upload returns HTTP `413`
- active job limit can return HTTP `429` during controlled testing

## Remote Checks

- `https://beta.datenpflege-nord.de/health` returns minimal OK if intentionally public
- dashboard gate behavior matches local behavior
- API token behavior matches local behavior
- Cloudflare route points to `http://localhost:8017`

## Logs

- no token values
- no beta password values
- no raw uploaded file content
- no unnecessary original upload filenames

## Cleanup And Retention

- jobs/artifacts are temporary
- no upload/output backups
- TTL is initially `24` hours unless Dustin chose a different final value
- cleanup endpoint remains authenticated

## Privacy

- private side-project beta only
- not publicly advertised
- no public listing
- no analytics
- Cloudflare may process access metadata
- home server processes uploaded files temporarily
