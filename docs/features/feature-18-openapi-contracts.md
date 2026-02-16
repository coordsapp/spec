# Feature 18 - OpenAPI Contracts

## Status
Built

## What it does
Publishes machine-readable API contracts for resolver and ownership workflows.

## Contract files
- `cloud/openapi/v1.yaml`
- `cloud/openapi/v1-phase3.yaml`
- `cloud/openapi/v1-phase9.yaml`

## Key behavior
- Defines request/response schemas and status codes
- Keeps runtime behavior aligned with published API expectations
- Enables SDK/client generation and integration testing

## Current coverage note (as of February 16, 2026)
- `cloud/openapi/v1.yaml` covers resolver/status endpoints
- `cloud/openapi/v1-phase3.yaml` covers phase 3 alias ownership flows
- `cloud/openapi/v1-phase9.yaml` covers coordination/routing endpoints
- Phase 5 warehouse/dock/carrier/operations endpoints are implemented in runtime and remain a follow-up OpenAPI coverage item
