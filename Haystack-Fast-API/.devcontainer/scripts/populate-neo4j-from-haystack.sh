#!/usr/bin/env bash
# Project allowlisted fleet tables from postgres-haystack into Neo4j (Cypher MERGE).
# Spec: Haystack-Fast-API/specs/005-haystack-neo4j-populate/
# Contract: contracts/neo4j-populate-env.md
#
# Env (defaults):
#   PGHOST / TARGET_HOST=postgres-haystack
#   PGPORT / TARGET_PORT=5432
#   PGUSER / TARGET_USER=postgres
#   PGPASSWORD / TARGET_PASSWORD=postgres
#   PGDATABASE / TARGET_DB=heavy_rental
#   NEO4J_URI=bolt://neo4j:7687
#   NEO4J_USER=neo4j NEO4J_PASSWORD=heavyrental NEO4J_DATABASE=neo4j
#   FLEET_TABLE_ALLOWLIST=asset,booking,category
#   FLEET_LABELS=Asset,Booking,Category
#   POPULATE_MODE=merge|rebuild
#   POPULATE_INTERVAL_SECONDS=60
#   POPULATE_ONCE=false   # if true, run one cycle and exit
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKER="${SCRIPT_DIR}/populate_neo4j.py"

log() {
  echo "[neo4j-populate] $*"
}

if [[ ! -f "$WORKER" ]]; then
  log "ERROR: worker not found at ${WORKER}"
  exit 1
fi

# Normalize dual env names used by merge-sync pack
export PGHOST="${PGHOST:-${TARGET_HOST:-postgres-haystack}}"
export PGPORT="${PGPORT:-${TARGET_PORT:-5432}}"
export PGUSER="${PGUSER:-${TARGET_USER:-postgres}}"
export PGPASSWORD="${PGPASSWORD:-${TARGET_PASSWORD:-postgres}}"
export PGDATABASE="${PGDATABASE:-${TARGET_DB:-heavy_rental}}"

export NEO4J_URI="${NEO4J_URI:-bolt://neo4j:7687}"
export NEO4J_USER="${NEO4J_USER:-neo4j}"
export NEO4J_PASSWORD="${NEO4J_PASSWORD:-heavyrental}"
export NEO4J_DATABASE="${NEO4J_DATABASE:-neo4j}"

export FLEET_TABLE_ALLOWLIST="${FLEET_TABLE_ALLOWLIST:-${SYNC_TABLE_ALLOWLIST:-asset,booking,category}}"
export FLEET_LABELS="${FLEET_LABELS:-Asset,Booking,Category}"
export POPULATE_MODE="${POPULATE_MODE:-merge}"
export POPULATE_INTERVAL_SECONDS="${POPULATE_INTERVAL_SECONDS:-60}"
POPULATE_ONCE="${POPULATE_ONCE:-false}"

log "Entrypoint: worker=${WORKER} once=${POPULATE_ONCE} mode=${POPULATE_MODE} interval=${POPULATE_INTERVAL_SECONDS}s"
log "Source: ${PGUSER}@${PGHOST}:${PGPORT}/${PGDATABASE} → ${NEO4J_URI} (labels=${FLEET_LABELS})"

ARGS=()
case "${POPULATE_ONCE,,}" in
  1|true|yes|on) ARGS+=(--once) ;;
esac

# Also accept --once on CLI
for arg in "$@"; do
  if [[ "$arg" == "--once" ]]; then
    ARGS+=(--once)
  fi
done

exec python3 "$WORKER" "${ARGS[@]+"${ARGS[@]}"}"
