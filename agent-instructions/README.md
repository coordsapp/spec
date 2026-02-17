# Agent Instructions for Coords Development

This directory contains instructions for AI agents working on different parts of the Coords ecosystem.

## Repository Structure

| Repo | License | Purpose | Primary Agent |
|------|---------|---------|---------------|
| `spec` | CC0 | Open protocol specification | Any |
| `core` | MIT | Go reference implementation | Any |
| `cloud` | Private | Enterprise runtime (hosted) | Cloud agents |

## Instruction Files

- `cloud-coordination.md` - Phase 9 coordination service implementation
- `cloud-events.md` - Event discipline and audit logging
- `cloud-rbac.md` - Role-based access control patterns
- `cloud-sla.md` - SLA monitoring and breach detection
- `cloud-api-sync.md` - API contract alignment with frontends
- `protocol-compliance.md` - L1/L2 protocol implementation rules

## Key Principles

1. **Protocol is Truth**: The `spec` repo defines canonical behavior. All implementations must pass spec test vectors.

2. **Event Discipline**: Every state change emits an immutable, versioned, tenant-scoped event.

3. **File Size Limits**: Keep files under 700 lines (soft), 800 lines (hard).

4. **RBAC Enforcement**: All endpoints validate permissions via middleware.

5. **Tenant Isolation**: All queries must be scoped to `org_id`.

## Coordination Between Agents

When making changes that affect multiple repos:

1. Update `spec` first if protocol changes
2. Update `core` reference implementation
3. Update `cloud` enterprise features
4. Notify frontend agents of API changes
