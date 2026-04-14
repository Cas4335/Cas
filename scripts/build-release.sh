#!/usr/bin/env bash
# PHX Release Bundle Builder
# Produces a self-contained release folder for offline customer deployment.
#
# Output: ./release-bundle/
#   images/         - Docker image tarballs
#   config/         - Configuration templates
#   docker/         - Compose files
#   scripts/        - Install/update/healthcheck scripts
#   docs/           - Documentation
#   .env.example    - Environment template
#   README.md       - Top-level readme

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
VERSION="${VERSION:-v1.0.0}"
BUNDLE_DIR="${REPO_ROOT}/release-bundle"

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log()  { echo -e "${GREEN}[PHX]${NC} $*"; }
warn() { echo -e "${YELLOW}[PHX WARN]${NC} $*"; }

log "Building PHX release bundle version ${VERSION}..."

# --------------------------------------------------------------------------
# Clean previous bundle
# --------------------------------------------------------------------------
rm -rf "${BUNDLE_DIR}"
mkdir -p "${BUNDLE_DIR}/images"

# --------------------------------------------------------------------------
# Build application images
# --------------------------------------------------------------------------
log "Building application images..."
docker compose -f "${REPO_ROOT}/docker/compose.yaml" build

# --------------------------------------------------------------------------
# Export images as tarballs (for offline delivery)
# --------------------------------------------------------------------------
log "Exporting images..."

IMAGES=(
    "phx-api:latest"
    "phx-ingest:latest"
    "phx-ui:latest"
)

for img in "${IMAGES[@]}"; do
    name="${img%%:*}"
    log "  Exporting ${img}..."
    docker save "${img}" -o "${BUNDLE_DIR}/images/${name}.tar"
done

# Export third-party images
log "  Exporting postgres..."
docker pull postgres:16-alpine
docker save postgres:16-alpine -o "${BUNDLE_DIR}/images/postgres.tar"

log "  Exporting qdrant..."
docker pull qdrant/qdrant:v1.9.2
docker save qdrant/qdrant:v1.9.2 -o "${BUNDLE_DIR}/images/qdrant.tar"

log "  Exporting ollama..."
docker pull ollama/ollama:latest
docker save ollama/ollama:latest -o "${BUNDLE_DIR}/images/ollama.tar"

# --------------------------------------------------------------------------
# Copy configuration and compose files
# --------------------------------------------------------------------------
log "Copying configuration files..."
cp -r "${REPO_ROOT}/docker" "${BUNDLE_DIR}/docker"
cp -r "${REPO_ROOT}/config" "${BUNDLE_DIR}/config"
cp -r "${REPO_ROOT}/docs" "${BUNDLE_DIR}/docs"
cp "${REPO_ROOT}/.env.example" "${BUNDLE_DIR}/.env.example"
cp "${REPO_ROOT}/README.md" "${BUNDLE_DIR}/README.md"

# Copy scripts (but not build-release.sh itself)
mkdir -p "${BUNDLE_DIR}/scripts"
cp "${SCRIPT_DIR}/install.sh" "${BUNDLE_DIR}/scripts/"
cp "${SCRIPT_DIR}/update.sh" "${BUNDLE_DIR}/scripts/"
cp "${SCRIPT_DIR}/healthcheck.sh" "${BUNDLE_DIR}/scripts/"
chmod +x "${BUNDLE_DIR}/scripts/"*.sh

# Create an offline-specific install wrapper
cat > "${BUNDLE_DIR}/scripts/install-offline.sh" <<'EOF'
#!/usr/bin/env bash
# Offline install: loads pre-built images from the bundle instead of pulling.
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BUNDLE_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
export OFFLINE_INSTALL=1
export BUNDLE_DIR="${BUNDLE_DIR}/images"
"${SCRIPT_DIR}/install.sh"
EOF
chmod +x "${BUNDLE_DIR}/scripts/install-offline.sh"

# --------------------------------------------------------------------------
# Create version file
# --------------------------------------------------------------------------
cat > "${BUNDLE_DIR}/VERSION" <<EOF
PHX Offline AI Knowledge Appliance
Version: ${VERSION}
Build date: $(date -u +"%Y-%m-%dT%H:%M:%SZ")
EOF

# --------------------------------------------------------------------------
# Create a tarball of the whole bundle
# --------------------------------------------------------------------------
log "Creating release tarball..."
cd "${REPO_ROOT}"
tar -czf "phx-${VERSION}.tar.gz" release-bundle/
log "Release tarball: phx-${VERSION}.tar.gz"

# --------------------------------------------------------------------------
# Summary
# --------------------------------------------------------------------------
echo ""
log "Release bundle created at: ${BUNDLE_DIR}"
log "Release tarball: ${REPO_ROOT}/phx-${VERSION}.tar.gz"
echo ""
echo "Bundle contents:"
ls -lh "${BUNDLE_DIR}/images/"
echo ""
echo "Deliver the tarball to the customer and run:"
echo "  tar -xzf phx-${VERSION}.tar.gz"
echo "  cd release-bundle"
echo "  cp .env.example .env"
echo "  # Edit .env with real values"
echo "  bash scripts/install-offline.sh"
