#!/usr/bin/env python3
"""SQL → Cypher MERGE: project fleet tables from postgres-haystack into Neo4j.

Fleet labels only (:Asset, :Booking, :Category). Never touches DocumentStore nodes.
Spec: Haystack-Fast-API/specs/005-haystack-neo4j-populate/
"""

from __future__ import annotations

import json
import os
import sys
import time
from datetime import date, datetime, time as dtime
from decimal import Decimal
from typing import Any
from uuid import UUID

import psycopg
from neo4j import GraphDatabase
from neo4j.exceptions import Neo4jError, ServiceUnavailable
from psycopg import sql
from psycopg.rows import dict_row

# Table (SQL) → Neo4j node label
DEFAULT_TABLE_LABELS: dict[str, str] = {
    "asset": "Asset",
    "booking": "Booking",
    "category": "Category",
}

# Internal props written by this job (not from SQL)
INTERNAL_PROPS = frozenset({"_source", "_populated_at"})


def log(msg: str) -> None:
    print(f"[neo4j-populate] {msg}", flush=True)


def env(name: str, default: str | None = None) -> str:
    val = os.environ.get(name, default)
    if val is None or val == "":
        if default is not None:
            return default
        raise SystemExit(f"Missing required env: {name}")
    return val


def parse_allowlist(raw: str) -> list[str]:
    raw = (raw or "").replace(" ", "")
    if not raw or raw.lower() in ("all", "*"):
        return list(DEFAULT_TABLE_LABELS.keys())
    # Relation name safety for SQL identifiers (alnum + underscore)
    cleaned = [t for t in raw.split(",") if t and all(c.isalnum() or c == "_" for c in t)]
    return cleaned or list(DEFAULT_TABLE_LABELS.keys())


def parse_labels(raw: str) -> set[str]:
    labels: set[str] = set()
    for x in (raw or "").split(","):
        label = x.strip()
        # Cypher label safety: alphanumeric + underscore only
        if label and label.replace("_", "").isalnum():
            labels.add(label)
    return labels or set(DEFAULT_TABLE_LABELS.values())


def coerce_value(value: Any) -> Any:
    """Convert Postgres values to Neo4j-safe scalars."""
    if value is None:
        return None
    if isinstance(value, bool):
        return value
    if isinstance(value, int) and not isinstance(value, bool):
        return value
    if isinstance(value, float):
        return value
    if isinstance(value, Decimal):
        # Prefer int when exact
        if value == value.to_integral_value():
            return int(value)
        return float(value)
    if isinstance(value, (datetime, date, dtime)):
        return value.isoformat()
    if isinstance(value, UUID):
        return str(value)
    if isinstance(value, (bytes, memoryview)):
        return bytes(value).hex()
    if isinstance(value, (list, dict)):
        return json.dumps(value, default=str)
    return value


def coerce_row(row: dict[str, Any]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for k, v in row.items():
        if k is None:
            continue
        key = str(k)
        if key.startswith("_"):
            # Avoid colliding with internal props from SQL columns named _*
            key = f"sql{key}"
        out[key] = coerce_value(v)
    return out


def table_exists(conn: psycopg.Connection, table: str) -> bool:
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT 1
            FROM information_schema.tables
            WHERE table_schema = 'public' AND table_name = %s
            """,
            (table,),
        )
        return cur.fetchone() is not None


def table_has_column(conn: psycopg.Connection, table: str, column: str) -> bool:
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT 1
            FROM information_schema.columns
            WHERE table_schema = 'public' AND table_name = %s AND column_name = %s
            """,
            (table, column),
        )
        return cur.fetchone() is not None


def fetch_rows(conn: psycopg.Connection, table: str) -> list[dict[str, Any]]:
    query = sql.SQL("SELECT * FROM {}.{}").format(
        sql.Identifier("public"),
        sql.Identifier(table),
    )
    with conn.cursor(row_factory=dict_row) as cur:
        cur.execute(query)
        return list(cur.fetchall())


def ensure_constraints(session, labels: set[str]) -> None:
    for label in sorted(labels):
        # Constraint names must be unique; label is alphanumeric from allowlist mapping.
        name = f"fleet_{label.lower()}_id"
        cypher = (
            f"CREATE CONSTRAINT {name} IF NOT EXISTS "
            f"FOR (n:`{label}`) REQUIRE n.id IS UNIQUE"
        )
        session.run(cypher)


def clear_fleet_labels(session, labels: set[str]) -> int:
    """Label-scoped delete only — never MATCH (n) DETACH DELETE n."""
    deleted = 0
    for label in sorted(labels):
        count_result = session.run(f"MATCH (n:`{label}`) RETURN count(n) AS c")
        record = count_result.single()
        n = int(record["c"]) if record else 0
        if n:
            session.run(f"MATCH (n:`{label}`) DETACH DELETE n")
            deleted += n
    return deleted


