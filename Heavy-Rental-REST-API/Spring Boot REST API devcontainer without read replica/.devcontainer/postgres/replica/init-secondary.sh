#!/usr/bin/env bash
set -euo pipefail

PGDATA=/var/lib/postgresql/data
PRIMARY_HOST="${PRIMARY_HOST:-db-primary}"
PRIMARY_PORT="${PRIMARY_PORT:-5432}"
REPLICATION_USER="${REPLICATION_USER:-replicator}"
REPLICATION_PASSWORD="${REPLICATION_PASSWORD:-replicatorpass}"

if [ -z "$(ls -A "$PGDATA")" ]; then
  echo "Bootstrapping replica from primary ${PRIMARY_HOST}:${PRIMARY_PORT}"
  export PGPASSWORD="$REPLICATION_PASSWORD"
  pg_basebackup -h "$PRIMARY_HOST" -D "$PGDATA" -U "$REPLICATION_USER" -P -v --wal-method=stream
  chmod 700 "$PGDATA"
  chown -R postgres:postgres "$PGDATA"
  touch "$PGDATA/standby.signal"
  cat >> "$PGDATA/postgresql.auto.conf" <<EOF2
primary_conninfo = 'host=${PRIMARY_HOST} port=${PRIMARY_PORT} user=${REPLICATION_USER} password=${REPLICATION_PASSWORD} application_name=postgres-secondary'
primary_slot_name = 'replica_slot'
EOF2
fi

# Start postgres as the postgres user to avoid root execution errors.
exec gosu postgres postgres -c config_file=/etc/postgresql/postgresql.conf -c hba_file=/etc/postgresql/pg_hba.conf
