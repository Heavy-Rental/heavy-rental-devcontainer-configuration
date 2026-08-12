-- Phase 5 / T5 / D4: pgvector platform ready (Spec Kit 004-haystack-pgvector).
-- Runs only on first init of the data directory (docker-entrypoint-initdb.d).
-- Healthcheck also CREATE EXTENSION IF NOT EXISTS for upgraded volumes.
CREATE EXTENSION IF NOT EXISTS vector;
