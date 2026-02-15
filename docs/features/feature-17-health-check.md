# Feature 17 - Health Check Endpoint

## Status
Built

## What it does
Provides a lightweight liveness endpoint for uptime checks and deployment validation.

## Endpoint
- `GET /healthz`

## Key behavior
- Returns service status payload for monitors
- Used by hosting platforms and uptime tools for quick health probes

## Where implemented
- `cloud/cmd/resolver/main.go`
