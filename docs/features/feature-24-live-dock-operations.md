# Feature 24 - Live Dock Operations

## Status
Planned

## What it does
Tracks real-time dock usage events to power operations dashboards and handoff coordination.

## Key behavior
- Arrive/depart event lifecycle
- Current dock occupancy state
- Trailer/workflow context per operation
- Aggregated warehouse operations view

## Primary endpoints
- `GET /v1/warehouses/{id}/operations`
- `POST /v1/warehouses/{id}/operations/docks/{dock_id}/arrive`
- `POST /v1/warehouses/{id}/operations/docks/{dock_id}/depart`
