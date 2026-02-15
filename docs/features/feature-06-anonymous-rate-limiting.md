# Feature 06 - Anonymous Rate Limiting

## Status
Built

## What it does
Protects the public resolver with anonymous per-IP limits.

## Policy
- `100` requests per hour per IP (Phase 2 free tier baseline)

## Key behavior
- Returns `429 Too Many Requests` when limit is exceeded
- Provides rate limit metadata in resolve responses

## Where implemented
- `cloud/internal/ratelimit/`
- `cloud/cmd/resolver/main.go`
