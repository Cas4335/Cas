#!/usr/bin/env bash
# PHX Update Script
# Applies updates to a running PHX deployment with minimal downtime.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log()  { echo -e "${GREEN}[PHX]${NC} $*"; }
warn() { echo -e "${YELLOW}[PHX WARN]${NC} $*"; }

log "Starting PHX update..."

# --------------------------------------------------------------------------
# Rebuild application images
# --------------------------------------------------------------------------
log "Rebuilding application images..."
docker compose -f "${REPO_ROOT}/docker/compose.yaml" build phx-api phx-ingest phx-ui

# --------------------------------------------------------------------------
# Apply database migrations
# --------------------------------------------------------------------------
log "Running database migrations..."
docker compose -f "${REPO_ROOT}/docker/compose.yaml" run --rm phx-api alembic upgrade head

# --------------------------------------------------------------------------
# Restart application services (rolling)
# Data services (postgres, qdrant, ollama) are kept running
# --------------------------------------------------------------------------
log "Restarting API service..."
docker compose -f "${REPO_ROOT}/docker/compose.yaml" up -d --no-deps phx-api

log "Restarting ingest service..."
docker compose -f "${REPO_ROOT}/docker/compose.yaml" up -d --no-deps phx-ingest

log "Restarting UI service..."
docker compose -f "${REPO_ROOT}/docker/compose.yaml" up -d --no-deps phx-ui

log "Waiting for services to be healthy..."
sleep 10

# --------------------------------------------------------------------------
# Verify
# --------------------------------------------------------------------------
"${SCRIPT_DIR}/healthcheck.sh"

log "Update complete."
