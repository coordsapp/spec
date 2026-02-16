# Feature 11 - RBAC and Org Scoping

## Status
Built

## What it does
Enforces role-based permissions and organization boundaries for protected endpoints.

## Roles
- `admin`
- `member`
- `viewer`

## Key behavior
- Permission checks at middleware layer
- Org-scoped alias, billing, domain, SLA, and warehouse operations
- Blocks unauthorized role actions by endpoint
- Warehouse permissions added:
  - `manage_warehouses`
  - `view_warehouses`

## Where implemented
- `cloud/internal/auth/rbac.go`
- `cloud/internal/auth/middleware.go`
