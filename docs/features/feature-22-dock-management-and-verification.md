# Feature 22 - Dock Management and Verification

## Status
Planned

## What it does
Adds dock-level resources under warehouses with geofenced verification and operational metadata.

## Key behavior
- Dock handle format: `@org/warehouse/dock`
- Verification states: pending, verified, deprecated
- Geofence verification with accuracy tracking
- Dock capability metadata (loading type, trailer constraints)

## Primary endpoints
- `POST /v1/warehouses/{id}/docks`
- `GET /v1/warehouses/{id}/docks`
- `GET /v1/warehouses/{id}/docks/{dock_id}`
- `PATCH /v1/warehouses/{id}/docks/{dock_id}`
- `DELETE /v1/warehouses/{id}/docks/{dock_id}`
- `POST /v1/warehouses/{id}/docks/{dock_id}/verify`
