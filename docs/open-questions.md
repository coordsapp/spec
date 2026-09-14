# Open Questions

Tracking doc for items surfaced during review, not yet worked on. Each item has an ID, status, and notes.

## OQ-001 — NaN/Infinity bypass boundary validation in `core` codec

- Status: Open
- Notes: `core/internal/coords/codec.go`'s `validateBounds` uses `if lat < minLat || lat > maxLat`. Under IEEE 754, comparisons against `NaN` are always `false`, so `NaN`/`Inf` values pass validation unrejected. `strconv.ParseFloat` parses the literal strings `"NaN"`, `"Inf"`, `"+Inf"`, `"-Inf"` as valid floats, so a crafted URI can round-trip through `Encode`/`Decode` as if it were a real location. This is the actual protocol reference implementation, so it affects any implementation modeled on it. Fix: rewrite the checks as accept-based (`if !(lat >= minLat && lat <= maxLat)`) or add explicit `math.IsNaN`/`math.IsInf` guards, and add a negative test vector to `spec/v1/test-vectors.md`.

## OQ-002 — Public `spec` repo contains internal/proprietary material

- Status: Open
- Notes: `spec/docs/agents-instructions/from-agent10-2-17-26.md` is an internal engineering memo (names an internal team "Bridgeflow Group," an internal role `bridgeflow_employee`, UI/theming directives for the closed-source product) rather than protocol content. `spec/docs/phases/` and `spec/docs/features/` also read as the full proprietary product roadmap rather than protocol docs. If this repo is public/CC0, this content undercuts the "neutral standard" positioning. If already pushed to GitHub, deleting the file isn't enough — needs purging from git history.

## OQ-003 — `cloud` maintains an independent, less-validated copy of the codec

- Status: Open
- Notes: `cloud/internal/resolver/l1.go` (`EncodeL1`) reimplements the checksum/formatting logic independently of `core` — `cloud/go.mod` has no dependency on `core`. It skips bounds validation entirely (not even the buggy version from OQ-001 — none at all). The Postgres schema backs this up: `aliases.lat`/`lng` have `CHECK` constraints but `default_altitude` doesn't. A bad altitude can reach the DB and get served as a `coords:` URI with no validation at any layer. Fix: have `cloud` import `core`'s codec package directly instead of maintaining a parallel copy.

## OQ-004 — SLA summary endpoint triggers full-platform aggregation as a side effect

- Status: Open
- Notes: `sla.Service.GetSummary` (an authenticated per-org "view my SLA" endpoint) calls `AggregateSLA(ctx, now)` synchronously if this month's `sla_periods` row doesn't exist yet. `AggregateSLA` loops over every eligible org platform-wide, not just the requester. There's already a background worker (`isla.NewAggregator`) doing this on a schedule. A single customer's first dashboard view each month can trigger a full cross-tenant computation pass inline in the request path. Fix: scope the lazy-aggregation fallback to just the requesting org, or drop it and rely solely on the background worker.

## OQ-005 — `JWT_SECRET` silently falls back to a hardcoded dev secret

- Status: Open
- Notes: `cmd/resolver/main.go` does `envOrDefault("JWT_SECRET", "dev-insecure-secret-change-me")`. A misconfigured production deploy that forgets to set `JWT_SECRET` would silently issue tokens signed with a known, public default instead of failing to start. Fix: hard-fail startup in production if `JWT_SECRET` is unset (or unset and `ENV=production`).

## OQ-006 — Custom-domain TLS provisioning is a no-op stub

- Status: Open
- Notes: `domains/tls.go`'s `NoopTLSManager.EnsureCertificate` does nothing. Cert provisioning for verified custom domains isn't actually implemented, so "verified custom domain" HTTPS support is incomplete relative to what the README/feature docs imply.

## OQ-007 — Carrier access tokens visible to viewer-role org members

