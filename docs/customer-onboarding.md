# Customer Onboarding Guide

This guide explains how to set up PHX for a new customer deployment.
It is written for non-expert users — you don't need to be a Docker expert.

---

## What Is PHX?

PHX is an internal AI assistant that can answer questions about your company's
documents and records.

Unlike a general AI chatbot:
- It **only answers from your approved documents** — not from the internet
- It **always shows its sources** (you can see which document it used)
- It **respects access rules** — HR staff only see HR documents, for example
- It **never writes to your systems** — it is read-only
- It **never calls the internet** — it runs entirely on your server

---

## What Is a Bind Mount?

A **bind mount** is a way of making a folder on your server visible inside a
Docker container.

Think of it like this: you have a folder `/mnt/customer-shares/hr` on your server.
When you set up a bind mount, PHX can read files from that folder.
But it's **read-only** — PHX cannot change, delete, or write any files.

```
Your server:                    PHX ingest container:
/mnt/customer-shares/hr   →    /customer_data/hr   (read-only)
```

---

## What Is a Named Volume?

A **named volume** is internal storage managed by Docker.
You don't need to create it — Docker creates it automatically.

PHX uses named volumes for:
- `phx_postgres_data` — user accounts, audit logs, sync history
- `phx_qdrant_storage` — the AI knowledge index (vectors)
- `phx_ollama_models` — the AI language models
- `phx_parsed_cache` — temporary parsing cache
- `phx_api_logs` — API logs

These survive container restarts and updates. To fully reset PHX, you would
delete these volumes (which destroys all indexed data).

---

## Connecting Company File Shares

### Step 1 — Decide which folders to connect

PHX uses four default departments. You can add more, but start with these:

| Department | Who can see it | Examples |
|---|---|---|
| shared | Everyone | Company handbook, general policies |
| operations | Operations team, management, admin | SOPs, runbooks, equipment lists |
| hr | HR team, admin | HR policies, job descriptions, benefits |
| management | Management, admin | Strategy docs, financial summaries |

### Step 2 — Put your files in the right place

Copy approved files to the corresponding folder on the server:

```bash
# Example: add the company handbook to shared
cp /path/to/company-handbook.pdf /mnt/customer-shares/shared/

# Add HR policies
cp /path/to/hr-policies/*.pdf /mnt/customer-shares/hr/
```

**Supported file formats:**
- `.pdf` — PDFs
- `.docx` — Word documents
- `.txt` — Plain text files
- `.md` — Markdown files
- `.csv` — CSV spreadsheets
- `.xlsx` — Excel spreadsheets

### Step 3 — Trigger indexing

After adding files, tell PHX to index them:

```bash
docker compose -f docker/compose.yaml exec phx-ingest python -m app.main --once
```

Watch the output — you should see each file being processed.

### Step 4 — Test it

Log in to PHX at `http://your-server:3000` and ask a question about a document
you just added. The answer should include a citation showing which document was used.

---

## Connecting a Company Database

PHX can also read from approved database tables using a **read-only account**.

**Requirements:**
- A read-only database user (PHX cannot and should not use admin credentials)
- A list of specific tables or views PHX is allowed to read

### Step 1 — Create a read-only database user

Ask your DBA to create a read-only user:

**Postgres:**
```sql
CREATE USER phx_readonly WITH PASSWORD 'choose-strong-password';
GRANT CONNECT ON DATABASE your_database TO phx_readonly;
GRANT USAGE ON SCHEMA public TO phx_readonly;
GRANT SELECT ON TABLE work_orders, equipment_log TO phx_readonly;
-- Only grant SELECT on specific tables!
```

**SQL Server:**
```sql
CREATE LOGIN phx_readonly WITH PASSWORD = 'choose-strong-password';
CREATE USER phx_readonly FOR LOGIN phx_readonly;
GRANT SELECT ON dbo.Products TO phx_readonly;
GRANT SELECT ON dbo.WorkOrders TO phx_readonly;
```

### Step 2 — Add to sources.yaml

Edit `config/customer-template/sources.yaml` and uncomment the database
section, filling in your credentials:

```yaml
- id: "ops-database"
  type: postgres
  enabled: true
  host: "your-db-server.company.local"
  port: 5432
  database: "your_database"
  user: "phx_readonly"
  password: "${EXT_PG_PASSWORD}"  # Set this in .env
  department: operations
  access_tags: [operations, management, admin]
  doc_type: database_record
  allowed_tables:
    - schema: public
      table: work_orders
      title_column: order_name
      body_columns: [description, status, notes]
```

