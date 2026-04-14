# PHX Security Architecture

This document describes the security design of the PHX offline AI knowledge appliance — how it authenticates users, enforces access control, keeps source data read-only, operates without internet connectivity, manages secrets, and logs every interaction for audit purposes. It also covers known limitations in the current v1 release and a roadmap for future hardening.

---

## 1. Security Design Principles

PHX is built around three foundational security principles that inform every architectural decision:

### Offline-First

PHX is designed to run entirely within your private network or on an air-gapped server. At runtime the application makes no outbound connections to the internet. There are no calls to external APIs, no telemetry beacons, no license check-ins, no cloud-hosted model endpoints. The language model weights live on disk inside the container image. All embedding and inference happens locally. This means that sensitive documents you ingest into PHX — financial records, HR files, operational procedures — never leave your infrastructure.

### Read-Only Sources

PHX never writes to your source data. File shares are mounted into the ingest container with the `:ro` (read-only) flag, which is enforced at the container runtime level; even if the ingest process were compromised, the kernel would reject any write attempt. Database sources are accessed with read-only credentials that have `SELECT` permission only and no `INSERT`, `UPDATE`, `DELETE`, or `DDL` rights. This means PHX cannot corrupt, modify, or exfiltrate your source systems even in the event of a software bug or adversarial prompt.

### Auth-Before-Retrieval

No document chunk is ever retrieved from the vector store until the requesting user has been fully authenticated and their access tags have been resolved. The authorization check happens in the API layer before any query reaches Qdrant. The model receives only the chunks that the user is permitted to see; it never touches restricted content and then "decides" whether to reveal it. This is a structural guarantee, not a policy one.

---

## 2. Authentication

### User Store

PHX maintains a local user registry in the PostgreSQL database (the `phx` schema, `users` table). There is no dependency on an external identity provider in v1. Each user record contains:

- `id` — UUID primary key
- `username` — unique, case-insensitive
- `email` — unique
- `password_hash` — bcrypt digest (see below)
- `role` — one of `admin`, `management`, `operations`, `hr`, `shared_user`
- `is_active` — boolean; inactive users cannot authenticate
- `created_at`, `updated_at` — timestamps

### Password Hashing

Passwords are hashed with **bcrypt** at a work factor of 12 (configurable via `BCRYPT_ROUNDS` environment variable). bcrypt was chosen because:

- It is adaptive: the work factor can be increased as hardware improves.
- It incorporates a random salt automatically, so identical passwords produce different hashes.
- It is deliberately slow, making offline brute-force attacks computationally expensive.

PHX never stores plaintext passwords. The bcrypt hash is the only password-related value written to the database.

### JWT Tokens

On successful login (`POST /auth/login`), the API issues a signed **JSON Web Token (JWT)**. Token properties:

| Field | Value |
|---|---|
| Algorithm | HS256 (HMAC-SHA256) |
| Issuer (`iss`) | `phx-api` |
| Subject (`sub`) | User UUID |
| Expiry (`exp`) | 8 hours from issuance |
| Custom claim: `role` | User's role string |
| Custom claim: `access_tags` | Array of tag strings resolved at login time |

The signing secret is read from the `JWT_SECRET` environment variable (see Section 6). Tokens are stateless — the API validates the signature and expiry on every request without a database round-trip.

**Token expiry:** 8-hour sessions are a deliberate balance between usability (a working day without forced re-login) and security (limiting the window of exposure if a token is intercepted). Tokens cannot be extended; users must re-authenticate after expiry.

**Token revocation:** v1 does not implement a token blocklist. If a user's account is deactivated mid-session, their existing token will continue to work until it expires. This is a known limitation (see Section 9). The recommended mitigation is to set `is_active = false` in the database and then wait up to 8 hours, or to restart the API service (which causes all in-memory state to reset — note: since tokens are stateless this does not revoke them either). The proper fix is a Redis-backed blocklist, planned for v2.

---

## 3. Authorization Flow

The authorization model is designed so that access control is enforced structurally — by filtering what data reaches the model — rather than by trusting the model to behave correctly.

### Step 1 — Role Assignment

Each user is assigned exactly one role at account creation. Roles map to sets of access tags:

| Role | Access Tags |
|---|---|
| `admin` | `admin`, `management`, `operations`, `hr`, `shared` |
| `management` | `management`, `shared` |
| `operations` | `operations`, `shared` |
| `hr` | `hr`, `shared` |
| `shared_user` | `shared` |

These mappings are defined in `config/roles.yaml` and loaded at startup.

### Step 2 — Tag Resolution at Login

When a user authenticates, the API resolves their role to an `access_tags` list and embeds it in their JWT. The tags travel with the token; no database query is needed on subsequent requests.

### Step 3 — Query Arrives

When a user submits a question to `POST /query`, the API middleware:

1. Validates the JWT signature and expiry. If invalid or expired, returns HTTP 401.
2. Extracts `user_id`, `role`, and `access_tags` from the token claims.
3. Passes the resolved `access_tags` to the retrieval layer.

### Step 4 — Qdrant Metadata Filter

Every document chunk stored in Qdrant carries a `access_tag` metadata field set at ingest time. When the retrieval layer queries Qdrant, it constructs a **mandatory filter** of the form:

```json
{
  "filter": {
    "must": [
      {
        "key": "access_tag",
        "match": {
          "any": ["operations", "shared"]
        }
      }
    ]
  }
}
```

This filter is built by the API from the user's token claims and is **never supplied by the user**. A user cannot inject a different filter through their query text. Qdrant evaluates the filter before scoring relevance — it is not possible for a chunk to be retrieved and then "filtered out afterwards" by the application. Only chunks whose `access_tag` is in the user's allowed list are candidates for retrieval.

### Step 5 — Model Receives Filtered Context

The language model receives only the chunks that passed the Qdrant filter. From the model's perspective, the restricted content simply does not exist. There is no scenario in which the model "sees" a restricted chunk and decides not to mention it.

### Why the Model Never Makes Access Decisions

This point is important enough to address directly.

Large language models are not reliable policy enforcement components. They can be manipulated through prompt injection — adversarial text hidden in a document or crafted into a question can instruct the model to ignore previous instructions, reveal information it was told to keep secret, or bypass stated restrictions. Models can also hallucinate, misinterpret instructions, or behave inconsistently across versions or configurations.

PHX's architecture is designed so that **the model has no access decision to make**. By the time a question reaches the model, the retrieval step has already filtered the context to only what that user is permitted to see. If a user is not authorized to see HR documents, no HR document chunks will appear in the context window. The model cannot reveal what it has never been given.

This is the same principle as "need to know" in traditional information security: the safest way to prevent disclosure is to never put the information in front of the entity that might disclose it, rather than hoping that entity will exercise discretion correctly every time.

Relying on a system prompt instruction such as "do not reveal documents tagged HR to non-HR users" would be fundamentally insecure and is explicitly not how PHX works.

---

## 4. Source Read-Only Guarantees

### File Mounts

File shares are mounted into the ingest container using Docker's read-only volume flag:

```yaml
# docker-compose.yml (ingest service)
volumes:
  - /your/file/share:/data/sources:ro
```

The `:ro` flag causes the Linux kernel to mount the filesystem in read-only mode at the VFS layer. Any write system call (open with O_WRONLY, write, unlink, mkdir, rename, etc.) issued by any process inside the container — regardless of whether it runs as root — will receive `EROFS` (Read-only file system). This is a kernel-enforced guarantee, not an application-level one.

### Database Credentials

Database sources are connected using a dedicated read-only service account. The credentials used by PHX have only the following privileges:

- `CONNECT` on the target database
- `USAGE` on the relevant schemas
- `SELECT` on the specific tables or views configured in `sources.yaml`

The account does not have `INSERT`, `UPDATE`, `DELETE`, `TRUNCATE`, `DROP`, `CREATE`, or any other write or DDL permission. Even if an attacker gained control of the ingest process and attempted to modify source data through the database connection, the database server would reject the operation with a permission error.

---

## 5. No Outbound Internet at Runtime

PHX is intended to run in environments where outbound internet access is either unavailable (air-gapped networks) or forbidden by policy. The application is designed to require no runtime internet access. Specifically:

