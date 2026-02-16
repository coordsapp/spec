# 11 - Phase 5 Warehouse Workflow (Logistics)

## Why this matters
Phase 5 is the logistics hero workflow that ties together ownership, verification, carrier sharing, and operations.

## End-to-end flow
1. Create warehouse (`POST /v1/warehouses`)
2. Create docks (`POST /v1/warehouses/{id}/docks`)
3. Verify docks on-site (`POST /v1/warehouses/{id}/docks/{dock_id}/verify`)
4. Issue carrier access (`POST /v1/warehouses/{id}/carrier-access`)
5. Track dock state (`/operations` arrive/depart APIs)

## Expected outcomes
- Carriers receive precise, verified arrival targets
- Dispatch and dock teams share a common spatial source of truth
- Resolver usage maps directly to live operational throughput
