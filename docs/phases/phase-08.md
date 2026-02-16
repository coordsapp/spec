# Phase 8 - Open Source Map Platform

## Status
Completed (delivered February 16, 2026)

## Objective
Add a professional map interface that makes coords handles and verified logistics data immediately actionable in-browser.

## Goal
Enable end-to-end flow:
1. open `/map`
2. search or click on map
3. load viewport overlays for warehouses, docks, and handles
4. share exact map context via URL

## Scope
- New map route:
1. `GET /map`
- New viewport API:
1. `GET /v1/map/resolve?bbox=minLng,minLat,maxLng,maxLat`
- Layer toggles for:
1. warehouses
2. docks
3. verified handles
- GeoJSON `FeatureCollection` response format with paging controls (`limit`, `offset`)
- Handle search and click-to-convert workflows integrated directly into map UX
- Map analytics events through existing onboarding instrumentation

## Week 1 Delivered
- Map backend service integrated into resolver runtime for Postgres mode:
1. bbox parsing and validation
2. layer filtering
3. viewport feature loading from warehouse/dock/alias records
- HTTP map handler created and routed:
1. `cloud/handlers/mapview/handler.go`
2. `/v1/map/resolve`
- `/map` page added with:
1. OpenStreetMap + Leaflet base map
2. coords handle search (`/v1/resolve/{handle}`)
3. click-to-convert (`/v1/convert/coordinate`)
4. live viewport overlay loading (`/v1/map/resolve`)
5. shareable URL state (`lat`, `lng`, `z`, `q`, `layers`)
- OpenAPI contract updated for `/v1/map/resolve`

## Operational Notes
- Backend implementation lives in:
1. `cloud/internal/mapview/service.go`
2. `cloud/handlers/mapview/handler.go`
- Web map implementation lives in:
1. `cloud/handlers/web/handler.go`
- Runtime wiring lives in:
1. `cloud/cmd/resolver/main.go`
- API contract lives in:
1. `cloud/openapi/v1.yaml`

## Success Metrics
- Median map load and first viewport overlay under 2 seconds in primary regions
- At least 25% of active users engage with `/map`
- Measurable map-to-claim/map-to-convert conversion events in onboarding analytics
