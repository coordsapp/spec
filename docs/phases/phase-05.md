# Phase 5 - Warehouse and Dock Management

## Status
Completed (Verified on February 16, 2026)

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

## Delivered Scope
- Warehouse CRUD with deterministic handle generation
- Dock CRUD with nested dock handles (`@org/warehouse/dock`)
- Dock verification endpoint with coordinate and accuracy capture
- Carrier access token create/list/revoke workflows
- Live dock operation lifecycle (`arrive` and `depart`)
- Org-scoped RBAC checks for manage/view warehouse workflows
- Tier and quota enforcement for business and enterprise plans
- Migration-backed schema for `warehouses`, `docks`, `carrier_access`, and `dock_operations`

## Tier Packaging
- `business`: up to 5 warehouses, 20 docks per warehouse, 10 carrier tokens
- `enterprise`: unlimited warehouses/docks/tokens, advanced operations support

## Verification Snapshot
- End-to-end flow verified in production on February 16, 2026
- Verified sequence:
  1. create warehouse
  2. create dock
  3. verify dock
  4. issue carrier access
  5. arrive and depart operation events
- Example verified handles:
  - `@phase5-e2e-1771215200/dallas-north-dc`
  - `@phase5-e2e-1771215200/dallas-north-dc/inbound-dock-1`
- Operations state transition verified: `arrived` -> `departed`

## Outcome Target
Coords becomes a mission-critical logistics workflow platform, not just a resolver utility.
