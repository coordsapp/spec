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
- Cross-check: the individual feature docs for this same work (`spec/docs/features/feature-16-billing-and-subscriptions.md`, `feature-19-custom-domain-support.md`, `feature-20-sla-monitoring-status.md`) all say `Status: Built` and accurately match the real code/endpoints. So the underlying Phase 4 work is genuinely done — it's specifically the roadmap-level `phase-04.md` summary (OQ-014) that never got updated, not the feature-level docs.

## OQ-016 — CORRECTED: Landblock is a real, live, actively-developed project — not a shelved whitepaper

- Status: Corrected 2026-09-14 — see notes. Was previously logged as "unlinked Word docs, zero code"; that was wrong.
- Notes: Brock confirmed: "landblock is here: https://landblock.app/ there are repos too. We work with governments on land registrations." Verified independently:
  - **Live site** (landblock.app): describes itself as a "Federation Protocol for Land Registries" — blockchain-based (Polygon PoS anchoring), DIDs + zero-knowledge proofs, DAO governance, "Pre-mainnet / Limited Preview" stage. Audience: governments, financial institutions, courts, jurisdictions. No specific government partnership named on the page itself.
  - **GitHub**: `landblock-dao/landblock-public` (org `landblock-dao`, created 2026-04-02). Description: "a cryptographic mirror of land records" that doesn't replace government authority — append-only, auditable record on Polygon, "Mirror Mode" lets registries publish proofs without workflow disruption. Status: **active development** — constitution ratified (v0.4.5), DAO governance live on the Amoy testnet, currently building subgraph indexing + a "Federation Liaison Service," with a **Peru pilot planned** (roadmap Phase 7). 25+ commits on main. Blocked from reading file contents directly via `get_file_contents` — same GitHub org PAT policy as OQ-013 — this came from a page fetch, not the API, so treat repo internals as unverified until a proper token is available.
  - **Coords dependency**: the live repo's roadmap lists "Full governance + CoordsApp integration" as a **Phase 8 (future)** item — meaning Landblock does not consume Coords today; it's planned. This is a different relationship than the local whitepaper draft implied (which described Coords as the current "spatial spine").
  - This is one of potentially several independent downstream consumers — see OQ-020 (Landos, now also confirmed real). See OQ-021 for the physical file-location mismatch, and OQ-023 for a real discrepancy between the local whitepaper drafts and what's actually live now.

## OQ-017 — Landblock's adoption-phase numbering: local whitepaper vs. live project no longer clearly the same model

- Status: Open — needs reconciliation, not just renaming
- Notes: The local `Landblock_Whitepaper_v0.1.docx` (in `cloud/docs/`) defines "Phase 1: Observation → Phase 2: Shadow Registry → Phase 3: Operational Use → Phase 4: Legal Elevation." The **live** `landblock-dao/landblock-public` repo's own roadmap uses a different phase scheme entirely (at least 8 phases, ending in "Full governance + CoordsApp integration" at Phase 8, with a Peru pilot at Phase 7) and frames the project around DAO constitution ratification and Polygon anchoring rather than the Observation/Shadow Registry/Operational Use/Legal Elevation stages. These read as two different roadmaps, not the same one renamed. The earlier fix proposed here (rename to "Stage L1-L4" to avoid colliding with Coords Cloud's engineering Phase 1-9) still stands and doesn't collide with anything on the live site, but it may now be moot/stale if the local whitepaper draft is simply an older version superseded by what's live. Worth confirming with Brock which document is authoritative before editing either.

## OQ-018 — Landblock's organizational separation: already real on Landblock's side: revisit what (if anything) is still needed on the Coords side

- Status: Partially resolved — Landblock itself is already fully independent; remaining question is about the local draft materials
- Notes: Landblock already has its own org (`landblock-dao`), its own DAO governance/constitution, its own domain (landblock.app), and its own GitHub repo — it is not structurally coupled to `Coords, Inc.` or the `cloud` repo in any way on Landblock's side. The original concern (Landblock nested inside the proprietary Coords entity) doesn't apply to the real, live Landblock. What's left: the **local** guarantee-contract docs + whitepaper draft sitting in `cloud/docs/` (see OQ-021) are Coords-side artifacts describing an older/different vision of the relationship, and should probably either be updated to reflect the real, current Landblock, moved out of `cloud/docs/` as historical/reference material, or removed if superseded.

## OQ-020 — CONFIRMED: "Landos" is Brock's own project, already naming Coords as its land identifier

- Status: Confirmed 2026-09-14 — Brock: "landos is my project too"
- Notes: Found via the GitHub org `Landos-Foundation` (repos: `spec` — CC0 protocol spec, pushed as recently as 2026-09-13; `community`; `notes`). `Landos-Foundation/community`'s whitepaper (`landos-whitepaper-v0.1.1.md`, dated 2026-06-05, Status: Draft) describes **Landos: A Sovereign Land Ownership Protocol** — a Cosmos SDK / Tendermint BFT blockchain with its own token (Landos Equity Token, LOS), a "Proof of Land" consensus model weighted by proof-of-habitation, and a five-mechanism ownership-validation scheme (neighbor quorum, AR boundary walking, delegated vouching, community memory, staged entry). Not the same project as Landblock — different org, different chain (Cosmos vs. Polygon), different token, different governance model, no DAO-constitution language, first deployment region named as Ghana rather than Peru. Roadmap status: "Landos is in active design phase. No network exists yet" (Phase 1 of 4, pre-testnet).
  - So Brock is now confirmed to be personally behind (at least) three related-but-separate projects: Coords App (the standard itself), Landblock, and Landos — plus whatever "and others" from the original directive still refers to.
  - Since Landos is Brock's own project rather than an unaffiliated third party, the "open standard, multiple independent consumers" test isn't proven by an outside adopter yet — but the discipline still matters, because Landos's own whitepaper already treats Coords as a stable external dependency (section 3.3: "identified by a Coords URI... defined by the Coords protocol (github.com/coordsapp)," plus a "Coords XREF System" mapping other geo-ID formats onto it). If `spec`/`core` change in ways that break that assumption, it breaks Brock's own downstream project first. OQ-002/OQ-003/OQ-022 still stand.

