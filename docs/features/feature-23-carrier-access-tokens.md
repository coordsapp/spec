# Feature 23 - Carrier Access Tokens

## Status
Built

## What it does
Provides controlled third-party access for carriers to resolve dock handles without full org membership.

## Key behavior
- Warehouse-scoped carrier access entries
- Expiring access tokens for least-privilege access
- Revocation support via delete endpoint
- Access auditability for enterprise controls
- Business-tier token quota enforcement per warehouse

## Primary endpoints
- `POST /v1/warehouses/{id}/carrier-access`
- `GET /v1/warehouses/{id}/carrier-access`
- `DELETE /v1/warehouses/{id}/carrier-access/{access_id}`

## Where implemented
- `cloud/internal/warehouse/service.go`
- `cloud/handlers/warehouses/carrier_access.go`
- `cloud/storage/schema_phase5_warehouse.sql`
