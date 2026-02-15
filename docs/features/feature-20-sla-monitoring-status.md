# Feature 20 - SLA Monitoring and Public Status

## Status
Built

## What it does
Adds enterprise SLA monitoring with automatic uptime aggregation, incident tracking, credit eligibility, and a public status endpoint.

## Endpoints
- `GET /v1/sla/summary`
- `GET /v1/sla/periods`
- `GET /v1/status/public`

## Key behavior
- Background health checks record pass/fail results
- Incident lifecycle opens on failure and resolves on recovery
- SLA periods are aggregated for business/enterprise orgs
- Credit percentages are computed using a deterministic policy function
- Public status exposes current operational state and open incidents

## Where implemented
- `cloud/storage/schema_phase4_sla.sql`
- `cloud/internal/sla/`
- `cloud/handlers/sla/`
- `cloud/handlers/status/public.go`
- `cloud/cmd/resolver/main.go`
