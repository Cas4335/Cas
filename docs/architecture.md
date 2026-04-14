# PHX — System Architecture

## Product Summary

PHX is an offline, on-premises AI knowledge appliance for small and mid-sized companies.
It gives your team a chat interface where they can ask questions and receive answers
grounded in your company's own documents and database records, with source citations
and role-based access controls.

Key properties:

- **Fully offline at runtime.** No queries, documents, embeddings, or answers leave
  the server. No cloud API is called. No telemetry is sent. The system functions
  identically whether or not the machine has internet access.
- **Read-only against your data.** PHX never writes to customer file systems or
  databases. All connectors operate with read-only credentials.
- **Deterministic access control.** What a user can see is decided by metadata
  filters applied before retrieval, not by the AI model. The model only ever sees
  chunks that already passed the filter.
- **Self-contained.** All dependencies — the language model, the embedding model,
  the vector database, the application database, the backend, and the UI — run as
  Docker containers on one server.

PHX is a v1 product. It is not SaaS, it does not support multi-region deployments,
and it does not include write-back, fine-tuning, or SSO in this release.

---

## Service Diagram

```
  Browser
     |
     | HTTP (port 3000)
     v
+----------+
|  phx-ui  |   React web chat interface
+----------+
     |
     | HTTP (port 8000)
     v
+-----------+          +-------------+
|  phx-api  |--------->| phx-qdrant  |  Vector DB (port 6333)
|           |          +-------------+
|  FastAPI  |
|           |--------->| phx-ollama  |  Local LLM + embeddings (port 11434)
|           |          +-------------+
|           |
|           |--------->| phx-postgres|  App metadata DB (port 5432)
+-----------+          +-------------+

+--------------+       +-------------+
| phx-ingest   |------>| phx-qdrant  |
|              |       +-------------+
| Ingest worker|
|              |------>| phx-ollama  |
|              |       +-------------+
|              |
|              |------>| phx-postgres|  (track ingest state)
+--------------+       +-------------+
        ^
        |
 [Customer data mounts]
 /customer_data/shared
 /customer_data/hr
 /customer_data/operations
 /customer_data/management
 (and/or external DB connections configured in sources.yaml)
```

Legend:
- `phx-ui` communicates only with `phx-api`.
- `phx-api` communicates with `phx-qdrant`, `phx-ollama`, and `phx-postgres`.
- `phx-ingest` communicates with `phx-qdrant`, `phx-ollama`, and `phx-postgres`.
- `phx-ingest` reads customer data via read-only bind mounts or read-only DB credentials.
- No service makes outbound calls to the internet.

---

## What Each Service Does

### phx-ui

The web chat interface. Built with React. Users log in, type questions, and receive
answers with citations. The UI holds no credentials after login except for the JWT
token in memory. It never calls any backend other than `phx-api`.

Port: **3000** (configurable via `UI_PORT`).

### phx-api

The core application backend. Built with FastAPI (Python). Responsible for:

- User authentication: validates credentials, issues JWT tokens.
- Authorization: loads the user's roles, derives the allowed access tags, and uses
  those tags as mandatory Qdrant filters on every retrieval call.
- Retrieval: embeds the user's query via Ollama, runs a filtered vector search in
  Qdrant, and scores results.
- Prompt assembly: builds the system prompt and context window from retrieved chunks.
- Answer generation: calls Ollama with the assembled prompt and streams the response.
- Audit logging: records every query, the chunk IDs retrieved, and the answer into
  Postgres.

Port: **8000** (configurable via `API_PORT`).

### phx-ingest

A background worker that keeps the vector database in sync with source documents and
database records. It is not a web server and accepts no inbound connections. Its job is:

- Read `sources.yaml` to discover configured sources.
- For filesystem sources: scan directories, detect new and changed files by comparing
  `content_hash` and `modified_at` against the state tracked in Postgres.
- For database sources: read allowlisted tables/views via read-only DB connections.
- Parse documents (PDF, DOCX, TXT, MD, CSV, XLSX) and extract text.
- Chunk text into overlapping segments.
- Embed each chunk using Ollama's embedding model.
- Upsert chunks and their metadata into Qdrant.
- Track ingest state (source ID, file path, hash, last processed timestamp) in Postgres
  so that only changed content is re-processed on subsequent runs.

Runs on a schedule (default: every 3600 seconds). Can also be triggered manually.

### phx-ollama

