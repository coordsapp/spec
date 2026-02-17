# API Contract Synchronization

## Overview

This document ensures API contracts between cloud backend and frontends stay aligned.

## Canonical Endpoints (v1-phase9.yaml)

| Endpoint | Method | Auth | Purpose |
|----------|--------|------|----------|
| `/v1/routing/plan` | POST | Required | Plan route with waypoints |
| `/v1/coordination/assign-dock` | POST | Required | Auto-assign best dock |
| `/v1/coordination/docks/{id}/status` | GET | Required | Real-time dock state |
| `/v1/notifications/arrival-alert` | POST | Required | Queue notifications |
| `/v1/analytics/sla-compliance` | GET | Required | SLA rollup |

## Request/Response Contracts

### POST /v1/routing/plan

**Request:**
```typescript
interface RoutePlanRequest {
  origin: string;           // Handle or "lat,lng"
  destination: string;      // Handle or "lat,lng"
  stops?: string[];         // Optional intermediate waypoints (max 25)
  vehicle_type?: 'truck' | 'van' | 'foot';  // Default: 'truck'
}
```

**Response:**
```typescript
interface RoutePlanResponse {
  vehicle_type: string;
  waypoints: RouteWaypoint[];
  legs: RouteLeg[];
  total_distance_meters: number;
  total_eta_seconds: number;
  planned_at: string;  // ISO 8601
}

interface RouteWaypoint {
  handle: string;
  lat: number;
  lng: number;
  source: 'alias' | 'literal' | 'geocoded';
}

interface RouteLeg {
  from: string;
  to: string;
  distance_meters: number;
  eta_seconds: number;
}
```

### POST /v1/coordination/assign-dock

**Request:**
```typescript
interface AssignDockRequest {
  warehouse_id: string;     // UUID
  carrier_name?: string;
  carrier_ref?: string;
  vehicle_type?: 'truck' | 'van' | 'foot';
  planned_arrival_at?: string;  // ISO 8601
  note?: string;
}
```

**Response (201):**
```typescript
interface DockAssignment {
  id: string;
  org_id: string;
  warehouse_id: string;
  dock_id: string;
  dock_handle: string;
  dock_name: string;
  carrier_name: string;
  carrier_ref?: string;
  vehicle_type: string;
  status: 'assigned' | 'arrived' | 'completed' | 'cancelled';
  note?: string;
  planned_arrival_at?: string;
  assigned_at: string;
  updated_at: string;
}
```

**Error (409):**
```json
{"error": "conflict"}
```

### GET /v1/coordination/docks/{id}/status

**Response:**
```typescript
interface DockStatus {
  dock_id: string;
  warehouse_id: string;
  dock_handle: string;
  dock_name: string;
  verification_status: string;
  state: 'available' | 'occupied' | 'cleaning' | 'unavailable' | 'assigned';
  current_operation_id?: string;
  current_carrier_name?: string;
  current_trailer_ref?: string;
  arrived_at?: string;
  last_departed_at?: string;
  active_assignment_id?: string;
  active_assignment_carrier?: string;
  updated_at: string;
}
```

### POST /v1/notifications/arrival-alert

**Request:**
```typescript
interface ArrivalAlertRequest {
  warehouse_id: string;     // UUID
  dock_id: string;          // UUID
  carrier_name?: string;
  carrier_ref?: string;
  eta_seconds?: number;
  channels?: ('sms' | 'email' | 'push')[];
  message?: string;
}
```

**Response (201):**
```typescript
interface ArrivalAlertResponse {
  notifications: NotificationDispatch[];
  count: number;
}

interface NotificationDispatch {
  id: string;
  channel: string;
  status: 'queued' | 'sent' | 'failed';
  message: string;
  scheduled_for?: string;
  created_at: string;
}
```

### GET /v1/analytics/sla-compliance

**Query Parameters:**
- `days` (int, default 30)
- `grace_minutes` (int, default 15)
- `limit` (int, default 50)
- `offset` (int, default 0)

**Response:**
```typescript
interface SLAComplianceSummary {
  items: SLAComplianceRecord[];
  days: number;
  grace_minutes: number;
  total_assignments: number;
  on_time_assignments: number;
  late_assignments: number;
  limit: number;
  offset: number;
}

interface SLAComplianceRecord {
  carrier_name: string;
  dock_id: string;
  dock_handle: string;
  total_assignments: number;
  on_time_assignments: number;
  late_assignments: number;
  on_time_rate: number;  // 0.0 - 1.0
  average_delay_sec: number;
}
```

## Frontend Implementation Notes

### React API Client

```typescript
// lib/api.ts
import axios from 'axios';

const api = axios.create({
  baseURL: process.env.REACT_APP_BACKEND_URL + '/api',
  withCredentials: true,
});

export const coordinationAPI = {
  planRoute: (data: RoutePlanRequest) => 
    api.post<RoutePlanResponse>('/v1/routing/plan', data),
  
  assignDock: (data: AssignDockRequest) => 
    api.post<DockAssignment>('/v1/coordination/assign-dock', data),
  
  getDockStatus: (dockId: string) => 
    api.get<DockStatus>(`/v1/coordination/docks/${dockId}/status`),
  
  sendArrivalAlert: (data: ArrivalAlertRequest) => 
    api.post<ArrivalAlertResponse>('/v1/notifications/arrival-alert', data),
  
  getSLACompliance: (params?: {
    days?: number;
    grace_minutes?: number;
    limit?: number;
    offset?: number;
  }) => api.get<SLAComplianceSummary>('/v1/analytics/sla-compliance', { params }),
};
```

### Error Handling

```typescript
try {
  const assignment = await coordinationAPI.assignDock({ warehouse_id: '...' });
} catch (err) {
  if (axios.isAxiosError(err)) {
    switch (err.response?.status) {
      case 401:
        // Redirect to login
        break;
      case 403:
        // Show permission denied
        break;
      case 409:
        // No available docks
        toast.error('No docks available. Please try again later.');
        break;
      default:
        toast.error('An error occurred');
    }
  }
}
```

## Breaking Change Protocol

When modifying API contracts:

1. **Update OpenAPI spec first** (`openapi/v1-phase9.yaml`)
2. **Version breaking changes** (e.g., `/v2/...`)
3. **Deprecate old endpoints** (6-month sunset)
4. **Notify frontend teams** before deployment
5. **Update this document**

## Testing Sync

Use the Postman collection for validation:
- `docs/phase9-smoke-tests.postman_collection.json`
- `docs/phase9-smoke-tests.postman_environment.json`

```bash
newman run docs/phase9-smoke-tests.postman_collection.json \
  -e docs/phase9-smoke-tests.postman_environment.json
```
