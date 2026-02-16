# Feature 29 - Open Source Map Platform

## Status
Completed (delivered February 16, 2026)

## What it does
Provides a coords-native map platform with a full workspace at `/map` and a classic explorer at `/explore`.

## Key behavior
- Map interface:
1. OpenStreetMap basemap with Leaflet rendering
2. handle search with resolver integration
3. click-to-convert lat/lng into L1 and suggested handles
4. shareable URL state for center/zoom/query/layers
5. compact bottom-right basemap toggle for streets/satellite/terrain
6. satellite mode includes roads and labels overlays
- Viewport data API:
1. `GET /v1/map/resolve` with bbox filtering
2. layer filtering (`warehouses`, `docks`, `handles`)
3. paging (`limit`, `offset`)
4. GeoJSON `FeatureCollection` response
- Instrumentation:
1. map views
2. viewport loads
3. layer toggles
4. handle searches
5. share-link interactions

## Primary routes
- `GET /map`
- `GET /explore`
- `GET /v1/map/resolve`

## Where implemented
- `cloud/internal/mapview/service.go`
- `cloud/handlers/mapview/handler.go`
- `cloud/handlers/web/web_map_v2.go`
- `cloud/handlers/web/web_map.go`
- `cloud/cmd/resolver/main.go`
- `cloud/openapi/v1.yaml`