A local instance of [Ollama](https://ollama.com/), running entirely inside Docker.
Serves two functions:

- **Embedding model** (`nomic-embed-text` by default): converts text chunks and user
  queries into 768-dimensional vectors.
- **Language model** (`llama3.2` by default): generates answers from assembled prompts.

Both models are pulled into a named Docker volume at container startup. They never
leave the server. No model API keys are needed.

Port: **11434**.

### phx-qdrant

A local instance of [Qdrant](https://qdrant.tech/), the vector database. Stores
embedded chunks with their full metadata payloads. Serves filtered approximate
nearest-neighbor searches. Qdrant's payload filtering is the enforcement point for
access control: the API passes `access_tags` filters on every query so that only
chunks the user is permitted to see are ever returned.

Port: **6333**. A web dashboard is available at `http://localhost:6333/dashboard`
(restrict this in production).

### phx-postgres

A local PostgreSQL instance. Stores application metadata only — not customer document
content. Tables include:

- Users and hashed passwords
- Role assignments
- Ingest state (which files have been processed, their hashes, timestamps)
- Audit log (queries, retrieved chunk IDs, answers, timestamps, user IDs)

Port: **5432**.

---

## Data Flow: User Query

This describes what happens from the moment a user submits a question.

```
1. User submits login credentials
   └─> phx-api validates credentials against phx-postgres (bcrypt hash check)
   └─> phx-api issues a signed JWT (HS256, 8-hour expiry)
   └─> JWT returned to phx-ui and held in memory

2. User types a question
   └─> phx-ui sends POST /chat with question + JWT in Authorization header

3. phx-api receives the request
   └─> JWT signature verified; expiry checked
   └─> User ID extracted from token

4. Authorization: derive allowed tags
   └─> Load user's roles from phx-postgres
   └─> Look up roles in roles.yaml to get the union of allowed access_tags
       Example: user with role "operations" gets tags ["operations", "shared_user"]
   └─> Tags become mandatory filter — they cannot be changed by user input

5. Query embedding
   └─> phx-api sends the question text to phx-ollama (nomic-embed-text)
   └─> Receives a 768-dimensional vector

6. Filtered vector retrieval from phx-qdrant
   └─> phx-api sends: vector + filter (access_tags must overlap allowed_tags)
                     + top_k (default 8) + min_score threshold (default 0.30)
   └─> Qdrant returns up to top_k chunks whose metadata passed the filter

7. Prompt assembly
   └─> Retrieved chunks are formatted with their source titles and paths
   └─> Assembled into a context block (max 3000 tokens by default)
   └─> System prompt instructs the model to answer only from provided context
       (strict_mode: true) and to cite sources

8. Answer generation
   └─> phx-api sends assembled prompt to phx-ollama (llama3.2)
   └─> Ollama streams the response token by token
   └─> phx-api streams the response back to phx-ui

9. Citation attachment
   └─> phx-api appends source references (title, path, chunk_id) to the response

10. Audit log
    └─> phx-api writes query text, user ID, retrieved chunk IDs, and answer
        to phx-postgres audit table

11. User sees the answer with citations in phx-ui
```

The model never sees the JWT, user roles, or access tags. It receives only the
assembled prompt text. Access control is enforced before the model is involved.

---

## Data Flow: Document Ingestion

This describes what happens when phx-ingest processes a source.

```
1. phx-ingest starts (on schedule or manual trigger)
   └─> Reads sources.yaml to get the list of configured sources

2. For each enabled source:

   FILESYSTEM SOURCE:
   └─> Scan directory recursively using include/exclude patterns from sources.yaml
   └─> For each file:
       └─> Compute content_hash (SHA-256)
       └─> Check phx-postgres ingest state table:
           - If file is new (no record): process it
           - If hash differs from stored hash: re-process it
           - If hash matches: skip (already current)

   DATABASE SOURCE:
   └─> Connect to external DB using read-only credentials from sources.yaml / .env
   └─> Query each allowlisted table/view
   └─> Each row becomes a document; the title and body columns are configured
       in sources.yaml

3. Parse and extract text
   └─> PDF: extract page text
   └─> DOCX: extract paragraphs
   └─> TXT / MD: read as-is
   └─> CSV / XLSX: serialize rows to text
   └─> DB rows: concatenate body_columns into text

4. Chunk the text
   └─> Split into overlapping segments (default: 512 tokens, 64 token overlap)
   └─> Each chunk inherits metadata from its source

5. Embed each chunk
   └─> Send chunk text to phx-ollama (nomic-embed-text)
   └─> Receive 768-dimensional embedding vector

6. Upsert into phx-qdrant
   └─> Each chunk stored as a point with:
       - ID: deterministic chunk_id (hash of source_id + position)
       - Vector: the embedding
       - Payload: all required metadata fields (see below)

7. Update ingest state in phx-postgres
   └─> Record source_id, source_path, content_hash, modified_at, chunk count,
       and timestamp

8. Repeat on next schedule interval
```

---

## Required Metadata Fields on Every Chunk

Every chunk stored in Qdrant must carry all of the following payload fields.
These fields are what make access control and citations work correctly.
If a field is missing, the chunk will be rejected at upsert time.

| Field | Type | Description |
|---|---|---|
| `tenant_id` | string | Customer identifier. Isolates data between tenants in future multi-tenant deployments. |
| `source_id` | string | The `id` field from `sources.yaml` for the source this chunk came from. |
| `source_type` | string | `filesystem`, `postgres`, or `sqlserver`. |
| `source_path` | string | Full path to the file, or `<db>.<schema>.<table>/<record_id>` for DB records. |
| `title` | string | Human-readable document title (filename or row identifier). |
| `department` | string | Department this document belongs to, from sources.yaml. |
| `access_tags` | list of strings | Tags that control who can retrieve this chunk (e.g., `["hr", "admin"]`). |
| `doc_type` | string | Category of document: `policy`, `procedure`, `hr_policy`, `strategy`, `database_record`, etc. |
| `record_id` | string | Unique identifier within the source (file path hash or DB primary key). |
| `modified_at` | ISO 8601 datetime string | When the source document was last modified. |
| `content_hash` | string | SHA-256 hash of the raw document content. Used for change detection. |
| `chunk_id` | string | Unique ID for this specific chunk. Deterministic: hash of `source_id + source_path + chunk_index`. |

These fields serve multiple roles:
- `access_tags` is the access control enforcement field. The Qdrant filter always checks it.
- `tenant_id` partitions data between customers in future multi-tenant mode.
- `content_hash` and `modified_at` allow the ingest worker to skip unchanged documents.
- `source_path`, `title`, and `chunk_id` populate the citations shown to users.

---

## Authorization Model

PHX uses a tag-based authorization model applied at the vector database layer.

```
User
 └─> has one or more roles: admin | management | operations | hr | shared_user

roles.yaml maps each role to a set of allowed access_tags:
  admin       → [admin, management, operations, hr, shared_user]
  management  → [management, shared_user]
  operations  → [operations, shared_user]
  hr          → [hr, shared_user]
  shared_user → [shared_user]

If a user has multiple roles, their allowed tags are the UNION of all role tags.

Every chunk in Qdrant has an access_tags field, set at ingest time from sources.yaml.
Example:
  hr-docs source → access_tags: [hr, admin]

At retrieval time:
  allowed_tags = derived from user's roles (e.g., ["hr", "shared_user"])
  Qdrant filter = chunk.access_tags must overlap with allowed_tags
  (at least one tag in the chunk's list must appear in the user's allowed list)

The AI model only receives chunks that already passed this filter.
The model has no knowledge of roles, tags, or the filtering logic.
User input cannot modify the filter.
```

This design means access control decisions are made entirely by deterministic metadata
comparison, not by AI judgment. A prompt injection attack cannot cause the model to
reveal content the user is not tagged for, because that content is never passed to the
model in the first place.

---

## Named Volumes and Bind Mounts

PHX uses two kinds of persistent storage:

### Named Docker Volumes

Named volumes are managed by Docker. Their data lives on the host machine inside
Docker's storage area (typically `/var/lib/docker/volumes/`). You do not manage
the path directly.

| Volume | Used By | Contains |
|---|---|---|
| `phx-postgres-data` | phx-postgres | All application database data |
| `phx-qdrant-data` | phx-qdrant | All vector database data and indexes |
| `phx-ollama-data` | phx-ollama | Downloaded model weights |

Named volumes persist across container restarts and `docker compose down`. They are
only deleted if you explicitly run `docker compose down -v`.

To back up named volumes, use the service-specific backup procedures described in the
deployment guide (pg_dump for Postgres, Qdrant snapshot API for Qdrant).

### Bind Mounts

Bind mounts connect a specific directory on the host machine to a path inside a container.
PHX uses bind mounts for two purposes:

**Customer data (read-only):**
Host directories containing the customer's documents are mounted read-only into the
`phx-ingest` container. The ingest worker reads from them; it cannot write to them.
Example: `/srv/customer_data/hr` on the host → `/customer_data/hr` inside the container.

**Configuration files (read-only):**
`sources.yaml`, `roles.yaml`, and `app.yaml` are mounted from the host's config
directory into the API and ingest containers. This allows configuration changes without
rebuilding images.

Bind mount paths are defined in `docker/compose.yaml` and must match the actual
directory layout on the host server.

---

## Why Docker Compose (Not Kubernetes) for v1

PHX v1 is designed to run on a single Linux server. The choice of Docker Compose
over Kubernetes is intentional:

- **Target customer profile.** Small and mid-sized companies typically do not run
  Kubernetes clusters. They have a server, often managed by a single IT person or
  the founder.
- **Operational simplicity.** Docker Compose is a single file. Operators can read it,
  understand it, and modify it without specialized training. Kubernetes adds significant
  operational overhead: cluster management, RBAC, ingress controllers, persistent volume
  claims, and more.
- **Single-node workload.** All PHX services fit on one well-specced server. There is
  no need for pod scheduling, horizontal pod autoscaling, or cross-node networking.
- **Offline deployment.** Release bundles are distributed as Docker image tarballs
  loaded with `docker load`. This is straightforward with Compose and more involved
  with Kubernetes.
- **Easier debugging.** `docker compose logs phx-api -f` is more accessible to the
  target operator than `kubectl logs -n phx deployment/phx-api -f`.

Kubernetes migration can be addressed in a future version if customers require high
availability, multi-node scaling, or existing K8s infrastructure.

---

## Repository Structure

```
/
├── CLAUDE.md                    Root instructions for Claude Code sessions
├── .claude/
│   ├── CLAUDE.md                Extended session instructions
│   └── skills/                  Claude Code skill workflows (bootstrap, tests, etc.)
├── .env.example                 Environment variable template — copy to .env
├── docker/
│   ├── compose.yaml             Main production Docker Compose file
│   └── compose.train.yaml       Optional trainer scaffold (isolated, not part of v1 runtime)
├── config/
│   └── customer-template/
│       ├── app.yaml             RAG behavior, answer format, audit settings
│       ├── roles.yaml           Role → access_tags mapping
│       └── sources.yaml         Data source definitions (files and databases)
├── scripts/
│   ├── install.sh               First-time setup script
│   ├── update.sh                Pull new release and restart stack
│   ├── healthcheck.sh           Verify all services are responding
│   └── build-release.sh         Package a release bundle for offline delivery
├── services/
│   ├── api/                     FastAPI backend
│   │   ├── app/
│   │   │   ├── main.py          Application entry point
│   │   │   ├── auth/            JWT issuance and validation
│   │   │   ├── retrieval/       Embedding, Qdrant queries, access filter
│   │   │   ├── rag/             Prompt assembly and Ollama calls
│   │   │   ├── models/          SQLAlchemy ORM models
│   │   │   ├── schemas/         Pydantic request/response schemas
│   │   │   ├── scripts/         seed.py and other admin scripts
│   │   │   └── config/          Config loading (app.yaml, roles.yaml)
│   │   ├── alembic/             Database migration files
│   │   ├── tests/               API unit and integration tests
│   │   └── Dockerfile
│   ├── ingest/                  Ingestion worker
│   │   ├── app/
│   │   │   ├── main.py          Entry point (scheduler + manual trigger)
│   │   │   ├── connectors/      filesystem.py, postgres.py, sqlserver.py, base.py
│   │   │   ├── parsers/         PDF, DOCX, CSV, XLSX, TXT/MD parsers
│   │   │   ├── chunker/         Text splitting with overlap
│   │   │   ├── embedder/        Ollama embedding client
│   │   │   └── state/           Postgres-backed ingest state tracker
│   │   ├── tests/               Ingest unit tests
│   │   └── Dockerfile
│   ├── ui/                      React web UI
│   │   ├── src/
│   │   │   ├── App.tsx          Root component
│   │   │   ├── pages/           Login, Chat pages
│   │   │   └── components/      Message list, citation cards, etc.
│   │   └── Dockerfile
│   └── trainer/                 Optional trainer scaffold (disabled by default in v1)
├── tests/
│   ├── unit/                    Unit tests (run without Docker)
│   ├── integration/             Integration tests (require running stack)
│   └── e2e/                     End-to-end tests
└── docs/
    ├── architecture.md          This file
    ├── deployment.md            Practical deployment guide
    ├── operations.md            Day-to-day operations
    ├── security.md              Security model deep dive
    └── customer-onboarding.md  Guide for setting up a new customer
```
