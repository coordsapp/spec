# Phase 3 - Alias Claiming and Verified Ownership

## Status
Completed (live and verified)

## Objective
Allow organizations to claim and verify aliases (for example `@acme/warehouse1`) with anti-squatting controls and org ownership.

## Scope
- Organization creation and tier/quota model
- Alias claim lifecycle:
  - create claim
  - list aliases
  - update alias metadata/altitude
  - release alias
- Verification flows:
  - geofenced verification
  - postal code verification
- Resolver enrichment with ownership metadata

## API Contract
Phase 3 contract is documented in:
- `openapi/v1-phase3.yaml`

## Delivered
- JWT issuance and validation (`/v1/auth/signup`, `/v1/auth/token`)
- RBAC middleware (`admin`, `member`, `viewer`)
- Org-scoped alias handlers:
  - `POST /v1/aliases`
  - `GET /v1/aliases`
  - `PATCH /v1/aliases/{id}`
  - `DELETE /v1/aliases/{id}`
  - `POST /v1/aliases/{id}/verify`
- Quota checks at claim time (`aliases_used < aliases_quota`)
- Geofenced verification radius checks and postal verification code validation
- Ownership metadata in resolver responses (`claimed_by`, `verified_at`)

## Live Validation
- Org creation returns `201`
- Alias claim returns `202`
- Geofenced verification returns `200`
- Resolver returns verified ownership metadata
- Free-tier quota enforcement returns `409` on over-limit claims

## Outcome
Verified, organization-scoped alias ownership is publicly resolvable and enforceable in production.
