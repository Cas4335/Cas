# Deployment Guide

This guide walks you through deploying PHX on a Linux server.
It is written for a technical founder who is comfortable with a terminal
but not necessarily an expert in Docker.

---

## Prerequisites

**Server requirements:**
- Linux server (Ubuntu 22.04 or Rocky Linux 8+ recommended)
- 8 GB RAM minimum (16 GB recommended for comfortable LLM inference)
- 50 GB free disk space minimum (for models, vectors, and documents)
- Docker Engine 24.0+
- Docker Compose v2 (comes with Docker Desktop or can be installed separately)

**Install Docker on Ubuntu:**
```bash
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER
# Log out and back in, then verify:
docker compose version
```

---

## First Deployment

### Step 1 — Clone or copy the repository

```bash
cd /opt
git clone <your-repo-url> phx
cd phx
```

### Step 2 — Configure your environment

```bash
cp .env.example .env
nano .env  # or use your preferred editor
```

The minimum required settings:
```
POSTGRES_PASSWORD=<choose a strong password>
JWT_SECRET_KEY=<run: openssl rand -hex 32>
TENANT_ID=your-company-name
```

Generate a JWT key:
```bash
openssl rand -hex 32
```

### Step 3 — Set up customer data directories

These are the folders where you will place approved company files.
PHX reads them as read-only — it cannot modify your files.

```bash
mkdir -p /mnt/customer-shares/shared
mkdir -p /mnt/customer-shares/operations
mkdir -p /mnt/customer-shares/hr
mkdir -p /mnt/customer-shares/management
```

You can place files here now or after the stack is running.

### Step 4 — Run the install script

```bash
bash scripts/install.sh
```

This will:
- Build Docker images
- Start all services
- Run database migrations
- Create demo users

The first startup downloads AI models (llama3.2 and nomic-embed-text).
This may take 10–20 minutes depending on your connection.
**After installation, no internet access is needed.**

### Step 5 — Verify everything is running

```bash
bash scripts/healthcheck.sh
```

You should see all green checkmarks.

### Step 6 — Open the UI

Open a web browser and navigate to: `http://your-server-ip:3000`

Default credentials (change these immediately):
- `admin@example.com` / `changeme123`
- `ops@example.com` / `changeme123`

---

## Port Reference

| Port | Service | Notes |
|------|---------|-------|
| 3000 | phx-ui (web chat) | LAN-accessible |
| 8000 | phx-api (FastAPI) | localhost only by default |
| 6333 | phx-qdrant (vector DB) | localhost only |
| 11434 | phx-ollama (AI models) | localhost only |
| 5432 | phx-postgres (database) | localhost only |

Only port 3000 is exposed to your LAN. All others are internal.

---

## Adding Your Documents

1. Copy approved files to the relevant directory:
   ```bash
   cp /path/to/company-docs/* /mnt/customer-shares/shared/
   ```

2. Supported file types: `.txt`, `.md`, `.pdf`, `.docx`, `.csv`, `.xlsx`

3. Trigger ingestion:
   ```bash
   docker compose -f docker/compose.yaml exec phx-ingest python -m app.main --once
   ```

4. Watch the logs to confirm files were indexed:
   ```bash
   docker compose -f docker/compose.yaml logs phx-ingest -f
   ```

---

## Updating PHX

```bash
# Get the latest code (or extract the new release bundle)
git pull

# Run the update script
bash scripts/update.sh
```

This rebuilds the application images, runs any new migrations, and restarts
application services. Your data (Postgres, Qdrant, Ollama models) is preserved.

---

## Backups

### Backup Postgres (application data, users, audit logs)

```bash
docker compose -f docker/compose.yaml exec phx-postgres \
  pg_dump -U phx phx > backup-$(date +%Y%m%d).sql
```

### Backup Qdrant (vector index)

Qdrant has a snapshot API:
```bash
curl -X POST http://localhost:6333/collections/phx_chunks/snapshots
```
Snapshots are stored in the `phx_qdrant_storage` volume.
To find the volume location:
```bash
docker volume inspect phx_qdrant_storage
```

### Restore Postgres

```bash
docker compose -f docker/compose.yaml exec -T phx-postgres \
  psql -U phx phx < backup-20240101.sql
```

---

## Offline Install from Release Bundle

When delivering PHX to a customer without internet access:

1. Copy the release tarball: `phx-v1.0.0.tar.gz`
2. On the customer server:
   ```bash
   tar -xzf phx-v1.0.0.tar.gz
   cd release-bundle
   cp .env.example .env
   # Fill in .env values
   bash scripts/install-offline.sh
   ```

The offline installer loads Docker images from the tarball (no internet needed).

---

## Stopping and Starting

```bash
# Stop all services (data is preserved)
docker compose -f docker/compose.yaml stop

# Start all services
docker compose -f docker/compose.yaml start

# Stop and remove containers (data volumes preserved)
docker compose -f docker/compose.yaml down

# Full reset including data volumes (DESTROYS ALL DATA)
docker compose -f docker/compose.yaml down -v  # USE WITH CAUTION
```
