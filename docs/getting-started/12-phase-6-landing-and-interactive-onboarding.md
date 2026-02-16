# 12 - Phase 6 Landing and Interactive Onboarding

## Status
In Progress (Week 2 active on February 16, 2026)

## Why this matters
Phase 6 improves first impression and onboarding conversion:
- visitors understand the product quickly
- developers can test workflows before account setup
- enterprise buyers get a clear upgrade and sales path

## Public web routes
- `GET /` landing page
- `GET /app` interactive onboarding dashboard
- `GET /docs`
- `GET /docs/quickstart`
- `GET /docs/api-reference`
- `GET /docs/use-cases/logistics`
- `GET /docs/protocol`

## JSON compatibility
Existing root integrations remain supported:
- `GET /?format=json`
- `GET /` with `Accept: application/json`

## Week 2 onboarding flow (`/app`)
Tutorial runner steps:
1. `POST /v1/auth/signup`
2. `POST /v1/warehouses`
3. `POST /v1/warehouses/{warehouse_id}/docks`
4. `POST /v1/warehouses/{warehouse_id}/docks/{dock_id}/verify`
5. `POST /v1/warehouses/{warehouse_id}/carrier-access`
6. `POST /v1/warehouses/{warehouse_id}/operations/docks/{dock_id}/arrive`
7. `POST /v1/warehouses/{warehouse_id}/operations/docks/{dock_id}/depart`
8. `GET /v1/warehouses/{warehouse_id}/operations`

## Sandbox mode behavior
- no account required
- local in-browser resource simulation
- generated token for auth-required endpoints
- local persistence via browser storage for progress/state

## Live mode behavior
- same explorer UI targets real endpoints
- user-provided bearer token is required for protected routes
- request/response payloads are shown inline for debugging

## Code snippet generation
Each request can be exported as:
1. cURL
2. JavaScript (`fetch`)
3. Python (`requests`)
4. Go (`net/http`)

## Where implemented
- `cloud/handlers/web/handler.go`
- `cloud/cmd/resolver/main.go`
