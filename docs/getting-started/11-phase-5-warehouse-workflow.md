# 11 - Phase 5 Warehouse Workflow (Logistics)

## Status
Completed (Verified on February 16, 2026)

## Why this matters
Phase 5 is the logistics hero workflow that ties together ownership, verification, carrier sharing, and operations.

## Prerequisites
- Org tier is `business` or `enterprise`
- Subscription status is active (`active`, `trialing`, or `past_due`)
- Authenticated org member with warehouse permissions

## End-to-end flow
1. Create warehouse (`POST /v1/warehouses`)
2. Create docks (`POST /v1/warehouses/{id}/docks`)
3. Verify docks on-site (`POST /v1/warehouses/{id}/docks/{dock_id}/verify`)
4. Issue carrier access (`POST /v1/warehouses/{id}/carrier-access`)
5. Track dock state (`/operations` arrive/depart APIs)

## Endpoint set
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

## Verified run snapshot
- Verified sequence executed successfully in production on February 16, 2026
- Example warehouse handle: `@phase5-e2e-1771215200/dallas-north-dc`
- Example dock handle: `@phase5-e2e-1771215200/dallas-north-dc/inbound-dock-1`
- Verified operation transition: `arrived` -> `departed`

## Expected outcomes
- Carriers receive precise, verified arrival targets
- Dispatch and dock teams share a common spatial source of truth
- Resolver usage maps directly to live operational throughput
