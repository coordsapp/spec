# Feature 14 - Tier Quota Enforcement

## Status
Built

## What it does
Enforces per-organization limits based on subscription tier.

## Key policy
- Free tier baseline: `5` aliases per org
- Business tier warehouse policies:
  - up to `5` warehouses per org
  - up to `20` docks per warehouse
  - up to `10` carrier access tokens per warehouse

## Key behavior
- Quota checked atomically at alias claim time
- Quota checked for warehouse, dock, and carrier-access creation paths
- Prevents over-allocation across concurrent requests
- Returns conflict/error response when quota is exceeded

## Where implemented
- `cloud/internal/phase3/service.go`
- `cloud/storage/schema_phase3.sql`
- `cloud/internal/warehouse/service.go`
- `cloud/storage/schema_phase5_warehouse.sql`
