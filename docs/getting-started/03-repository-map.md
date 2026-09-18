# 03 - Repository Map

## `coordsapp/spec`
Protocol and documentation source of truth:
- v1 format docs
- test vectors
- `docs/open-questions.md` — the numbered tracking doc for review findings
- no phase/feature docs — all of them (including the protocol-level ones: Phases 1, 10, 11; Features 1, 2, 3, 31) live in `cloud/docs/` instead, consolidated there 2026-09-18 (see OQ-002)

## `coordsapp/core`
Go CLI + public reference codec:
- `coords encode lat lng alt`
- `coords decode <uri>`
- Works offline
- Codec is a public package (`core/coords`, not `internal/`) so other modules — `cloud`, or external consumers like Landos/Landblock — can import it directly (see OQ-003)

## `coordsapp/cloud`
Hosted API and platform services:
- `/v1/resolve/{handle}`
- Auth, orgs, RBAC
- Alias claiming and verification
- Billing, domains, SLA/status
- Warehouse workflows (`/v1/warehouses/...`)
- Dock verification and operations (`/v1/warehouses/{id}/operations/...`)
- Map platform (`/map`, `/explore`, `/v1/map/resolve`)
- Active coordination runtime (`/v1/routing/plan`, `/v1/coordination/...`)
- `docs/phases/` and `docs/features/`: all phase/feature docs (Phases 1-11, Features 1-31), fully consolidated from `spec` on 2026-09-18
- L1 encoding delegates to `github.com/coordsapp/core/coords` (local `replace` dependency) rather than an independent copy

Key Phase 5 implementation paths:
- `cloud/internal/warehouse/service.go`
- `cloud/handlers/warehouses/`
- `cloud/storage/schema_phase5_warehouse.sql`

Key Phase 8 and Phase 9 implementation paths:
- `cloud/handlers/web/web_map_v2.go`
- `cloud/internal/mapview/service.go`
- `cloud/internal/coordination/`
- `cloud/handlers/coordination/`
- `cloud/storage/schema_phase9_coordination.sql`