## OQ-021 — Landblock's source docs are physically nested inside the `cloud` repo

- Status: Open — Brock chose to leave files in place for now, revisit later
- Notes: The 4 guarantee-contract docx files + whitepaper sit in `C:\coordsapp\cloud\docs\`, i.e. inside the proprietary Coords Cloud repo, which directly contradicts "Landblock is a separate project that needs to move independently" (OQ-016, OQ-018). Options discussed: a new sibling folder (`C:\landblock\`) fully outside `coordsapp`, or a new top-level folder inside the same parent workspace (`C:\coordsapp\landblock\`) but still its own repo. Deferred — no files moved yet.

## OQ-022 — Principle: `spec`/`core` need to stay generic enough for multiple independent consumers

- Status: Open — direction stated, not yet enforced
- Notes: Brock's stated goal: Coords should be built and planned so it's usable by "a lot of different projects like landos, landblock and others" — not just the `cloud` SaaS. That means `spec` (protocol) and `core` (reference codec) need to stay strictly neutral: no consumer-specific business logic, branding, or internal planning docs. This directly motivates fixing two things already tracked: OQ-002 (internal `cloud`/business content currently sitting in the public `spec` repo — the opposite of neutral) and OQ-003 (`cloud` should import `core`'s codec directly instead of maintaining its own parallel copy — right now even Coords' own commercial consumer doesn't actually build on the shared reference implementation, which undercuts the "one open standard, many consumers" model before a single external consumer has even tried).
- Update 2026-09-14: this is no longer purely aspirational. Landos (OQ-020) already references `github.com/coordsapp` directly in its own public whitepaper and defines a "Coords XREF System" mapping other geo-ID systems onto Coords URIs — real external design-time dependency, ahead of anything `cloud` itself does with `core`. That raises the stakes on OQ-002/OQ-003: cleanup that was "good hygiene" for an internal repo is now also about not breaking (or embarrassing the project in front of) a real outside adopter.

## OQ-023 — Local Landblock whitepaper drafts describe a different architecture than the live Landblock project

- Status: Open — needs confirmation from Brock on which is current
- Notes: The local docx drafts in `cloud/docs/` (Explainer, 3 Guarantee Contracts, Reference Schema, `Landblock_Whitepaper_v0.1`) describe Landblock as a non-blockchain system: Coords App + Parcel Registry + Authority Registry + Evidence Store + Dispute Registry, with Coords as the current "spatial spine" dependency — no blockchain, no Polygon, no DAO, no token anywhere in that text. The **live** landblock.app site and `landblock-dao/landblock-public` repo describe a blockchain-first system: Polygon PoS anchoring, DAO constitution (v0.4.5), DIDs + zero-knowledge proofs, Amoy testnet governance — with Coords appearing only as a future Phase 8 integration target, not a current dependency. These aren't small wording differences — they're two different technical architectures for what's nominally the same project name. Possibilities: (a) the local docs are an early v0.1 draft that was superseded by a pivot to the blockchain/DAO model, (b) the local docs describe a different, Coords-specific sub-component that still applies alongside the blockchain layer, or (c) the local docs are stale and should be archived/removed. Don't guess — ask Brock which is authoritative before touching either.

## OQ-024 — GitHub org PAT policy also blocks reading `landblock-dao` and may block others

- Status: Open
- Notes: Same restriction as OQ-013 (fine-grained PAT lifetime > 366 days rejected) also blocks `landblock-dao` — confirmed when `get_file_contents` on `landblock-dao/landblock-public` failed with the identical error. Everything logged about that repo in OQ-016 came from a page fetch, not the API, so it's shallower and less verifiable than a direct repo read would be (no visibility into actual file contents, commit history, or issues). `Landos-Foundation`'s repos were readable normally — this seems to be a per-org policy some orgs set and others don't. Worth getting a compliant token if deeper verification of `landblock-dao` internals is ever needed.

## OQ-019 — No CI/automated test pipeline; phase-completion claims are self-asserted

- Status: Open
- Notes: None of `spec`, `core`, or `cloud` has a `.github/` (or other CI config) directory. There's real Go test coverage throughout `cloud` and `core` (`codec_test.go`, `jwt_test.go`, `rbac_test.go`, `webhook_test.go`, `service_test.go` in several packages, etc.), and manual QA artifacts exist (`cloud/docs/phase9-smoke-tests.md` + Postman collection, `cloud/docs/map-qa-checklist.md`), but nothing runs these automatically on push/PR. `phase-06.md` itself already flags this: "Full local `go test ./...` remains dependent on local Go toolchain availability." So the "Completed"/"verified in production" claims in the phase docs (specific dates, specific handles created) are self-reported in the docs themselves, not backed by any CI artifact. Not urgent, but worth having before this gets more contributors or more public exposure.
