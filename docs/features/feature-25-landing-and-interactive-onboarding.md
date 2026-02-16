# Feature 25 - Landing Experience and Interactive Onboarding

## Status
Built (Week 2 in progress as of February 16, 2026)

## What it does
Adds a product-facing web experience on top of the resolver service:
- conversion-focused landing page
- developer onboarding dashboard
- docs hub navigation
- sandbox and live API exploration

## Key behavior
- `GET /` serves modern landing HTML by default
- root JSON compatibility preserved through content negotiation and `format=json`
- `GET /app` provides guided tutorial steps for warehouse workflow
- in-browser API explorer supports endpoint presets and request editing
- generated code snippets in cURL, JavaScript, Python, and Go
- sandbox mode allows no-account, local-state trial workflow

## Primary routes
- `GET /`
- `GET /app`
- `GET /docs`
- `GET /docs/quickstart`
- `GET /docs/api-reference`
- `GET /docs/use-cases/logistics`
- `GET /docs/protocol`

## Week 2 workflow presets
- `POST /v1/auth/signup`
- `POST /v1/warehouses`
- `POST /v1/warehouses/{warehouse_id}/docks`
- `POST /v1/warehouses/{warehouse_id}/docks/{dock_id}/verify`
- `POST /v1/warehouses/{warehouse_id}/carrier-access`
- `POST /v1/warehouses/{warehouse_id}/operations/docks/{dock_id}/arrive`
- `POST /v1/warehouses/{warehouse_id}/operations/docks/{dock_id}/depart`
- `GET /v1/warehouses/{warehouse_id}/operations`

## Where implemented
- `cloud/handlers/web/handler.go`
- `cloud/cmd/resolver/main.go`
