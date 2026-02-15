# Feature 05 - Altitude Override in Resolve

## Status
Built

## What it does
Allows clients to override default alias altitude at resolve time.

## Endpoint usage
- `GET /v1/resolve/{handle}?alt=<meters>`

## Key behavior
- Uses alias default altitude when `alt` is omitted
- Uses provided altitude when `alt` is present and valid
- Produces checksum-bound L1 URI for final altitude value

## Where implemented
- `cloud/cmd/resolver/main.go`
- `cloud/internal/resolver/`
