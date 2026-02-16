# 16 - Phase 8 Open Source Map Platform

## Status
In Progress (started February 16, 2026)

## Why this matters
The map experience turns coords into a full spatial workflow surface where teams can search, inspect, and share operational locations without switching tools.

## New public routes
- `GET /map`
- `GET /v1/map/resolve`

## Map viewport request
```bash
curl "https://coords.up.railway.app/v1/map/resolve?bbox=-97.2,32.5,-96.1,33.1&layers=warehouses,docks,handles&limit=500"
```

## Handle search flow
1. Open `/map`
2. Enter a handle such as `@acme/warehouse-1/dock-2`
3. Resolve it via `GET /v1/resolve/{handle}`
4. Copy/share the generated URL state for teammates

## Layer controls
- `warehouses`: aggregated points from verified dock clusters
- `docks`: verified dock locations with warehouse context
- `handles`: verified public aliases inside viewport

## URL state parameters
- `lat`: map center latitude
- `lng`: map center longitude
- `z`: zoom level
- `q`: active handle search query
- `layers`: comma-separated layer list

## Where implemented
- `cloud/internal/mapview/service.go`
- `cloud/handlers/mapview/handler.go`
- `cloud/handlers/web/handler.go`
- `cloud/cmd/resolver/main.go`
- `cloud/openapi/v1.yaml`
