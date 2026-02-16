# Feature 22 - Dock Management and Verification

## Status
Built

## What it does
Adds dock-level resources under warehouses with geofenced verification and operational metadata.

## Key behavior
- Dock handle format: `@org/warehouse/dock`
- Verification states: pending, verified, deprecated
- Verification capture with latitude/longitude and accuracy tracking
- Dock capability metadata (loading type, trailer constraints)
- Business-tier dock quota enforcement per warehouse

## Primary endpoints
- `POST /v1/warehouses/{id}/docks`
- `GET /v1/warehouses/{id}/docks`
- `GET /v1/warehouses/{id}/docks/{dock_id}`
- `PATCH /v1/warehouses/{id}/docks/{dock_id}`
- `DELETE /v1/warehouses/{id}/docks/{dock_id}`
- `POST /v1/warehouses/{id}/docks/{dock_id}/verify`

## Where implemented
- `cloud/internal/warehouse/service.go`
- `cloud/handlers/warehouses/docks.go`
- `cloud/storage/schema_phase5_warehouse.sql`
