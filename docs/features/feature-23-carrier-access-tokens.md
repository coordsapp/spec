# Feature 23 - Carrier Access Tokens

## Status
Planned

## What it does
Provides controlled third-party access for carriers to resolve dock handles without full org membership.

## Key behavior
- Warehouse-scoped carrier access entries
- Expiring access tokens for least-privilege access
- Revocation support via delete endpoint
- Access auditability for enterprise controls

## Primary endpoints
- `POST /v1/warehouses/{id}/carrier-access`
- `GET /v1/warehouses/{id}/carrier-access`
- `DELETE /v1/warehouses/{id}/carrier-access/{access_id}`
