# .claude/CLAUDE.md — Session Instructions

This file extends the root `CLAUDE.md` with session-specific workflow guidance.
Always read the root `CLAUDE.md` first.

---

## Before Making Any Change

1. Read the file you're about to change
2. Understand what service it belongs to (api / ingest / ui)
3. Check if there's an existing pattern (look at adjacent files)
4. Confirm the change doesn't violate any security constraint from root CLAUDE.md

---

## Service Entry Points

| Service | Main file | Tests |
|---|---|---|
| API | `services/api/app/main.py` | `services/api/tests/` |
| Ingest | `services/ingest/app/main.py` | `services/ingest/tests/` |
| UI | `services/ui/src/App.tsx` | (manual / browser) |

---

## Environment Variables

All runtime config lives in `.env` (gitignored). Use `.env.example` as the template.
For tests, use `.env.test` or pytest fixtures — never the production `.env`.

---

## Database Migrations

Migrations are managed by Alembic in `services/api/`.

To create a new migration:
```bash
cd services/api
alembic revision --autogenerate -m "description"
```

To run migrations:
```bash
alembic upgrade head
```

Never edit migration files after they've been applied to production.
Always add a new migration instead.

---

## Qdrant Collections

- Collection name: `phx_chunks` (configured via env `QDRANT_COLLECTION`)
- Vector dimension: 768 (nomic-embed-text default) or configured via `EMBEDDING_DIM`
- Payload fields must match the required metadata schema in root CLAUDE.md

---

## Ollama Models

- Default LLM: `llama3.2` (configurable via `OLLAMA_LLM_MODEL`)
- Default embedding model: `nomic-embed-text` (configurable via `OLLAMA_EMBED_MODEL`)
- Models are pulled at container startup via entrypoint script
- Never hardcode model names outside of environment variable defaults

---

## Common Workflows

Use the skills in `.claude/skills/` for common operations:

- `.claude/skills/bootstrap-stack/SKILL.md` — first-time setup
- `.claude/skills/run-tests/SKILL.md` — run all tests
- `.claude/skills/build-release/SKILL.md` — build customer bundle
- `.claude/skills/add-source/SKILL.md` — add a new source connector
- `.claude/skills/security-check/SKILL.md` — security audit checklist

---

## Debugging Tips

- API logs: `docker compose logs phx-api -f`
- Ingest logs: `docker compose logs phx-ingest -f`
- Qdrant UI: http://localhost:6333/dashboard (dev only)
- Postgres: `docker compose exec phx-postgres psql -U phx phx`

---

## Pull Request Checklist

Before opening a PR:
- [ ] Tests pass
- [ ] No hardcoded secrets
- [ ] No outbound API calls added
- [ ] Authorization filter is preserved
- [ ] `.env.example` updated if new env vars added
- [ ] Docs updated if behavior changed
