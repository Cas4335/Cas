# Implementation Log

This file tracks what was built and when, phase by phase.

---

## v1.0.0 — Initial Build

**Date:** 2024-04

### Phase 1 — Repository Scaffold

- Created root `CLAUDE.md` with architecture boundaries, security constraints, code style rules
- Created `.claude/CLAUDE.md` with session-specific workflow guidance
- Created `README.md` with quick start and service overview
- Created `.env.example` with all required environment variable documentation
- Created `.gitignore`
- Created `config/customer-template/sources.yaml` with filesystem and DB source examples
- Created `config/customer-template/roles.yaml` with role→tag mapping
- Created `config/customer-template/app.yaml` with RAG behavior configuration
- Created `.claude/skills/` with 5 workflow skills

### Phase 2 — Docker Compose and Service Skeletons

- Created `docker/compose.yaml` with all 6 services, named volumes, bind mounts,
  health checks, and restart policies
- Created `docker/compose.train.yaml` (isolated trainer scaffold, disabled by default)
- Created `services/api/Dockerfile` (non-root Python image)
- Created `services/ingest/Dockerfile` (includes PDF parsing system deps)
- Created `services/ui/Dockerfile` (multi-stage: Vite build → nginx)
- Created `services/ui/nginx.conf` with SPA routing and API proxy
- Created `services/trainer/Dockerfile` (scaffold only, not required for v1)

### Phase 3 — Postgres Models and Migrations

- Created SQLAlchemy models: `User`, `Role`, `Source`, `SyncJob`, `SyncItem`, `AuditLog`
- Created Alembic migration `001_initial_schema.py`
- Created seed script with 5 demo users (admin, ops, hr, management, shared_user)
- Every model includes timezone-aware timestamps

### Phase 4 — API Auth and Role Model

- `app/core/security.py`: bcrypt password hashing, JWT creation with expiry
- `app/core/roles.py`: role→access_tag mapping with YAML config loading
- `app/middleware/auth.py`: JWT bearer token validation FastAPI dependency
- `app/routers/auth.py`: login and /me endpoints
- Login uses timing-attack-resistant password check (runs verify even on unknown email)

### Phase 5 — Qdrant and Ollama Integration

- `app/core/qdrant_client.py`: async/sync clients, collection initialization with payload indexes
- `app/services/ollama.py`: async embed and generate functions
- `app/services/retrieval.py`: authorized Qdrant search with auth filter
- Collection indexes: `access_tags`, `tenant_id`, `source_id`, `department`

### Phase 6 — Filesystem Ingestion

- `ingest/app/connectors/base.py`: `BaseConnector` interface and `RawDocument` dataclass
- `ingest/app/connectors/filesystem.py`: recursive scan with include/exclude patterns
- `ingest/app/parsers/dispatcher.py`: parsers for txt, md, pdf, docx, csv, xlsx
- `ingest/app/chunker/text_chunker.py`: sliding window chunker with paragraph boundary awareness
- `ingest/app/embedder.py`: synchronous Ollama embedding client
- `ingest/app/state_tracker.py`: Postgres-backed hash tracking for incremental sync
- `ingest/app/pipeline.py`: full orchestration with batched Qdrant upserts
- `ingest/app/main.py`: CLI entry with `--once` flag and scheduled mode

### Phase 7 — Retrieval and Citations

- `app/services/rag.py`: prompt building, citation formatting, insufficiency detection
- `app/routers/chat.py`: full RAG pipeline with audit logging
- Strict mode: model instructed to answer only from context
- Citations include: chunk_id, source_id, source_path, title, department, score, excerpt
- Every chat request writes an `AuditLog` record

### Phase 8 — Database Connectors

- `ingest/app/connectors/postgres_connector.py`: read-only Postgres connector
  with `default_transaction_read_only=on`
- `ingest/app/connectors/sqlserver_connector.py`: read-only SQL Server connector
- Both use allowlisted tables only (no arbitrary SQL)

### Phase 9 — Web UI

- React + Vite + TypeScript SPA
- `LoginPage.tsx`: email/password form with error display
- `ChatPage.tsx`: chat interface with message history, loading state, citations panel
- `CitationCard.tsx`: expandable citation card with excerpt
- `useAuth.ts`: JWT auth hook with localStorage persistence and /me validation
- nginx serves built SPA and proxies `/api/` to phx-api

### Phase 10 — Tests

- `services/api/tests/test_auth.py`: password hashing, JWT, login/me endpoints
- `services/api/tests/test_roles.py`: role→tag mapping for all roles and edge cases
- `services/api/tests/test_rag.py`: prompt building, citations, insufficiency detection
- `services/ingest/tests/test_chunker.py`: chunking logic, determinism, edge cases
- `services/ingest/tests/test_filesystem.py`: filesystem connector, hash tracking
- `services/ingest/tests/test_parsers.py`: text and CSV parsers
- `tests/e2e/test_happy_path.py`: full stack E2E (requires running stack, opt-in with E2E=1)

### Phase 11 — Release Packaging

- `scripts/install.sh`: first-time deployment with prerequisite checks
- `scripts/update.sh`: rolling update preserving data
- `scripts/healthcheck.sh`: comprehensive health check with clear output
- `scripts/build-release.sh`: builds offline bundle with Docker image tarballs

### Phase 12 — Documentation

- `docs/architecture.md`: full system architecture, data flows, service descriptions
- `docs/deployment.md`: step-by-step deployment for non-expert technical founders
- `docs/security.md`: security model, auth flow, audit logging, hardening guidance
- `docs/operations.md`: day-to-day ops, troubleshooting, hooks configuration
- `docs/customer-onboarding.md`: plain-language guide for non-experts

---

## Known v1 Limitations (Planned for v1.1+)

- Removing a document does not automatically delete its vectors from Qdrant
- User management UI not yet implemented (currently via Postgres directly)
- No streaming LLM responses (uses non-streaming Ollama API)
- Single tenant per deployment (multi-tenant is out of scope for v1)
- No SSO or Active Directory integration
