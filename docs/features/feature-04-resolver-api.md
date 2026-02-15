# Feature 04 - Resolver API (Handle to L1)

## Status
Built

## What it does
Exposes HTTP resolution of handles into immutable L1 coordinates.

## Endpoint
- `GET /v1/resolve/{handle}`

## Key behavior
- Validates handle syntax
- Resolves seeded and claimed handles
- Returns canonical L1 URI and alias metadata
- Returns structured errors (`400`, `404`, `429`)

## Where implemented
- `cloud/cmd/resolver/main.go`
- `cloud/internal/resolver/`
