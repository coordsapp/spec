# 15 - Phase 7 Interactive Coordinate Converter

## Status
Completed (delivered February 16, 2026)

## Why this matters
The converter is the fastest way for new users to see Coords value. It removes setup friction and turns familiar lat/lng data into directly usable Coords outputs.

## New public routes
- `GET /tools/converter`
- `POST /v1/convert/coordinate`
- `POST /v1/convert/batch`

## Single conversion request
```bash
curl -X POST "https://coords.up.railway.app/v1/convert/coordinate" \
  -H "Content-Type: application/json" \
  -d '{"lat":32.7767,"lng":-96.7970,"alt":185.5,"label":"dallas north dock"}'
```

## Batch CSV request
```bash
curl -X POST "https://coords.up.railway.app/v1/convert/batch" \
  -H "Content-Type: application/json" \
  -d '{"csv":"lat,lng,alt,label\n32.7767,-96.7970,185.5,dallas\n37.7749,-122.4194,10.2,sf"}'
```

## Interactive flow
1. Open `/tools/converter`
2. Enter coordinates or click the map
3. Copy generated L1/handle outputs
4. Use snippets to integrate in app code
5. Use batch converter for migration datasets

## Expected output set
1. `l1` Coords URI
2. `suggested_handle`
3. `suggested_spot`
4. `geojson` feature
5. `wkt` point

## Where implemented
- `cloud/internal/converter/service.go`
- `cloud/handlers/converter/handler.go`
- `cloud/handlers/web/handler.go`
- `cloud/cmd/resolver/main.go`
- `cloud/openapi/v1.yaml`
