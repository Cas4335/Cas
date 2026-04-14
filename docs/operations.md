# Operations Guide

Day-to-day operations for PHX administrators.

---

## Starting and Stopping

```bash
# Start all services
docker compose -f docker/compose.yaml up -d

# Stop all services (data preserved)
docker compose -f docker/compose.yaml stop

# Restart a single service
docker compose -f docker/compose.yaml restart phx-api

# View all service status
docker compose -f docker/compose.yaml ps
```

---

## Checking Health

```bash
bash scripts/healthcheck.sh
```

This checks:
- All Docker containers are running
- API health endpoint responds
- UI is serving
- Qdrant is healthy
- Ollama is responding

---

## Viewing Logs

```bash
# All services
docker compose -f docker/compose.yaml logs -f

# Specific service
docker compose -f docker/compose.yaml logs phx-api -f
docker compose -f docker/compose.yaml logs phx-ingest -f

# Last 100 lines
docker compose -f docker/compose.yaml logs phx-api --tail=100
```

---

## Triggering a Manual Sync

To immediately re-index all sources (runs once and exits):
```bash
docker compose -f docker/compose.yaml exec phx-ingest python -m app.main --once
```

To check the last sync result (via API):
```bash
curl -H "Authorization: Bearer <admin-token>" http://localhost:8000/sync/shared-docs
```

---

## Viewing Audit Logs

Via the API (admin token required):
```bash
curl -H "Authorization: Bearer <admin-token>" \
  "http://localhost:8000/admin/audit-logs?limit=50"
```

Via Postgres directly:
```bash
docker compose -f docker/compose.yaml exec phx-postgres \
  psql -U phx phx -c "SELECT created_at, u.email, query_text, answer_grounded FROM audit_logs a JOIN users u ON a.user_id = u.id ORDER BY created_at DESC LIMIT 20;"
```

---

## Adding a New User

Currently via the seed script or direct Postgres insert. (User management
API is on the v1.1 roadmap.)

Via Postgres:
```bash
docker compose -f docker/compose.yaml exec phx-postgres psql -U phx phx
```
```sql
-- First hash a password with Python:
-- python3 -c "from passlib.context import CryptContext; c = CryptContext(schemes=['bcrypt']); print(c.hash('newpassword123'))"

INSERT INTO users (email, display_name, hashed_password, is_active, created_at, updated_at)
VALUES ('newuser@company.com', 'New User', '<bcrypt-hash>', true, NOW(), NOW());

-- Assign a role (find role_id from roles table)
SELECT id, name FROM roles;
INSERT INTO user_roles (user_id, role_id) VALUES (<user_id>, <role_id>);
```

---

## Changing User Passwords

```bash
# Generate new hash
docker compose -f docker/compose.yaml exec phx-api \
  python3 -c "from app.core.security import hash_password; print(hash_password('newpassword'))"

# Update in database
docker compose -f docker/compose.yaml exec phx-postgres psql -U phx phx -c \
  "UPDATE users SET hashed_password='<hash>' WHERE email='user@company.com';"
```

---

## Adding a New Document Folder

1. Create the folder and add files:
   ```bash
   mkdir -p /mnt/customer-shares/newdept
   cp /path/to/files/* /mnt/customer-shares/newdept/
   ```

2. Add bind mount to `docker/compose.yaml`:
   ```yaml
   # Under phx-ingest volumes:
   - /mnt/customer-shares/newdept:/customer_data/newdept:ro
   ```

3. Add source to `config/customer-template/sources.yaml`:
   ```yaml
   - id: "newdept-docs"
     type: filesystem
     enabled: true
     path: /customer_data/newdept
     department: newdept
     access_tags: [operations, admin]  # who can see these
     doc_type: document
     include_patterns: ["**/*.pdf", "**/*.txt"]
   ```

4. Restart ingest:
   ```bash
   docker compose -f docker/compose.yaml up -d --no-deps phx-ingest
   docker compose -f docker/compose.yaml exec phx-ingest python -m app.main --once
   ```

---

## Common Troubleshooting

### Ingest not picking up new files

- Check the file extension is supported (`.txt`, `.md`, `.pdf`, `.docx`, `.csv`, `.xlsx`)
- Check it's not in an excluded pattern
- Verify the bind mount path is correct: `docker compose exec phx-ingest ls /customer_data/shared`
- Check logs: `docker compose logs phx-ingest`

### Model not responding

```bash
docker compose logs phx-ollama | tail -50
# Check if models were pulled:
curl http://localhost:11434/api/tags
```

If models are missing:
```bash
docker compose exec phx-ollama ollama pull llama3.2
docker compose exec phx-ollama ollama pull nomic-embed-text
```

### Qdrant collection empty

```bash
curl http://localhost:6333/collections/phx_chunks
# If collection doesn't exist, restart phx-api (it creates on startup)
# Then run ingest
```

### Auth failures (401)

- Check JWT_SECRET_KEY is set in `.env`
- Token may be expired (default 8h) — log in again
- User may be inactive: check `is_active` in users table

### UI can't reach API

- Verify `VITE_API_URL` in `.env` points to the correct API address
- Check nginx proxy config in `services/ui/nginx.conf`
- Test API directly: `curl http://localhost:8000/health`

---

## Claude Code Hooks (Recommended)

To configure Claude Code to automatically lint after edits and run tests before
release, create `.claude/settings.json` in the project root:

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "cd services/api && python -m black app/ --check --quiet 2>/dev/null || echo '[PHX] Formatting check: run black to fix'"
          }
        ]
      }
    ],
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "echo '[PHX] Running bash command — check for outbound URLs or write operations'"
          }
        ]
      }
    ]
  }
}
```

For release validation, add to your release workflow:
```bash
# Validate compose files before building
docker compose -f docker/compose.yaml config > /dev/null && echo "Compose valid"

# Run tests
cd services/api && python -m pytest tests/ -v
cd services/ingest && python -m pytest tests/ -v
```

> **Note:** The `.claude/settings.json` hooks file is for local Claude Code sessions.
> It is not applied globally and does not affect CI/CD. Each developer or session
> can configure it independently.

---

## Disk Space Management

Check volume sizes:
```bash
docker system df -v
```

Qdrant storage can grow with many documents. Monitor with:
```bash
curl http://localhost:6333/collections/phx_chunks | python3 -m json.tool
```

Old sync job records can be pruned:
```sql
DELETE FROM sync_items WHERE indexed_at < NOW() - INTERVAL '90 days';
DELETE FROM sync_jobs WHERE created_at < NOW() - INTERVAL '90 days' AND status = 'completed';
```