def merge_nodes(session, label: str, rows: list[dict[str, Any]]) -> int:
    if not rows:
        return 0
    merged = 0
    cypher = (
        f"UNWIND $rows AS row "
        f"MERGE (n:`{label}` {{id: row.id}}) "
        f"SET n += row.props, n._source = 'fleet-mirror', n._populated_at = datetime() "
        f"RETURN count(n) AS c"
    )
    batch: list[dict[str, Any]] = []
    for row in rows:
        props = coerce_row(row)
        if "id" not in props or props["id"] is None:
            continue
        node_id = props.pop("id")
        # Keep id in props too for property completeness
        props["id"] = node_id
        # Strip internal keys if SQL somehow produced them
        for k in list(props.keys()):
            if k in INTERNAL_PROPS:
                props.pop(k, None)
        batch.append({"id": node_id, "props": props})
    if not batch:
        return 0
    # Chunk to avoid huge transactions
    chunk_size = 500
    for i in range(0, len(batch), chunk_size):
        chunk = batch[i : i + chunk_size]
        result = session.run(cypher, rows=chunk)
        record = result.single()
        merged += int(record["c"]) if record else len(chunk)
    return merged


def merge_relationships(session, conn: psycopg.Connection) -> dict[str, int]:
    """Best-effort FK edges when columns exist."""
    counts: dict[str, int] = {}

    # Asset → Category
    if (
        table_exists(conn, "asset")
        and table_exists(conn, "category")
        and table_has_column(conn, "asset", "id")
    ):
        # Common FK column names
        cat_col = None
        for candidate in ("category_id", "categoryId", "category"):
            if table_has_column(conn, "asset", candidate):
                cat_col = candidate
                break
        if cat_col:
            query = sql.SQL(
                "SELECT id AS asset_id, {} AS category_id FROM public.asset "
                "WHERE {} IS NOT NULL"
            ).format(sql.Identifier(cat_col), sql.Identifier(cat_col))
            with conn.cursor(row_factory=dict_row) as cur:
                cur.execute(query)
                rows = [
                    {
                        "asset_id": coerce_value(r["asset_id"]),
                        "category_id": coerce_value(r["category_id"]),
                    }
                    for r in cur.fetchall()
                ]
            if rows:
                cypher = (
                    "UNWIND $rows AS row "
                    "MATCH (a:Asset {id: row.asset_id}) "
                    "MATCH (c:Category {id: row.category_id}) "
                    "MERGE (a)-[r:IN_CATEGORY]->(c) "
                    "RETURN count(r) AS c"
                )
                result = session.run(cypher, rows=rows)
                rec = result.single()
                counts["IN_CATEGORY"] = int(rec["c"]) if rec else 0

    # Booking → Asset
    if (
        table_exists(conn, "booking")
        and table_exists(conn, "asset")
        and table_has_column(conn, "booking", "id")
    ):
        asset_col = None
        for candidate in ("asset_id", "assetId", "asset"):
            if table_has_column(conn, "booking", candidate):
                asset_col = candidate
                break
        if asset_col:
            query = sql.SQL(
                "SELECT id AS booking_id, {} AS asset_id FROM public.booking "
                "WHERE {} IS NOT NULL"
            ).format(sql.Identifier(asset_col), sql.Identifier(asset_col))
            with conn.cursor(row_factory=dict_row) as cur:
                cur.execute(query)
                rows = [
                    {
                        "booking_id": coerce_value(r["booking_id"]),
                        "asset_id": coerce_value(r["asset_id"]),
                    }
                    for r in cur.fetchall()
                ]
            if rows:
                cypher = (
                    "UNWIND $rows AS row "
                    "MATCH (b:Booking {id: row.booking_id}) "
                    "MATCH (a:Asset {id: row.asset_id}) "
                    "MERGE (b)-[r:FOR_ASSET]->(a) "
                    "RETURN count(r) AS c"
                )
                result = session.run(cypher, rows=rows)
                rec = result.single()
                counts["FOR_ASSET"] = int(rec["c"]) if rec else 0

    return counts


