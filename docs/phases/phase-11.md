# Phase 11 - Protocol Hardening and Standard Readiness

## Status
In Progress — items 1 and 2 done (2026-09-18); items 3 and 4 remain.

## Objective
Close the correctness, security, and trust gaps found during the September 2026 review before building further on top of Coords (CXS/Phase 10) or expecting more external projects to depend on it. Landos and Landblock already treat Coords as a stable foundation — this phase makes that assumption actually true.

## Goal
No new features. Every item here fixes something already shipped, so the protocol and its reference implementation can be trusted the way a real standard needs to be.

## Scope

1. **Fix NaN/Infinity bypassing bounds validation in `core`** (tracked as OQ-001) — **Done 2026-09-18**
   `core/internal/coords/codec.go`'s `validateBounds` used `<`/`>` comparisons, which are always `false` against `NaN` under IEEE 754 — so `NaN` values passed validation unrejected (Infinity was actually already caught, since `Inf > max`/`-Inf < min` both evaluate true). Fixed: rewrote as accept-based bounds checks plus explicit `math.IsNaN`/`math.IsInf` guards, added negative test vectors to `spec/v1/test-vectors.md`/`.json`, and made the finiteness requirement a normative rule in `spec/v1/boundaries.md` rather than leaving it as an implementation detail. Verified via full test suite before pushing.

2. **Unify the codec — `cloud` imports `core` instead of reimplementing it** (OQ-003) — **Done 2026-09-18**
   `cloud/internal/resolver/l1.go` reimplemented checksum/formatting independently, with no bounds validation at all — not even the buggy version from item 1. Fixed, with one prerequisite that wasn't scoped when this phase was written: `core`'s codec lived under `core/internal/coords`, and Go's `internal/` rule blocks any other module (`cloud` included) from ever importing it. Relocated it to a new public `core/coords` package first, then wired `cloud/go.mod` to depend on it via a local `replace` directive (`core` isn't tagged/published), rewrote `EncodeL1` to delegate to `core.Encode`, and propagated the now-possible error through `store.go` and `converter/service.go`. The `default_altitude` missing-`CHECK`-constraint gap this item mentioned is now moot for the encode path (validated before it ever becomes a URI), but the column itself still has no DB-level constraint — worth a follow-up if data can reach it through some other path.

3. **Remove internal/proprietary content from the public `spec` repo** (OQ-002)
   `spec/docs/agents-instructions/from-agent10-2-17-26.md` and the phase/feature planning docs read as internal `cloud` product material, not protocol content. Fix: move anything that isn't protocol-level into `cloud`'s own docs (or delete it), and if this has already been pushed publicly, purge it from git history, not just the working tree.

4. **Add CI** (OQ-019)
   None of `spec`, `core`, or `cloud` runs tests automatically. Real test coverage already exists (`codec_test.go`, `jwt_test.go`, `rbac_test.go`, `webhook_test.go`, etc.) — it's just never run on push/PR. Fix: a basic GitHub Actions workflow per repo (`go test ./...` at minimum) so "Completed"/"verified" status in the phase docs is backed by something automated, not self-reported.

## Explicitly Out of Scope
- CXS design (Phase 10) — stays a separate, parallel discussion track.
- New API surface, new endpoints, new product features.
- The Railway migration (OQ-009) and the other lower-severity items in `open-questions.md` (JWT secret fallback, TLS stub, rate limiter scaling, etc.) — real, but not blocking trust in the protocol itself. Candidates for a future phase if not folded in here later.

## Why this order
Items 1 and 2 are the actual correctness risk — a bad URI reaching production, or two implementations quietly disagreeing. Item 3 is a trust/positioning risk now that outside projects can read the public repo. Item 4 makes sure none of the first three regress silently later.

## Execution Plan
1. ~~Fix and test the `core` bounds-validation bug; add the negative test vector.~~ Done.
2. ~~Wire `cloud` to import `core`; delete `l1.go`'s duplicate logic.~~ Done (codec unified; the `default_altitude` CHECK constraint is a separate, still-open follow-up — not required for the encode-path fix itself).
3. Audit `spec` for anything non-protocol; relocate or delete; purge history if needed.
4. Add CI workflows to all three repos.

## Success Criteria
- ~~A crafted `coords:l1:v1:NaN,...` URI is rejected by both `core` and `cloud`.~~ Met — verified in an isolated test build (couldn't run directly on Brock's machine; `device_bash` was down).
- ~~`cloud` has zero independent codec logic — one implementation, one source of truth.~~ Met — `cloud/internal/resolver/l1.go` now delegates to `core.Encode`.
- `spec`'s public content is 100% protocol-level; nothing internal remains in the working tree or (if already pushed) in history.
- `go test ./...` runs automatically on every push/PR across all three repos, with results visible before merge.

## Cleanup Still Owed
- `core/internal/coords/` (the old private package) is dead code now that `core/coords/` exists. Delete `codec.go` and `codec_test.go` there once the new package is confirmed building locally.

See `docs/open-questions.md` for full detail and status on each numbered item.
