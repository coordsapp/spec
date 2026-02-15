# Feature 09 - Auto-Migration on Startup

## Status
Built

## What it does
Automatically applies embedded SQL schema and seed files when running in Postgres mode.

## Toggle
- `AUTO_MIGRATE=true` (default)

## Key behavior
- Runs schema files in fixed order
- Boots a fresh deployment without manual SQL execution
- Keeps startup deterministic for hosted environments

## Where implemented
- `cloud/internal/resolver/migrate.go`
- `cloud/storage/migrations.go`
- `cloud/cmd/resolver/main.go`
