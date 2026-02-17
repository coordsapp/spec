# Cloud Coordination Service Instructions

## Overview

The Phase 9 coordination service (`internal/coordination/`) handles active logistics:
- Route planning with handle/coordinate waypoints
- Dock assignment and status tracking
- Arrival notifications
- SLA compliance analytics

## File Organization

```
internal/coordination/
├── service.go           # Types, errors, constructor (~180 lines)
├── service_dock.go      # AssignDock, GetDockStatus (~215 lines)
├── service_routing.go   # PlanRoute (~90 lines)
├── service_resolve.go   # Waypoint resolution
├── service_notifications.go # Arrival alerts
├── service_analytics.go # SLA compliance
├── service_scan.go      # Batch operations
└── service_utils.go     # Helpers
```

**Rule:** Keep each file under 700 lines. Split by concern if approaching limit.

## Dock State Machine

```
                    ┌─────────────┐
                    │  available  │
                    └──────┬──────┘
                           │ AssignDock()
                           ▼
                    ┌─────────────┐
                    │  assigned   │
                    └──────┬──────┘
                           │ Carrier arrives
                           ▼
                    ┌─────────────┐
                    │  occupied   │
                    └──────┬──────┘
                           │ Carrier departs
                           ▼
                    ┌─────────────┐
                    │  cleaning   │ (15 min grace)
                    └──────┬──────┘
                           │ Grace period ends
                           ▼
                    ┌─────────────┐
                    │  available  │
                    └─────────────┘

Exception: unavailable (if dock.status != 'verified')
```

## AssignDock Logic

```go
// 1. Find best available dock (transaction + FOR UPDATE lock)
SELECT d.id, d.handle, d.name
FROM docks d
JOIN warehouses w ON w.id = d.warehouse_id
WHERE d.warehouse_id = $warehouse_id
  AND w.org_id = $org_id
  AND d.status = 'verified'
  AND NOT EXISTS (active operation)
  AND NOT EXISTS (active assignment)
ORDER BY last_activity ASC NULLS FIRST
LIMIT 1
FOR UPDATE

// 2. Create assignment record
INSERT INTO coordination_assignments (...)

// 3. Return assignment with dock details
```

**Important:** Use `FOR UPDATE` to prevent race conditions.

## Route Planning

```go
func (s *Service) PlanRoute(ctx, orgID, input) (RoutePlan, error) {
    // 1. Resolve all waypoints (handles → coordinates)
    // 2. Calculate Haversine distance between consecutive points
    // 3. Estimate ETA based on vehicle type speed
    // 4. Return route plan with legs
}
```

**Speed defaults:**
- Truck: 60 km/h → 16.67 m/s
- Van: 50 km/h → 13.89 m/s
- Foot: 5 km/h → 1.39 m/s

## API Endpoints

| Endpoint | Method | Permission | Handler |
|----------|--------|------------|----------|
| `/v1/routing/plan` | POST | ViewWarehouses | `PlanRoute` |
| `/v1/coordination/assign-dock` | POST | ManageWarehouses | `AssignDock` |
| `/v1/coordination/docks/{id}/status` | GET | ViewWarehouses | `DockStatus` |
| `/v1/notifications/arrival-alert` | POST | ManageWarehouses | `ArrivalAlert` |
| `/v1/analytics/sla-compliance` | GET | ViewWarehouses | `SLACompliance` |

## Request/Response Examples

### POST /v1/routing/plan

```json
// Request
{
  "origin": "@carrier/truck-123",
  "destination": "@acme/warehouse/dock-1",
  "stops": ["@acme/checkpoint-a"],
  "vehicle_type": "truck"
}

// Response
{
  "vehicle_type": "truck",
  "waypoints": [
    {"handle": "@carrier/truck-123", "lat": 38.91, "lng": -77.04, "source": "alias"},
    {"handle": "@acme/checkpoint-a", "lat": 38.90, "lng": -77.03, "source": "alias"},
    {"handle": "@acme/warehouse/dock-1", "lat": 38.89, "lng": -77.02, "source": "alias"}
  ],
  "legs": [
    {"from": "@carrier/truck-123", "to": "@acme/checkpoint-a", "distance_meters": 1500, "eta_seconds": 90},
    {"from": "@acme/checkpoint-a", "to": "@acme/warehouse/dock-1", "distance_meters": 1200, "eta_seconds": 72}
  ],
  "total_distance_meters": 2700,
  "total_eta_seconds": 162,
  "planned_at": "2026-02-17T18:00:00Z"
}
```

### POST /v1/coordination/assign-dock

```json
// Request
{
  "warehouse_id": "uuid-here",
  "carrier_name": "FastFreight",
  "carrier_ref": "TRK-001",
  "vehicle_type": "truck",
  "planned_arrival_at": "2026-02-17T18:30:00Z"
}

// Response (201)
{
  "id": "assignment-uuid",
  "dock_id": "dock-uuid",
  "dock_handle": "@acme/warehouse/dock-3",
  "dock_name": "Dock 3",
  "carrier_name": "FastFreight",
  "status": "assigned",
  "assigned_at": "2026-02-17T18:00:00Z"
}

// Error (409) - No available dock
{"error": "conflict"}
```

## Testing Checklist

- [ ] AssignDock returns 409 when no docks available
- [ ] AssignDock prevents double-assignment (unique index)
- [ ] GetDockStatus returns correct state based on operations
- [ ] PlanRoute handles mix of handles and coordinates
- [ ] PlanRoute limits stops to 25 max
- [ ] SLA compliance calculates grace period correctly
