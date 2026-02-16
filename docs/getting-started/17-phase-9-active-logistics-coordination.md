# 17 - Phase 9 Active Logistics Coordination

## Status
In Progress (initial runtime slice delivered February 16, 2026)

## Why this matters
Phase 9 moves coords from "where is this location?" to "coordinate this logistics operation now."

## New APIs
- `POST /v1/routing/plan`
- `POST /v1/coordination/assign-dock`
- `GET /v1/coordination/docks/{id}/status`
- `POST /v1/notifications/arrival-alert`
- `GET /v1/analytics/sla-compliance`

## Quick Route Planning Example
```bash
curl -X POST "https://coords.up.railway.app/v1/routing/plan" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "origin":"@carrier/fastfreight-truck-123",
    "destination":"@acme/logistics-center/dock-1",
    "stops":["@fuel/dallas-north"],
    "vehicle_type":"truck"
  }'
```

## Quick Dock Assignment Example
```bash
curl -X POST "https://coords.up.railway.app/v1/coordination/assign-dock" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "warehouse_id":"<warehouse-uuid>",
    "carrier_name":"FastFreight",
    "vehicle_type":"truck",
    "planned_arrival_at":"2026-02-16T19:15:00Z"
  }'
```

## Map Integration
- `/map` route planning panel now calls `POST /v1/routing/plan`.
- `/explore` remains available as the lightweight classic map.

## Where implemented
- `cloud/internal/coordination/`
- `cloud/handlers/coordination/`
- `cloud/openapi/v1-phase9.yaml`
- `cloud/storage/schema_phase9_coordination.sql`
