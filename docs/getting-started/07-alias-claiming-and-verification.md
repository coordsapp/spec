# 07 - Alias Claiming and Verification

## Flow
1. Create org / obtain token
2. Claim alias (`POST /v1/aliases`)
3. Verify alias (`POST /v1/aliases/{id}/verify`)
4. Resolve publicly (`GET /v1/resolve/{handle}`)

## Verification methods
- `geofenced`: client must be near claim coordinates
- `postal`: code-based verification

## Important rules
- Pending claims expire
- Ownership is org-scoped
- RBAC controls who can claim/update/release
