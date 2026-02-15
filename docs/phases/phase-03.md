# Phase 3 - Alias Claiming and Verified Ownership

## Status
Planned / API Contract Drafted

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

## Outcome Target
Verified, organization-scoped alias ownership that is publicly resolvable and auditable.
