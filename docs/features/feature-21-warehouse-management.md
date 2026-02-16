# Feature 21 - Warehouse Management API

## Status
Planned

## What it does
Introduces org-scoped warehouse entities with CRUD operations and canonical warehouse handle generation.

## Key behavior
- Warehouse lifecycle: active/inactive
- Org ownership and RBAC enforcement
- Timezone-aware warehouse metadata
- Deterministic warehouse handle generation

## Primary endpoints
- `POST /v1/warehouses`
- `GET /v1/warehouses`
- `GET /v1/warehouses/{id}`
- `PATCH /v1/warehouses/{id}`
- `DELETE /v1/warehouses/{id}`
