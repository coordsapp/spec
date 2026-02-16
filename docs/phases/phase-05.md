# Phase 5 - Warehouse and Dock Management

## Status
Planned

## Objective
Deliver a logistics-first workflow that makes Coords operationally central for warehouse teams and carrier networks.

## Goal
Enable end-to-end flow:
1. Create warehouse
2. Create docks
3. Verify docks on-site
4. Share handles with carriers
5. Track live dock operations

## Core Data Model
- `warehouses`: org-owned warehouse records and metadata
- `docks`: dock records, handles, capability metadata, and verification state
- `carrier_access`: scoped carrier tokens for controlled handle usage
- `dock_operations`: arrival/departure lifecycle events for live status

## API Surface
- `POST /v1/warehouses`
- `GET /v1/warehouses`
- `GET /v1/warehouses/{id}`
- `PATCH /v1/warehouses/{id}`
- `DELETE /v1/warehouses/{id}`
- `POST /v1/warehouses/{id}/docks`
- `GET /v1/warehouses/{id}/docks`
- `GET /v1/warehouses/{id}/docks/{dock_id}`
- `PATCH /v1/warehouses/{id}/docks/{dock_id}`
- `DELETE /v1/warehouses/{id}/docks/{dock_id}`
- `POST /v1/warehouses/{id}/docks/{dock_id}/verify`
- `POST /v1/warehouses/{id}/carrier-access`
- `GET /v1/warehouses/{id}/carrier-access`
- `DELETE /v1/warehouses/{id}/carrier-access/{access_id}`
- `GET /v1/warehouses/{id}/operations`
- `POST /v1/warehouses/{id}/operations/docks/{dock_id}/arrive`
- `POST /v1/warehouses/{id}/operations/docks/{dock_id}/depart`

## Execution Plan
1. Week 1: warehouse/dock schema and warehouse CRUD
2. Week 2: dock CRUD + geofenced dock verification
3. Week 3: carrier access token flows
4. Week 4: live operations dashboard APIs + workflow documentation

## Tier Packaging
- `business`: up to 5 warehouses, 20 docks per warehouse, 10 carrier tokens
- `enterprise`: unlimited warehouses/docks/tokens, advanced operations support

## Success Metrics
- 50+ warehouses created in first month
- >90% dock verification success rate
- 3+ carriers connected per active warehouse
- 80% of onboarded warehouses using operations endpoints daily

## Outcome Target
Coords becomes a mission-critical logistics workflow platform, not just a resolver utility.
