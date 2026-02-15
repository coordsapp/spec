# Feature 14 - Tier Quota Enforcement

## Status
Built

## What it does
Enforces per-organization alias limits based on subscription tier.

## Key policy
- Free tier baseline: `5` aliases per org

## Key behavior
- Quota checked atomically at alias claim time
- Prevents over-allocation across concurrent requests
- Returns conflict/error response when quota is exceeded

## Where implemented
- `cloud/internal/phase3/service.go`
- `cloud/storage/schema_phase3.sql`
