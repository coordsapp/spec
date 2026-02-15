# Phase 2 - Resolver MVP

## Status
Completed (live deployment verified)

## Objective
Ship a public resolver API that maps human handles to immutable L1 coordinates with low friction.

## Delivered
- `GET /v1/resolve/{handle}` with validation and structured errors
- In-memory anonymous rate limiting (100 req/hr per IP)
- OpenAPI contract in `openapi/v1.yaml`
- L1 canonical encoding and checksum generation in resolver layer
- Dual store mode:
  - `STORE_MODE=memory`
  - `STORE_MODE=postgres` with `DATABASE_URL`
- PostgreSQL assets:
  - `storage/schema.sql` (idempotent)
  - `storage/seed.sql`
- Auto-migration on startup for Postgres mode
- Railway deployment assets (`Dockerfile`, `railway.toml`)

## Outcome
Resolver API is deployable and persistent, with restart-safe schema/bootstrap behavior.
