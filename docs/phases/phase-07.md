# Phase 7 - Interactive Coordinate Converter

## Status
Completed (delivered February 16, 2026)

## Objective
Provide a zero-friction path from raw latitude/longitude data to usable Coords artifacts so new users can experience value immediately.

## Goal
Enable end-to-end flow:
1. enter coordinates or click map
2. convert to Coords outputs
3. copy results and code snippets
4. optionally batch-convert CSV datasets

## Scope
- Conversion APIs:
1. `POST /v1/convert/coordinate`
2. `POST /v1/convert/batch`
- Interactive converter UI at `GET /tools/converter`
- Multi-format conversion outputs:
1. Coords L1 URI
2. suggested handles
3. GeoJSON feature
4. WKT point
- Batch conversion from JSON list or CSV payload
- Converter usage analytics via onboarding events

## Week 1 Implementation
- Add converter domain service:
1. coordinate validation (`lat`, `lng`, `alt`)
2. L1 generation through resolver encoding
3. suggested handle generation
4. GeoJSON/WKT generation
5. batch conversion and CSV parsing
- Add converter handlers and route wiring in resolver
- Add converter web experience (`/tools/converter`) with:
1. manual converter form
2. map click conversion (Leaflet + OpenStreetMap)
3. generated code snippets (cURL/JS/Python/Go)
4. copy actions for key outputs
5. batch CSV conversion panel
- Update OpenAPI and docs references for new converter endpoints

## Initial Route Set
- `GET /tools/converter`
- `POST /v1/convert/coordinate`
- `POST /v1/convert/batch`

## Operational Notes
- Converter backend is implemented in:
1. `cloud/internal/converter/service.go`
2. `cloud/handlers/converter/handler.go`
- Web converter experience is implemented in:
1. `cloud/handlers/web/handler.go`
- Route wiring is in:
1. `cloud/cmd/resolver/main.go`
- OpenAPI updates are in:
1. `cloud/openapi/v1.yaml`

## Success Metrics
- Time to first conversion < 30 seconds
- Converter-to-signup click path improves onboarding completion
- Batch conversion success rate > 95% for valid CSV inputs
