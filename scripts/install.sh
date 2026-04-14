#!/usr/bin/env bash
# PHX Install Script
# Performs first-time setup for a PHX deployment.
# Run as root or with sudo on the target Linux server.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log() { echo -e "${GREEN}[PHX]${NC} $*"; }
warn() { echo -e "${YELLOW}[PHX WARN]${NC} $*"; }
die() { echo -e "${RED}[PHX ERROR]${NC} $*" >&2; exit 1; }

# --------------------------------------------------------------------------
# Check prerequisites
# --------------------------------------------------------------------------
log "Checking prerequisites..."

command -v docker >/dev/null 2>&1 || die "Docker is not installed. Install Docker Engine first."
command -v docker compose version >/dev/null 2>&1 || die "Docker Compose v2 not found. Upgrade Docker."

DOCKER_VERSION=$(docker --version | grep -oP '\d+\.\d+' | head -1)
log "Docker version: ${DOCKER_VERSION}"

# Check for .env file
if [ ! -f "${REPO_ROOT}/.env" ]; then
    if [ -f "${REPO_ROOT}/.env.example" ]; then
        warn ".env not found. Copying from .env.example..."
        cp "${REPO_ROOT}/.env.example" "${REPO_ROOT}/.env"
        warn "IMPORTANT: Edit .env and set real values before continuing."
        echo ""
        echo "  Required fields to set:"
        echo "    POSTGRES_PASSWORD=<strong password>"
        echo "    JWT_SECRET_KEY=<run: openssl rand -hex 32>"
        echo ""
        read -p "Press Enter to continue after editing .env, or Ctrl+C to cancel..."
    else
        die "No .env or .env.example found in ${REPO_ROOT}"
    fi
fi

# Validate required env vars
source "${REPO_ROOT}/.env"
[ -z "${POSTGRES_PASSWORD:-}" ] && die "POSTGRES_PASSWORD is not set in .env"
[ -z "${JWT_SECRET_KEY:-}" ] && die "JWT_SECRET_KEY is not set in .env"
[ "${JWT_SECRET_KEY}" = "CHANGE_ME_generate_with_openssl_rand_hex_32" ] && \
    die "JWT_SECRET_KEY is still the placeholder. Generate a real key: openssl rand -hex 32"

# --------------------------------------------------------------------------
# Create customer data directories
# --------------------------------------------------------------------------
log "Creating customer data mount directories..."
mkdir -p /mnt/customer-shares/shared
mkdir -p /mnt/customer-shares/operations
mkdir -p /mnt/customer-shares/hr
mkdir -p /mnt/customer-shares/management

# --------------------------------------------------------------------------
# Pull images (offline install: skip this section and use docker load instead)
# --------------------------------------------------------------------------
if [ "${OFFLINE_INSTALL:-0}" = "1" ]; then
    log "Offline install mode: loading images from release bundle..."
    BUNDLE_DIR="${BUNDLE_DIR:-${REPO_ROOT}/release-bundle/images}"
    for tarfile in "${BUNDLE_DIR}"/*.tar; do
        [ -f "$tarfile" ] || continue
        log "Loading ${tarfile}..."
        docker load -i "${tarfile}"
    done
else
    log "Pulling base images..."
    docker compose -f "${REPO_ROOT}/docker/compose.yaml" pull postgres qdrant 2>/dev/null || true
fi

# --------------------------------------------------------------------------
# Build application images
# --------------------------------------------------------------------------
log "Building application images..."
docker compose -f "${REPO_ROOT}/docker/compose.yaml" build

# --------------------------------------------------------------------------
# Start infrastructure services first
# --------------------------------------------------------------------------
log "Starting infrastructure services (postgres, qdrant)..."
docker compose -f "${REPO_ROOT}/docker/compose.yaml" up -d phx-postgres phx-qdrant

log "Waiting for Postgres to be ready..."
for i in $(seq 1 30); do
    if docker compose -f "${REPO_ROOT}/docker/compose.yaml" exec -T phx-postgres \
        pg_isready -U "${POSTGRES_USER:-phx}" -d "${POSTGRES_DB:-phx}" >/dev/null 2>&1; then
        break
    fi
    sleep 2
done

# --------------------------------------------------------------------------
# Run migrations
# --------------------------------------------------------------------------
log "Running database migrations..."
docker compose -f "${REPO_ROOT}/docker/compose.yaml" run --rm phx-api \
    alembic upgrade head

# --------------------------------------------------------------------------
# Seed demo data
# --------------------------------------------------------------------------
log "Seeding demo users and roles..."
docker compose -f "${REPO_ROOT}/docker/compose.yaml" run --rm phx-api \
    python -m app.scripts.seed

# --------------------------------------------------------------------------
# Start all services
# --------------------------------------------------------------------------
log "Starting all services..."
docker compose -f "${REPO_ROOT}/docker/compose.yaml" up -d

log "Waiting for stack to be healthy..."
sleep 10
"${SCRIPT_DIR}/healthcheck.sh" || warn "Some services not yet healthy. Check logs."

echo ""
log "Installation complete!"
echo ""
echo "  UI:  http://localhost:3000"
echo "  API: http://localhost:8000"
echo ""
echo "  Default credentials (CHANGE BEFORE USING REAL DATA):"
echo "    admin@example.com / changeme123"
echo "    ops@example.com / changeme123"
echo ""
echo "  Next steps:"
echo "    1. Place approved files in /mnt/customer-shares/<department>/"
echo "    2. Edit config/customer-template/sources.yaml"
echo "    3. Trigger first ingest:"
echo "       docker compose -f docker/compose.yaml exec phx-ingest python -m app.main --once"
