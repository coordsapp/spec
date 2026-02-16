# Phase 9 - Active Logistics Coordination

## Status
In Progress (started February 16, 2026)

## Objective
Turn coords from a spatial reference system into an operational runtime for real-time logistics coordination.

## Goal
Enable end-to-end operational flow:
1. plan routes using coords handles as waypoints
2. assign carriers to optimal available docks
3. monitor live dock state
4. queue arrival alerts for warehouse teams
5. track SLA compliance by carrier and dock

## Scope
- New coordination/routing APIs:
1. `POST /v1/routing/plan`
2. `POST /v1/coordination/assign-dock`
3. `GET /v1/coordination/docks/{id}/status`
4. `POST /v1/notifications/arrival-alert`
5. `GET /v1/analytics/sla-compliance`
- New OpenAPI contract:
1. `cloud/openapi/v1-phase9.yaml`
- New schema module:
1. `cloud/storage/schema_phase9_coordination.sql`
- `/map` route planning panel integrated with `POST /v1/routing/plan`

## Delivered In This Iteration
- New coordination domain service:
1. route waypoint resolution from handles or literal `lat,lng`
2. multi-leg planning with distance and ETA rollups
3. dock assignment against currently available verified docks
4. dock state synthesis (`available`, `occupied`, `cleaning`, `unavailable`, `assigned`)
5. arrival alert queueing model and dispatch records
6. SLA compliance rollups by carrier/dock
- New coordination handlers and enterprise route wiring
- Migrations updated to include Phase 9 schema

## Operational Notes
- Service implementation:
1. `cloud/internal/coordination/`
- HTTP handlers:
1. `cloud/handlers/coordination/`
- Route registration:
1. `cloud/cmd/resolver/routes_enterprise.go`
- Startup wiring:
1. `cloud/cmd/resolver/main.go`

## Next Delivery Targets
1. external routing engine integration (OSRM/Valhalla) beyond straight-line ETA estimation
2. assignment lifecycle transitions (`arrived`, `completed`, `cancelled`) APIs
3. production delivery channels (SMS/email/push providers) for notification execution
4. deeper map overlays for live carrier tracking
