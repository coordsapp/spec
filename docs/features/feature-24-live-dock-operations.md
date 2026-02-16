# Feature 24 - Live Dock Operations

## Status
Built

## What it does
Tracks real-time dock usage events to power operations dashboards and handoff coordination.

## Key behavior
- Arrive/depart event lifecycle
- Current dock occupancy state
- Trailer/workflow context per operation
- Aggregated warehouse operations view
- Single open operation enforced per dock

## Primary endpoints
- `GET /v1/warehouses/{id}/operations`
- `POST /v1/warehouses/{id}/operations/docks/{dock_id}/arrive`
- `POST /v1/warehouses/{id}/operations/docks/{dock_id}/depart`

## Where implemented
- `cloud/internal/warehouse/service.go`
- `cloud/handlers/warehouses/operations.go`
- `cloud/storage/schema_phase5_warehouse.sql`
