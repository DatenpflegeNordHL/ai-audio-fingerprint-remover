# Private Beta Rollback

Rollback is manual and local to the home server.

## Trigger Conditions

- service does not start
- `/health` fails
- dashboard gate does not behave as expected
- API auth behaves unexpectedly
- upload limit or cleanup checks fail
- logs expose sensitive values

## Steps

1. Stop the active service.

   Docker Compose:

   ```bash
   docker compose down
   ```

   systemd alternative:

   ```bash
   systemctl stop audio-quality-humanizer-web
   ```

2. Check out the previous known-good tag or previous deployment directory. The `v0.17.0` command below is only an example rollback target; use the actual previous known-good tag for the server.

   ```bash
   git fetch --tags
   git checkout v0.17.0
   ```

3. Reuse the server-only environment file after confirming it contains no committed values.

4. Restart the chosen service method.

5. Verify local health.

   ```bash
   curl -i http://127.0.0.1:8017/health
   ```

6. Verify remote route.

   ```bash
   curl -i https://beta.datenpflege-nord.de/health
   ```

7. Review logs for token, beta password, uploaded content, and unexpected file path exposure.

## Data Handling

Temporary jobs and artifacts may be deleted during rollback. They are not a durable data store and should not be backed up.
