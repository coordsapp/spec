# Feature 28 - Interactive Coordinate Converter

## Status
Built (Phase 7 implementation started February 16, 2026)

## What it does
Adds an end-user and developer-friendly coordinate conversion workflow that turns raw coordinates into Coords-native outputs and integration-ready snippets.

## Key behavior
- Single conversion endpoint:
1. validates coordinate ranges and altitude bounds
2. generates Coords L1 URI
3. returns suggested handles
4. returns GeoJSON + WKT formats
- Batch conversion endpoint:
1. accepts JSON items or CSV payload
2. processes mixed-validity rows
3. reports per-row success/failure
- Interactive converter UI:
1. manual coordinate entry
2. map click conversion via Leaflet/OpenStreetMap
3. code snippets (cURL/JavaScript/Python/Go)
4. copy-to-clipboard actions
5. batch CSV conversion runner
- Converter interactions emit onboarding analytics events.

## Primary routes
- `GET /tools/converter`
- `POST /v1/convert/coordinate`
- `POST /v1/convert/batch`

## Where implemented
- `cloud/internal/converter/service.go`
- `cloud/handlers/converter/handler.go`
- `cloud/handlers/web/handler.go`
- `cloud/cmd/resolver/main.go`
- `cloud/openapi/v1.yaml`
