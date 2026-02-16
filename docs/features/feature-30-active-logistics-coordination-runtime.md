# Feature 30 - Active Logistics Coordination Runtime

## Status
Built (initial Phase 9 slice delivered February 16, 2026)

## What it does
Adds the first operational coordination runtime for logistics workflows on top of coords handles.

## Key behavior
- Route planning:
1. `POST /v1/routing/plan`
2. accepts origin/destination/stops as handles or literal `lat,lng`
3. returns normalized waypoints, route legs, total distance, and ETA
- Dock assignment:
1. `POST /v1/coordination/assign-dock`
2. selects an available verified dock for the requested warehouse
3. persists assignment state for operational coordination
- Dock state:
1. `GET /v1/coordination/docks/{id}/status`
2. resolves dock state as one of `available`, `occupied`, `cleaning`, `unavailable`, `assigned`
- Arrival alerts:
1. `POST /v1/notifications/arrival-alert`
2. queues channel-specific notifications (`sms`, `email`, `push`)
- SLA analytics:
1. `GET /v1/analytics/sla-compliance`
2. provides on-time/late performance rollups by carrier and dock

## API Surface
- `POST /v1/routing/plan`
- `POST /v1/coordination/assign-dock`
- `GET /v1/coordination/docks/{id}/status`
- `POST /v1/notifications/arrival-alert`
- `GET /v1/analytics/sla-compliance`

## Where implemented
- `cloud/internal/coordination/`
- `cloud/handlers/coordination/`
- `cloud/cmd/resolver/routes_enterprise.go`
- `cloud/openapi/v1-phase9.yaml`
- `cloud/storage/schema_phase9_coordination.sql`

## Notes
- This is a runtime foundation slice for Phase 9.
- Route ETA is currently computed from geodesic distance and vehicle profile speed heuristics.
- Deeper external routing/provider integrations are planned in subsequent Phase 9 increments.
