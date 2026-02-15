# Phase 3 - Alias Claiming and Verified Ownership

## Status
In progress (API + schema + auth foundation implemented)

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

## Implemented Foundation
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

## Outcome Target
Verified, organization-scoped alias ownership that is publicly resolvable and auditable.