### Step 3 — Set the credential in .env

Add the database password to your `.env` file:
```
EXT_PG_PASSWORD=the-readonly-password-you-created
```

### Step 4 — Restart and sync

```bash
docker compose -f docker/compose.yaml up -d --no-deps phx-ingest
docker compose -f docker/compose.yaml exec phx-ingest python -m app.main --once
```

---

## Creating User Accounts

### Roles

| Role | What they can see |
|---|---|
| `admin` | Everything — all departments, all documents |
| `management` | Management documents + shared documents |
| `operations` | Operations documents + shared documents |
| `hr` | HR documents + shared documents |
| `shared_user` | Shared documents only |

### Adding Users

PHX v1 manages users directly in the database.
Run the seed script to add the default demo users, then add real users via
the database:

```bash
docker compose -f docker/compose.yaml exec phx-postgres psql -U phx phx
```

```sql
-- Find the role ID for the role you want to assign
SELECT id, name FROM roles;

-- Add a new user (hash password first — see operations guide)
INSERT INTO users (email, display_name, hashed_password, is_active, created_at, updated_at)
VALUES ('alice@company.com', 'Alice Smith', '<bcrypt-hash>', true, NOW(), NOW());

-- Assign a role
INSERT INTO user_roles (user_id, role_id)
SELECT u.id, r.id FROM users u, roles r
WHERE u.email = 'alice@company.com' AND r.name = 'operations';
```

---

## What Happens During Ingestion?

When you trigger a sync, PHX:

1. **Scans** each configured source (folder or database)
2. **Reads** each file or row using read-only access
3. **Extracts text** from PDFs, Word docs, spreadsheets, etc.
4. **Splits** long documents into smaller chunks (default: ~512 characters each)
5. **Converts** each chunk into a vector (a list of numbers representing its meaning)
6. **Stores** each chunk in the vector database (Qdrant) with metadata tags
7. **Records** which files were processed and their content hashes
8. **Skips** unchanged files on subsequent syncs (faster re-indexing)

---

## Verifying a Document Was Indexed

### Via the sync status API

```bash
# Get the last sync for "shared-docs" source
curl -H "Authorization: Bearer <admin-token>" \
  http://localhost:8000/sync/shared-docs
```

### Via a test question

Log in as a user who has access to the document and ask a question about it.
If indexed correctly, the answer will include a citation from that document.

### Via Qdrant directly (advanced)

```bash
curl http://localhost:6333/collections/phx_chunks
```

This shows the total number of indexed chunks.

---

## What Users See

When a user asks a question:

1. They type their question in the chat box
2. PHX searches for relevant document chunks (only ones they're authorized to see)
3. PHX uses the AI model to synthesize an answer from those chunks
4. The answer appears with **citations** — each showing:
   - Document title
   - Source path
   - Department
   - How closely it matched (similarity score)
   - A short excerpt

If PHX doesn't find relevant documents, it says:
> "I don't have enough information in the approved documents to answer that question."

It will **not** guess or make things up.

---

## Removing a Document

To remove a document from the knowledge base:

1. Delete the file from the server folder:
   ```bash
   rm /mnt/customer-shares/hr/old-policy.pdf
   ```

2. On the next sync cycle, PHX will detect the file is gone.
   **Note:** In v1, existing vectors are not automatically deleted when a file
   is removed. To force a clean re-index of a source, contact your administrator.
   Full re-index support is planned for v1.1.

---

## Frequently Asked Questions

**Q: Can PHX see my password or personal messages?**
A: No. PHX only reads the files and database tables you explicitly configure.
It stores only document content and the questions users ask (for audit purposes).

**Q: Can PHX modify my database or files?**
A: No. All connections are strictly read-only. PHX cannot change, delete, or
insert anything into your systems.

**Q: What happens if I add a file and ask a question immediately?**
A: PHX won't know about the file until the next sync. Either wait for the
scheduled sync (default: every hour) or trigger a manual sync.

**Q: Does PHX call the internet?**
A: No. After installation, PHX runs entirely offline. The AI models run on
your server. No queries, documents, or answers leave your network.

**Q: Who can see the audit logs?**
A: Only users with the `admin` role can view audit logs. Logs record who asked
what and which documents were used.

**Q: Can a user see documents they're not authorized for?**
A: No. Authorization is enforced before any search happens. If a user's role
doesn't include the `hr` tag, they will never see HR documents — not in search
results, not in answers, not in citations.