def run_cycle(
    pg_conninfo: str,
    neo4j_uri: str,
    neo4j_user: str,
    neo4j_password: str,
    neo4j_database: str,
    tables: list[str],
    fleet_labels: set[str],
    mode: str,
) -> int:
    """Run one populate cycle. Returns 0 on success/soft-skip, 1 on hard failure."""
    t0 = time.monotonic()
    mode = (mode or "merge").lower().strip()
    if mode not in ("merge", "rebuild"):
        log(f"WARN: unknown POPULATE_MODE={mode!r}; using merge")
        mode = "merge"

    skipped_missing = 0
    skipped_no_id = 0
    nodes_merged = 0
    tables_ok = 0
    deleted = 0
    rel_counts: dict[str, int] = {}

    try:
        with psycopg.connect(pg_conninfo, connect_timeout=5) as conn:
            driver = GraphDatabase.driver(
                neo4j_uri, auth=(neo4j_user, neo4j_password)
            )
            try:
                driver.verify_connectivity()
                with driver.session(database=neo4j_database) as session:
                    ensure_constraints(session, fleet_labels)

                    if mode == "rebuild":
                        deleted = clear_fleet_labels(session, fleet_labels)
                        log(
                            f"rebuild: deleted fleet nodes count={deleted} "
                            f"labels={','.join(sorted(fleet_labels))}"
                        )

                    for table in tables:
                        label = DEFAULT_TABLE_LABELS.get(table)
                        if not label:
                            # Unknown table: PascalCase fallback only if in fleet_labels
                            label = table[:1].upper() + table[1:]
                        if label not in fleet_labels:
                            log(
                                f"SKIP table={table}: label {label} not in FLEET_LABELS "
                                f"(isolation)"
                            )
                            skipped_missing += 1
                            continue
                        if not table_exists(conn, table):
                            log(f"SKIP table={table}: not found in public")
                            skipped_missing += 1
                            continue
                        if not table_has_column(conn, table, "id"):
                            log(f"SKIP table={table}: no id column")
                            skipped_no_id += 1
                            continue
                        rows = fetch_rows(conn, table)
                        n = merge_nodes(session, label, rows)
                        nodes_merged += n
                        tables_ok += 1
                        log(f"MERGE label={label} table={table} rows={len(rows)} merged={n}")

                    rel_counts = merge_relationships(session, conn)
                    for rel, c in rel_counts.items():
                        log(f"MERGE rel={rel} count={c}")
            finally:
                driver.close()
    except (psycopg.OperationalError, psycopg.Error) as exc:
        duration_ms = int((time.monotonic() - t0) * 1000)
        log(f"SKIP cycle: postgres unavailable: {exc}")
        log(
            f"METRICS populate status=skip_pg duration_ms={duration_ms} "
            f"mode={mode} nodes_merged=0"
        )
        return 0
    except (ServiceUnavailable, Neo4jError, OSError) as exc:
        duration_ms = int((time.monotonic() - t0) * 1000)
        log(f"SKIP cycle: neo4j unavailable: {exc}")
        log(
            f"METRICS populate status=skip_neo4j duration_ms={duration_ms} "
            f"mode={mode} nodes_merged=0"
        )
        return 0
    except Exception as exc:  # noqa: BLE001 — cycle isolation
        duration_ms = int((time.monotonic() - t0) * 1000)
        log(f"ERROR cycle failed: {exc}")
        log(
            f"METRICS populate status=error duration_ms={duration_ms} "
            f"mode={mode} nodes_merged={nodes_merged}"
        )
        return 0  # soft-fail: keep loop alive

    duration_ms = int((time.monotonic() - t0) * 1000)
    rel_total = sum(rel_counts.values())
    log(
        f"METRICS populate status=ok duration_ms={duration_ms} mode={mode} "
        f"tables_ok={tables_ok} skipped_missing={skipped_missing} "
        f"skipped_no_id={skipped_no_id} nodes_merged={nodes_merged} "
        f"rels_merged={rel_total} rebuild_deleted={deleted}"
    )
    return 0


def main(argv: list[str] | None = None) -> int:
    argv = argv if argv is not None else sys.argv[1:]
    once = "--once" in argv

    pg_host = env("PGHOST", env("TARGET_HOST", "postgres-haystack"))
    pg_port = env("PGPORT", env("TARGET_PORT", "5432"))
    pg_user = env("PGUSER", env("TARGET_USER", "postgres"))
    pg_password = env("PGPASSWORD", env("TARGET_PASSWORD", "postgres"))
    pg_db = env("PGDATABASE", env("TARGET_DB", "heavy_rental"))
    pg_conninfo = (
        f"host={pg_host} port={pg_port} user={pg_user} "
        f"password={pg_password} dbname={pg_db}"
    )

    neo4j_uri = env("NEO4J_URI", "bolt://neo4j:7687")
    neo4j_user = env("NEO4J_USER", "neo4j")
    neo4j_password = env("NEO4J_PASSWORD", "heavyrental")
    neo4j_database = env("NEO4J_DATABASE", "neo4j")

    tables = parse_allowlist(
        env("FLEET_TABLE_ALLOWLIST", env("SYNC_TABLE_ALLOWLIST", "asset,booking,category"))
    )
    fleet_labels = parse_labels(
        env("FLEET_LABELS", "Asset,Booking,Category")
    )
    mode = env("POPULATE_MODE", "merge")
    interval = int(env("POPULATE_INTERVAL_SECONDS", "60"))
    if interval < 1:
        interval = 60

    log(
        f"Config: pg={pg_host}:{pg_port}/{pg_db} neo4j={neo4j_uri} "
        f"db={neo4j_database} tables={','.join(tables)} "
        f"labels={','.join(sorted(fleet_labels))} mode={mode} "
        f"interval={interval}s once={once}"
    )

    if once:
        return run_cycle(
            pg_conninfo,
            neo4j_uri,
            neo4j_user,
            neo4j_password,
            neo4j_database,
            tables,
            fleet_labels,
            mode,
        )

    while True:
        run_cycle(
            pg_conninfo,
            neo4j_uri,
            neo4j_user,
            neo4j_password,
            neo4j_database,
            tables,
            fleet_labels,
            mode,
        )
        time.sleep(interval)


if __name__ == "__main__":
    raise SystemExit(main())
