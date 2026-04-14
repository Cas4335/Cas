# CLAUDE.md — Offline AI Knowledge Appliance (v1)

This file instructs all future Claude Code sessions working in this repository.
Read it fully before making any changes.

---

## Product Summary

This is an **offline, on-prem AI knowledge appliance** for small and mid-sized companies.
It runs entirely within a customer's infrastructure with **zero outbound internet dependencies at runtime**.

It is NOT SaaS. It is NOT a cloud product. It is NOT an agent with write access.

---

## Repository Structure

```
/
  CLAUDE.md                  ← this file (root instructions)
  .claude/CLAUDE.md          ← extended session instructions
  docker/
    compose.yaml             ← production compose
    compose.train.yaml       ← optional trainer scaffold (isolated)
  config/customer-template/  ← per-customer config templates
  scripts/                   ← install, update, healthcheck, release
  services/
    api/                     ← FastAPI backend
    ingest/                  ← ingestion worker
    ui/                      ← React frontend
    trainer/                 ← optional, not required for v1 runtime
  docs/                      ← all documentation
  tests/                     ← unit, integration, e2e
  .claude/skills/            ← Claude Code skill workflows
```

---

## Code Style

- Python: follow PEP 8, use `black` formatting, `isort` imports
- TypeScript/React: ESLint + Prettier, functional components, no class components
- All secrets via environment variables — never hardcoded
- Use explicit configuration over implicit magic
- Prefer flat, readable code over clever abstractions
- Keep functions small and single-purpose
- Add comments only where logic is non-obvious

---

## Architecture Boundaries

Each service has a strict domain:

| Service | Owns | Must NOT |
|---|---|---|
| `phx-api` | Auth, retrieval, prompt assembly, answer generation | Write to customer DBs, shell out, call cloud APIs |
| `phx-ingest` | Scanning, parsing, chunking, embedding, upsert | Accept inbound connections, write to customer systems |
| `phx-ui` | Login, chat, citations | Store credentials, call backends directly except phx-api |
| `phx-qdrant` | Vector storage | Nothing custom |
| `phx-ollama` | Local model inference and embeddings | Nothing custom |
| `phx-postgres` | Application metadata | Customer data storage |

---

## Security Constraints

**These rules are non-negotiable and must never be violated:**

1. **No outbound internet at runtime.** Never add `requests.get("https://...")` or any call to external APIs, model providers, telemetry endpoints, or update servers in runtime code.
2. **No write access to customer data sources.** Database connectors must be read-only. File mounts must be read-only.
3. **Authorization before retrieval.** The model never decides access control. Metadata filters are applied to Qdrant queries before any chunk reaches the model.
4. **No hardcoded secrets.** All credentials, keys, and salts come from environment variables or mounted secrets files.
5. **No arbitrary SQL from user input.** Database connectors use allowlisted tables/views only.
6. **JWT tokens must have expiry.** Default: 8 hours. Never use `exp=None`.
7. **Passwords must be hashed.** Use `bcrypt` via `passlib`. Never store plaintext.

---

## Authorization Model

- Users have one or more roles: `admin`, `management`, `operations`, `hr`, `shared_user`
- Each role maps to a set of `access_tags` (defined in `config/customer-template/roles.yaml`)
- Every chunk in Qdrant has an `access_tags` metadata field (list of strings)
- Before retrieval, the API derives `allowed_tags` from the user's roles
- Qdrant filter: chunk's `access_tags` must overlap with `allowed_tags`
- **The model only sees chunks that passed the filter**

Never bypass this filter. Never let user input modify the filter.

---

## Adding New Connectors

To add a new source type (e.g., MySQL):

1. Create `services/ingest/app/connectors/<name>.py`
2. Implement the `BaseConnector` interface (see `connectors/base.py`)
3. Add source type to `sources.yaml` schema validation
4. Add parser/extractor if needed
5. Write unit tests in `tests/unit/ingest/`
6. Update `docs/customer-onboarding.md` with the new source type
7. Do NOT add write operations. Do NOT store raw credentials in code.

---

## Test Expectations

- All new features must have unit tests
- Auth flows must have integration tests
- Every API route must have at least one test
- Run tests before any release build:
  ```bash
  cd services/api && python -m pytest tests/ -v
  cd services/ingest && python -m pytest tests/ -v
  ```
- Tests must pass before pushing to main

---

## Release Packaging Rules

- Use `scripts/build-release.sh` to produce a customer bundle
- Release bundles contain: exported Docker images, compose files, config templates, install script
- Never include `.env` files with real secrets in release bundles
- Always use `.env.example` with placeholder values
- Tag releases with semantic versioning: `v1.0.0`, `v1.1.0`, etc.

---

## What NOT to Build

- No Kubernetes manifests (v1 is Docker Compose only)
- No Active Directory or SSO integration
- No cloud API calls
- No write-back to customer systems
- No arbitrary SQL generation from chat
- No per-document ACL UI
- No training/fine-tuning in the default stack

---

## Implementation Log

See `docs/implementation-log.md` for the history of what was built and when.
