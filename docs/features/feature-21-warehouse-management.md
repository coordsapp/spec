# Feature 21 - Warehouse Management API

## Status
Built

## What it does
Introduces org-scoped warehouse entities with CRUD operations and canonical warehouse handle generation.

## Key behavior
- Warehouse lifecycle: active/inactive
- Org ownership and RBAC enforcement
- Timezone-aware warehouse metadata
- Deterministic warehouse handle generation
- Tier gating for business/enterprise orgs with active subscriptions
- Business-tier quota enforcement for warehouse count

## Primary endpoints
- `POST /v1/warehouses`
- `GET /v1/warehouses`
- `GET /v1/warehouses/{id}`
- `PATCH /v1/warehouses/{id}`
- `DELETE /v1/warehouses/{id}`

## Where implemented
- `cloud/internal/warehouse/service.go`
- `cloud/handlers/warehouses/warehouses.go`
- `cloud/cmd/resolver/main.go`