- The language model is loaded from local model weights stored in a named Docker volume, populated during initial setup.
- The embedding model is likewise local.
- There are no API calls to Anthropic, OpenAI, Hugging Face, or any other external service.
- There is no update check, telemetry, or analytics beacon.
- DNS resolution for internal hostnames (between containers) is handled by Docker's internal DNS; no external DNS is required.

**Recommended network configuration:** Deploy PHX on a network segment with no default route to the internet, or use firewall rules to block all outbound traffic from the PHX host. The application will function correctly with no outbound connectivity.

---

## 6. Secret Management

### Environment Variables

All secrets are supplied to the application via environment variables, which are set in the `.env` file at the project root. The `.env` file is listed in `.gitignore` and must never be committed to version control. A `.env.example` file is provided with placeholder values as a reference.

The following secrets must be set before first run:

| Variable | Purpose |
|---|---|
| `JWT_SECRET` | HMAC-SHA256 signing key for JWT tokens. Must be at least 32 characters of random data. |
| `POSTGRES_PASSWORD` | Password for the PHX database superuser (used during setup only). |
| `POSTGRES_APP_PASSWORD` | Password for the application read/write database user. |
| `POSTGRES_READONLY_PASSWORD` | Password for the read-only source database user (if applicable). |
| `QDRANT_API_KEY` | API key for Qdrant (if running Qdrant with authentication enabled). |

### Generating Secrets

Generate strong random values for secrets using:

```bash
openssl rand -hex 32
```

or

