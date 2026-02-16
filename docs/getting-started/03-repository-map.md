# 03 - Repository Map

## `coordsapp/spec`
Protocol and documentation source of truth:
- v1 format docs
- test vectors
- phases/features docs

## `coordsapp/core`
Go CLI:
- `coords encode lat lng alt`
- `coords decode <uri>`
- Works offline

## `coordsapp/cloud`
Hosted API and platform services:
- `/v1/resolve/{handle}`
- Auth, orgs, RBAC
- Alias claiming and verification
- Billing, domains, SLA/status
- Warehouse workflows (`/v1/warehouses/...`)
- Dock verification and operations (`/v1/warehouses/{id}/operations/...`)
- Map platform (`/map`, `/explore`, `/v1/map/resolve`)
- Active coordination runtime (`/v1/routing/plan`, `/v1/coordination/...`)

Key Phase 5 implementation paths:
- `cloud/internal/warehouse/service.go`
- `cloud/handlers/warehouses/`
- `cloud/storage/schema_phase5_warehouse.sql`

Key Phase 8 and Phase 9 implementation paths:
- `cloud/handlers/web/web_map_v2.go`
- `cloud/internal/mapview/service.go`
- `cloud/internal/coordination/`
- `cloud/handlers/coordination/`
- `cloud/storage/schema_phase9_coordination.sql`
