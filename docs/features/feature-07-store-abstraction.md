# Feature 07 - Store Abstraction (Memory and Postgres)

## Status
Built

## What it does
Supports dual storage modes for local development and production persistence.

## Modes
- `STORE_MODE=memory`
- `STORE_MODE=postgres` with `DATABASE_URL`

## Key behavior
- Shared store interface for resolver and alias flows
- Runtime mode switch via environment variable
- Same handler surface across both backends

## Where implemented
- `cloud/internal/resolver/store.go`
- `cloud/internal/resolver/store_factory.go`