```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

### Never Hardcode Secrets

Secrets must never appear in:

- Source code files
- Docker image layers (do not use `ENV` in Dockerfile for secrets)
- `docker-compose.yml` (reference variables from `.env` instead)
- Log files
- API responses
- Documentation or comments

If a secret is accidentally committed to git, it should be treated as compromised and rotated immediately. The git history should be cleaned using `git filter-branch` or BFG Repo-Cleaner, and all places the secret was used must be audited.

---

## 7. Audit Logging

Every query submitted to PHX is logged for audit purposes. The audit log is designed to allow a security officer or administrator to answer: "Who asked what, when, and what information did they receive?"

### What Is Logged

For every call to `POST /query`, the following is written to the `audit_log` table in PostgreSQL:

| Field | Description |
|---|---|
| `id` | UUID, auto-generated |
| `user_id` | UUID of the authenticated user |
| `username` | Username at time of query (denormalized for readability) |
| `role` | User's role at time of query |
| `timestamp` | UTC timestamp of the request |
| `query_text` | The exact text of the user's question |
| `retrieved_chunk_ids` | Array of Qdrant point IDs returned by the retrieval step |
| `answer_summary` | First 500 characters of the generated answer (configurable) |
| `response_time_ms` | Total latency from request receipt to response sent |

Logging of `query_text` means that the audit log itself may contain sensitive information (users may paste document contents into their questions). The audit log table should be accessible only to administrators.

### Viewing Audit Logs

Audit logs can be queried via the admin API:

```
GET /admin/audit?user_id=<uuid>&from=<ISO8601>&to=<ISO8601>&limit=100
```

Or directly in PostgreSQL:

```sql
SELECT timestamp, username, role, query_text, array_length(retrieved_chunk_ids, 1) AS chunks_used
FROM phx.audit_log
ORDER BY timestamp DESC
LIMIT 50;
```

The admin UI (available at `/admin` when logged in as an `admin` role user) provides a searchable table view of audit logs with filtering by user, date range, and keyword.

### Log Retention

By default, audit logs are retained indefinitely. Administrators should establish a retention policy appropriate to their compliance requirements and periodically archive or purge old records. A helper script is provided at `scripts/archive_audit_logs.sh`.

---

## 8. Incident Response Basics

### Suspected Unauthorized Access

1. Identify the affected user account from audit logs.
2. Disable the account immediately: `UPDATE phx.users SET is_active = false WHERE username = '<username>';`
3. Review audit logs for the account: all queries, timestamps, and retrieved chunk IDs.
4. Note that existing JWT tokens remain valid until expiry (up to 8 hours). If immediate revocation is required, restart the API service to clear in-memory sessions (tokens are stateless but this clears any session-adjacent state).
5. Rotate `JWT_SECRET` and restart all services to invalidate all currently issued tokens system-wide.
6. Preserve audit log records for the investigation period before any archival or deletion.

### Suspected Prompt Injection

If a user reports unexpected behaviour from the model — for example, the model appearing to ignore instructions or revealing information inconsistently — retrieve the query from the audit log and inspect the `query_text` and `retrieved_chunk_ids`. Check whether any of the retrieved chunks contain injected instructions. Remove the offending document from the source folder; it will be purged from the index on the next sync or by running `scripts/purge_document.sh <doc_id>`.

### Credential Compromise

If a database credential, JWT secret, or API key is suspected to be compromised:

1. Generate a new secret value.
2. Update the `.env` file.
3. Restart all affected services (`docker compose restart api ingest`).
4. Audit recent access using the affected credential.

### Data Breach Assessment

Because PHX operates entirely on-premises and makes no outbound connections, a "data breach" in the PHX context most likely means either unauthorized internal access (covered above) or compromise of the host machine itself. If the host is compromised, treat all secrets as compromised and rotate them. The vector store (Qdrant) contains embeddings derived from your documents but not the original document text — however, embeddings can in some cases be used to reconstruct approximate source text, so they should also be considered sensitive.

---

## 9. v1 Security Limitations and Recommended Future Hardening

The following are known limitations of the current v1 release. They do not represent vulnerabilities in the design, but they are areas where the security posture can be improved in future versions.

### No Token Revocation / Blocklist

**Limitation:** JWT tokens cannot be invalidated before they expire. A deactivated user retains access for up to 8 hours.

**Recommendation:** Implement a Redis-backed token blocklist. On logout or account deactivation, add the token JTI (unique identifier) to the blocklist. The API checks the blocklist on every request.

### No SSO / LDAP Integration

**Limitation:** PHX maintains its own user database. There is no integration with Active Directory, LDAP, SAML, or OIDC. User accounts must be managed separately from your corporate directory.

**Recommendation:** Add an OIDC/SAML authentication provider in v2. This allows users to log in with corporate credentials, eliminates the need to manage a separate password database, and enables centralized account deactivation.

### No Per-Document ACLs

**Limitation:** Access control is at the "tag" level. You cannot grant a specific user access to a single document without granting them access to all documents with that tag.

**Recommendation:** Implement per-document ACLs stored in PostgreSQL and referenced in Qdrant metadata. This enables fine-grained access control, for example: "only the CFO and their direct reports can see the Q3 acquisition analysis document."

### No TLS Internally

**Limitation:** Communication between containers (API ↔ Qdrant, API ↔ PostgreSQL) is unencrypted within the Docker network. If the Docker host is shared or the Docker network is exposed, traffic could be intercepted.

**Recommendation:** Enable TLS on Qdrant and PostgreSQL, and configure the API to connect using TLS. For the external-facing API endpoint, place a TLS-terminating reverse proxy (nginx, Traefik, Caddy) in front of the API container.

### No Network Segmentation Between Services

**Limitation:** All PHX containers share a single Docker network. A compromised container could reach any other service.

**Recommendation:** Define separate Docker networks for the API-frontend, API-backend, and storage layers. Use explicit `networks` declarations in `docker-compose.yml` to restrict which containers can communicate with which.

### No Rate Limiting or Brute-Force Protection

**Limitation:** The `/auth/login` endpoint has no rate limiting. An attacker with network access to the API can attempt unlimited password guesses.

**Recommendation:** Add rate limiting middleware (e.g., slowapi for FastAPI) to the login endpoint. After N failed attempts from the same IP or for the same username, impose an exponential backoff delay or temporary lockout.

### No MFA

**Limitation:** Authentication relies solely on username and password. There is no second factor.

**Recommendation:** Add TOTP-based MFA (e.g., compatible with Google Authenticator or Authy) as an optional or required second factor, configurable per role.

### Audit Log Integrity

**Limitation:** Audit logs are stored in the same PostgreSQL database that the application writes to. An admin-level user could modify or delete audit records.

**Recommendation:** Stream audit logs to an append-only log store (e.g., a WORM-compliant object storage bucket, or a separate PostgreSQL instance with row-level security preventing deletes) to preserve log integrity for compliance purposes.

---

*This document reflects the PHX v1 security architecture. Review and update it whenever security-relevant changes are made to the system.*
