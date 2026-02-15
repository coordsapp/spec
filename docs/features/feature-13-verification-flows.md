# Feature 13 - Verification Flows (Geofenced and Postal)

## Status
Built

## What it does
Verifies alias ownership through physical-location or postal proof before public trust elevation.

## Endpoint
- `POST /v1/aliases/{id}/verify`

## Verification methods
- `geofenced` (distance/proximity checks)
- `postal` (verification code flow)

## Key behavior
- Moves claim status to verified on successful proof
- Rejects failed verification attempts with explicit errors
- Supports anti-squatting, trust, and ownership integrity

## Where implemented
- `cloud/internal/phase3/`
- `cloud/storage/schema_phase3.sql`
