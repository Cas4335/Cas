#!/usr/bin/env bash
# PHX Health Check Script
# Checks all services and reports their status.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

PASS=0
FAIL=0

check() {
    local name="$1"
    local cmd="$2"
    if eval "$cmd" >/dev/null 2>&1; then
        echo -e "${GREEN}✓${NC} ${name}"
        PASS=$((PASS + 1))
    else
        echo -e "${RED}✗${NC} ${name}"
        FAIL=$((FAIL + 1))
    fi
}

echo "PHX Health Check"
echo "================"

# Docker services
check "phx-postgres running" "docker compose -f ${REPO_ROOT}/docker/compose.yaml ps phx-postgres | grep -q 'running\\|Up'"
check "phx-qdrant running"   "docker compose -f ${REPO_ROOT}/docker/compose.yaml ps phx-qdrant | grep -q 'running\\|Up'"
check "phx-ollama running"   "docker compose -f ${REPO_ROOT}/docker/compose.yaml ps phx-ollama | grep -q 'running\\|Up'"
check "phx-api running"      "docker compose -f ${REPO_ROOT}/docker/compose.yaml ps phx-api | grep -q 'running\\|Up'"
check "phx-ingest running"   "docker compose -f ${REPO_ROOT}/docker/compose.yaml ps phx-ingest | grep -q 'running\\|Up'"
check "phx-ui running"       "docker compose -f ${REPO_ROOT}/docker/compose.yaml ps phx-ui | grep -q 'running\\|Up'"

# HTTP endpoints
check "API health endpoint"  "curl -sf http://localhost:8000/health"
check "UI serving"           "curl -sf http://localhost:3000/"
check "Qdrant health"        "curl -sf http://localhost:6333/healthz"
check "Ollama models"        "curl -sf http://localhost:11434/api/tags"

echo ""
echo "Results: ${PASS} passed, ${FAIL} failed"

if [ $FAIL -gt 0 ]; then
    echo ""
    echo "Troubleshooting:"
    echo "  View logs:    docker compose -f docker/compose.yaml logs <service-name>"
    echo "  Restart all:  docker compose -f docker/compose.yaml restart"
    exit 1
fi

echo -e "${GREEN}All checks passed.${NC}"
