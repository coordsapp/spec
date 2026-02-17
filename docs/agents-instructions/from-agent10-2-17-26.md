📘 Agent Instructions: Coords Cloud & Runtime Alignment
Last Updated: February 18, 2026
Owner: Bridgeflow Group (Brock)
Status: ✅ Active | Phase: 9 (Coordination & Enterprise Runtime)
1. Protocol Alignment (Source of Truth)
Critical: The internal resolver logic in cloud/internal/resolver/l1.go is the canonical reference.
Format: v1|<lat>|<lng>|<alt> (Pipe-separated).
Precision: Lat/Lng (6 decimals), Altitude (2 decimals, Required).
URI Scheme: coords:l1:v1:%s,%s,%s*%s
Action: All agents (Python/Go/JS) must validate against this exact format before processing. No deviations allowed.
2. Database Schema Enhancements (Event Discipline)
The existing schema_phase9_coordination.sql is approved. Add the following to enforce immutability and audit trails:
sql
123456789101112131415
-- ADD: Immutable event log for audit trail (Bridgeflow Event Contract Spec)
CREATE TABLE IF NOT EXISTS coordination_events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    org_id UUID NOT NULL REFERENCES orgs(id) ON DELETE CASCADE,
    aggregate_type TEXT NOT NULL, -- 'dock', 'carrier', 'assignment'
    aggregate_id UUID NOT NULL,
    event_type TEXT NOT NULL, -- e.g., 'dock.status_changed', 'sla.breach'
    event_data JSONB NOT NULL,
    version INTEGER NOT NULL DEFAULT 1,
    created
3. RBAC Permission Matrix
Map backend permissions (internal/auth/middleware.go) to UI capabilities strictly:
Permission
Roles
UI Capability
ViewWarehouses
viewer, operator, admin
View map, docks, carriers (Read-Only)
ManageWarehouses
operator, admin
Assign docks, update status, trigger workflows
ManageBilling
admin
Access billing settings, upgrade tiers
ManageDomains
admin
Configure custom domains
SuperAdmin
bridgeflow_employee
Global visibility, tenant management
4. API Contract & Endpoint Alignment
Ensure frontend calls match the OpenAPI spec (openapi/v1-phase9.yaml).
Note: Python runtime endpoints should mirror these paths.
Endpoint
Method
Purpose
Status
/v1/routing/plan
POST
Plan route with handle/coord waypoints
✅ Aligned
/v1/coordination/assign-dock
POST
Auto-assign best available dock
✅ Aligned
/v1/coordination/docks/{id}/status
GET
Real-time dock state
⚠️ Check Path Param
/v1/notifications/arrival-alert
POST
Queue SMS/email/push alerts
✅ Aligned
/v1/analytics/sla-compliance
GET
SLA rollup by carrier/dock
✅ Aligned
5. Dock State Machine Logic
Enforce this deterministic workflow in both Go and Python services:
mermaid











Grace Period: 15 minutes default for Cleaning → Available.
Validation: Any transition failing L1 checksum or RBAC checks must halt and emit an error event.
6. SLA Compliance & Breach Detection
Calculation Logic:
Compare planned_arrival_at vs. actual_arrival_at.
Breach Threshold: NOW() > planned_arrival_at + grace_minutes.
Grouping: Analytics must group by carrier_name and dock_id.
Automated Worker Requirements:
Scan: Query assignments exceeding threshold.
Emit: Create sla.breach event in coordination_events.
Notify: Trigger notification abstraction (SMS/Email/Push).
Escalate: If unresolved after 
X
X minutes, escalate to org_admin.
7. Implementation Directives for Agents
A. Event Emission (Go & Python)
Every state change must emit an event. Example (Go):
go
123
func (s *Service) emitEvent(ctx context.Context, orgID, aggType, aggID, eventType string, data any) error {
    // Insert into coordination_events with user_sub from context
}
Python agents must replicate this pattern in FastAPI dependencies.
B. Frontend/Backend Sync
Map Workspace: Must reflect real-time coordination_events via WebSocket or polling.
Dark Theme: Enforced globally (Enterprise Command Center feel).
Mock Mode: VITE_MOCK_MODE must simulate realistic SLA breaches and dock turnovers for testing.
8. File Organization & Quality Gates
Line Limit: Max 800 lines/file. Refactor at 700.
Branching: Single main branch. No feature branches.
Testing: Integration tests require valid JWTs. Mock data must cover edge cases (e.g., simultaneous dock assignment).
🚀 Immediate Action Items for All Agents
Cloud Agents: Update schema_phase9_coordination.sql with the coordination_events table.
Python Agents: Verify /api/coordination/docks/{id} matches the v1 spec path exactly.
Frontend Agents: Ensure the "95.5% SLA" metric is calculated dynamically from the event log, not hardcoded.
Security Agents: Audit l1.go and Python equivalent to ensure altitude is required and precision is fixed.
Save this file to C:\coordsapp\spec\docs\agents-instructions\