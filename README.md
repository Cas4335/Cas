# PHX — Offline AI Knowledge Appliance (v1)

An on-prem AI retrieval system for small and mid-sized companies.
Runs fully offline. No cloud dependencies at runtime.

---

## What It Does

PHX lets your team ask questions and get answers grounded in your company's
approved documents and database records — with source citations, access controls,
and a complete audit trail.

It does **not** write to your systems. It does **not** call the internet.
It does **not** give the AI free rein over your infrastructure.

---

## Services

| Service | Purpose |
|---|---|
| `phx-ui` | Internal web chat UI |
| `phx-api` | FastAPI backend, auth, retrieval, RAG |
| `phx-ingest` | Document and database ingestion worker |
| `phx-ollama` | Local AI model server (LLM + embeddings) |
| `phx-qdrant` | Vector database |
| `phx-postgres` | Application metadata (users, roles, audit logs) |

---

## Quick Start (Development)

```bash
# 1. Copy and fill in your environment
cp .env.example .env
# Edit .env with your settings

# 2. Start the stack
docker compose -f docker/compose.yaml up -d

# 3. Run database migrations
docker compose -f docker/compose.yaml exec phx-api alembic upgrade head

# 4. Seed demo data
docker compose -f docker/compose.yaml exec phx-api python -m app.scripts.seed

# 5. Trigger first ingest
docker compose -f docker/compose.yaml exec phx-ingest python -m app.main --once

# 6. Open the UI
# http://localhost:3000
```

---

## Default Demo Credentials

| Username | Password | Role |
|---|---|---|
| admin@example.com | changeme123 | admin |
| ops@example.com | changeme123 | operations |
| hr@example.com | changeme123 | hr |
| mgmt@example.com | changeme123 | management |

**Change all passwords before connecting real data.**

---

## Documentation

- [Architecture](docs/architecture.md)
- [Deployment Guide](docs/deployment.md)
- [Operations Guide](docs/operations.md)
- [Security Model](docs/security.md)
- [Customer Onboarding](docs/customer-onboarding.md)

---

## Project Structure

```
docker/          Docker Compose files
config/          Customer configuration templates
scripts/         install, update, healthcheck, release scripts
services/api/    FastAPI backend
services/ingest/ Ingestion worker
services/ui/     React web UI
services/trainer/ Optional trainer scaffold (disabled by default)
tests/           Unit, integration, e2e tests
docs/            All documentation
.claude/         Claude Code session instructions and skills
```

---

## License

Internal use only. Not for public distribution.