- Status: Open
- Notes: `ListCarrierAccess` returns `CarrierAccess.AccessToken` (a live bearer credential for external carriers) in full, unmasked. Any org member with `view_warehouses` — including the lowest `viewer` role — can read every active carrier token for the org, not just admins/creators. Decide whether viewers should see live credentials at all, or only masked/redacted values.

## OQ-008 — Rate limiter won't hold across multiple replicas

- Status: Open
- Notes: `internal/ratelimit/limiter.go` is in-memory, per-process, fixed-window. Fine at `numReplicas = 1` (current `railway.toml`), but breaks down once the service scales horizontally — no shared state across instances. Needs a shared store (Redis, Postgres-backed counter, etc.) before scaling out.

## OQ-009 — Railway-specific config to migrate off

- Status: Open
- Notes: Moving off Railway. Currently baked in: `cloud/railway.toml` (whole file); `cloud/README.md`'s "Railway deploy" section (CLI steps + a migration curl example pointed at `coords.up.railway.app`); `cloud/.env.example`'s three `BILLING_*_URL` vars defaulting to `https://coords.up.railway.app`; `cloud/cmd/resolver/main.go`'s matching hardcoded Go fallback defaults for the same three URLs. Dockerfile is generic and doesn't need to change.

## OQ-010 — Inconsistent legal entity name across licenses/docs

- Status: Open
- Notes: MIT license (`core`) says "coordsapp," proprietary license (`cloud`) says "Coords, Inc.," internal docs say "Bridgeflow Group." Worth settling on one legal name before more public exposure.

## OQ-011 — Hardcoded `valid_until` cliff date

- Status: Open
- Notes: `aliases.valid_until` defaults to a literal `'2030-01-01 00:00:00+00'` in `storage/schema.sql`. Fine for now, but it's a ticking hardcoded expiration sitting in the schema rather than a computed/configurable default.

## OQ-012 — Crude public status severity heuristic

- Status: Open
- Notes: `sla.GetPublicStatus` sets status to `degraded` at exactly 1 open incident and `major_outage` at 2+, regardless of check criticality. One flapping non-critical check reads the same as two unrelated real outages. Consider weighting by check importance or duration.

## OQ-013 — GitHub token blocked by org conditional access policy

- Status: Open
- Notes: The `coordsapp` GitHub org blocks the connected fine-grained PAT because its lifetime exceeds 366 days. Repos/issues/PRs under that org can't be read through this token as configured. Needs a shorter-lived token to restore access.

## OQ-014 — Phase 4 doc contradicts itself on completion status

- Status: Open
- Notes: `spec/docs/phases/README.md` lists "Phase 4 - Enterprise Features and Scale" as `Completed`, but `phase-04.md`'s own `## Status` field says `Planned`. The body reads like a forward-looking plan (week-by-week execution plan, aspirational "Success Metrics," an "Outcome Target" instead of an "Outcome") with none of the "Delivered"/"Live Validation" evidence sections every other phase doc has. The underlying features (billing/Stripe, custom domains, SLA monitoring) do actually exist in the code, so this looks like the work shipped but the doc was never rewritten from plan-form to a real completion retrospective. Fix: either rewrite `phase-04.md` with real delivered/verification details and flip its own Status to match the index, or correct the index back to `Planned`/`In Progress` until that rewrite happens.

## OQ-015 — Phase 4's SLA promise and API surface don't match what shipped

- Status: Open
- Notes: `phase-04.md`'s pricing table promises the $29/mo "team" tier "99.5% SLA," and its "API Surface" list names `GET /v1/sla/status`. The actual implementation (`cloud/internal/sla/service.go`, confirmed by `cloud/README.md`) exposes `GET /v1/sla/summary` and `GET /v1/sla/periods`, both gated to `business`/`enterprise` tier only (`GET /v1/status/public` is the only unauthenticated one) — "team" isn't a recognized eligible tier anywhere in the SLA gating code. So the endpoint name drifted, and it's unclear whether "team" customers are meant to get an SLA credit/target without any dashboard visibility, or whether this is a real gap between the pricing promise and what was built. Worth confirming intent before this becomes a support/billing dispute.
