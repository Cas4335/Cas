# Skill: bootstrap-stack

Bootstrap a fresh PHX deployment from scratch.

## Steps

1. Verify `.env` exists and has required values:
   ```bash
   grep -E "^POSTGRES_PASSWORD|^JWT_SECRET_KEY" .env
   ```

2. Create customer data directories:
   ```bash
   mkdir -p /mnt/customer-shares/{shared,operations,hr,management}
   ```

3. Build images:
   ```bash
   docker compose -f docker/compose.yaml build
   ```

4. Start infrastructure:
   ```bash
   docker compose -f docker/compose.yaml up -d phx-postgres phx-qdrant phx-ollama
   ```

5. Wait for Ollama to pull models (may take several minutes on first run):
   ```bash
   docker compose -f docker/compose.yaml logs phx-ollama -f
   ```

6. Run migrations:
   ```bash
   docker compose -f docker/compose.yaml run --rm phx-api alembic upgrade head
   ```

7. Seed demo users:
   ```bash
   docker compose -f docker/compose.yaml run --rm phx-api python -m app.scripts.seed
   ```

8. Start all services:
   ```bash
   docker compose -f docker/compose.yaml up -d
   ```

9. Run healthcheck:
   ```bash
   bash scripts/healthcheck.sh
   ```

10. Trigger first ingest:
    ```bash
    docker compose -f docker/compose.yaml exec phx-ingest python -m app.main --once
    ```

## Common Issues

- If `phx-api` fails to start: check `POSTGRES_PASSWORD` and `JWT_SECRET_KEY` in `.env`
- If Ollama is slow: model pull happens on first boot, wait 5–10 minutes
- If ingest finds no files: verify `/mnt/customer-shares/` has files and mounts are correct
