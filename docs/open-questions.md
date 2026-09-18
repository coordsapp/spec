# Open Questions

Tracking doc for items surfaced during review, not yet worked on. Each item has an ID, status, and notes.

## OQ-001 — NaN/Infinity bypass boundary validation in `core` codec

- Status: Fixed 2026-09-18
- Notes: `core/internal/coords/codec.go`'s `validateBounds` used `if lat < minLat || lat > maxLat`. Under IEEE 754, comparisons against `NaN` are always `false`, so `NaN` values passed validation unrejected (Infinity was actually already caught by the old reject-based check, since `Inf > maxLat` and `-Inf < minLat` both evaluate true — the real gap was NaN specifically). `strconv.ParseFloat` parses the literal strings `"NaN"`, `"Inf"`, `"+Inf"`, `"-Inf"` as valid floats, so a crafted URI could round-trip through `Encode`/`Decode` as if it were a real location. Fix applied: `validateBounds` now rewritten as accept-based (`!(lat >= minLat && lat <= maxLat)`) plus explicit `math.IsNaN`/`math.IsInf` guards for both belt-and-suspenders clarity and defense against a future change to the bounds logic. Added `TestEncodeRejectsNaNAndInfinity` plus NaN/Infinity cases in `TestDecodeRejectsInvalidValues` to `core/internal/coords/codec_test.go`, and negative vectors to `spec/v1/test-vectors.md` and `spec/v1/test-vectors.json`. Verified passing (full `go test ./...` for this package) before pushing. Not yet verified against `cloud`'s independent codec copy — see OQ-003, which is the very next Phase 11 item and would eliminate this class of bug there too by having `cloud` import `core` directly instead of maintaining its own unvalidated copy.

## OQ-002 — Public `spec` repo contains internal/proprietary material

- Status: Fixed 2026-09-18 (working tree); git-history purge still open if this repo has already been pushed publicly
- Notes: Two separate issues were bundled in the original note:
  1. **`spec/docs/agents-instructions/from-agent10-2-17-26.md`** — an internal engineering memo (names the internal "Bridgeflow Group" team, an internal `bridgeflow_employee` role, frontend theming directives like "Dark Theme: Enforced globally," `VITE_MOCK_MODE` test setup) with zero protocol content. **Fixed**: copied verbatim (plus a relocation note) to `cloud/docs/agent-instructions-phase9-2026-02-17.md`; the old `spec/docs/agents-instructions/` folder has been deleted.
  2. **`spec/docs/phases/` and `spec/docs/features/`** — the complete engineering roadmap for the hosted Coords Cloud product (endpoint lists, Stripe/billing details, tier pricing, warehouse/logistics business logic, week-by-week delivery notes) was sitting inside a repo whose own `README.md` describes itself as just "Open protocol spec for Coords - CC0 public domain." Brock's direction: move anything cloud-related to `cloud/docs`. First pass split by content — Phases 2-9 and Features 4-30 (Coords Cloud product-build material) moved to `cloud/docs/`, while Phases 1, 10, 11 and Features 1, 2, 3, 31 (judged genuinely protocol/standards-level) stayed in `spec`. **Brock then overrode that split**: he uses these phase/feature docs from `cloud`, not `spec`, regardless of protocol-relevance, so all of it belongs in one place. **Fully consolidated 2026-09-18**: the remaining 7 files (`phase-01.md`, `phase-10.md`, `phase-11.md`, `feature-01-protocol-v1.md`, `feature-02-l1-uri-checksum.md`, `feature-03-cli-offline-encode-decode.md`, `feature-31-geodetic-and-interoperability-standards.md`) moved to `cloud/docs/phases/` and `cloud/docs/features/`, fixing their internal cross-references to `docs/open-questions.md` (now `spec/docs/open-questions.md`, since that tracker stays in `spec`) and to each other (`feature-31.md`'s reference to `phase-10.md` now points at `cloud/docs/phases/phase-10.md`). `cloud/docs/phases/README.md` and `cloud/docs/features/README.md` are now complete, unified indexes (all 11 phases, all 31 features) with no more spec/cloud split caveat. `spec/docs/phases/` and `spec/docs/features/` have been deleted entirely — `spec` now holds zero phase/feature docs, only `spec/docs/open-questions.md` and `spec/docs/getting-started/`. Updated the stale path references this created in OQ-014/OQ-015 (already pointed at `cloud/docs/` from the first pass) and in `spec/docs/getting-started/03-repository-map.md`.
  - **Leftover**: if `spec` has already been pushed publicly with any of this in it at an earlier commit, deleting the working-tree copies isn't enough on its own — it would still need purging from git history to actually be gone from a public repo.

## OQ-003 — `cloud` maintains an independent, less-validated copy of the codec

- Status: Fixed 2026-09-18
- Notes: `cloud/internal/resolver/l1.go` (`EncodeL1`) reimplemented the checksum/formatting logic independently of `core` — `cloud/go.mod` had no dependency on `core`. It skipped bounds validation entirely (not even the buggy version from OQ-001 — none at all). The Postgres schema backs this up: `aliases.lat`/`lng` have `CHECK` constraints but `default_altitude` doesn't, so a bad altitude could reach the DB and get served as a `coords:` URI with no validation at any layer.
- Fix applied: found a prerequisite that wasn't scoped when this was originally logged — `core`'s codec lived entirely under `core/internal/coords`, and Go's `internal/` import rule means no other module can ever import it, `cloud` included. So the fix also relocated the codec to a new public `core/coords` package (updating `core/cmd/coords/main.go`'s import to match) before `cloud` could depend on it at all. `cloud/go.mod` now has `require github.com/coordsapp/core ...` plus `replace github.com/coordsapp/core => ../core` (a local relative-path replace, since `core` isn't tagged/published — standard approach for this kind of monorepo-adjacent sibling layout). `cloud/internal/resolver/l1.go`'s `EncodeL1` now delegates directly to `core.Encode`, and its signature changed from `(string)` to `(string, error)` since it can now actually fail; propagated that error through `store.go`'s `fromRecord` (used by both `MemoryStore` and `PostgresStore`) and `converter/service.go`'s `Convert`. Verified in an isolated sandbox build (couldn't run this on Brock's machine directly — `device_bash` is still down there): both modules build clean, `go vet` passes, and every existing test — including the exact checksum-string assertions in `resolver/store_test.go` (`TestLookup`, `TestLookupWithAltitudeOverride`) — still passes with byte-identical output, confirming the codec swap doesn't change any encoded value, only adds real validation.
- Leftover: `core/internal/coords/` (the old private package) is now dead code, superseded by `core/coords/`. I can't delete files on Brock's device right now (`device_bash` down) — he should delete `core/internal/coords/codec.go` and `codec_test.go` once he's confirmed the new `core/coords` package builds on his machine. Also worth noting for OQ-022: `core/coords` being public now means Landos or Landblock could in principle import Coords' actual reference codec directly instead of reimplementing it themselves — hadn't been possible before this fix.

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
- Notes: (Path update 2026-09-18: `phase-04.md` and the feature docs referenced below moved to `cloud/docs/` as part of OQ-002 — the roadmap-level self-contradiction described here is unaffected by the move.) `phases/README.md` lists "Phase 4 - Enterprise Features and Scale" as `Completed`, but `phase-04.md`'s own `## Status` field says `Planned`. The body reads like a forward-looking plan (week-by-week execution plan, aspirational "Success Metrics," an "Outcome Target" instead of an "Outcome") with none of the "Delivered"/"Live Validation" evidence sections every other phase doc has. The underlying features (billing/Stripe, custom domains, SLA monitoring) do actually exist in the code, so this looks like the work shipped but the doc was never rewritten from plan-form to a real completion retrospective. Fix: either rewrite `phase-04.md` with real delivered/verification details and flip its own Status to match the index, or correct the index back to `Planned`/`In Progress` until that rewrite happens.

## OQ-015 — Phase 4's SLA promise and API surface don't match what shipped

- Status: Open
- Notes: `phase-04.md`'s pricing table promises the $29/mo "team" tier "99.5% SLA," and its "API Surface" list names `GET /v1/sla/status`. The actual implementation (`cloud/internal/sla/service.go`, confirmed by `cloud/README.md`) exposes `GET /v1/sla/summary` and `GET /v1/sla/periods`, both gated to `business`/`enterprise` tier only (`GET /v1/status/public` is the only unauthenticated one) — "team" isn't a recognized eligible tier anywhere in the SLA gating code. So the endpoint name drifted, and it's unclear whether "team" customers are meant to get an SLA credit/target without any dashboard visibility, or whether this is a real gap between the pricing promise and what was built. Worth confirming intent before this becomes a support/billing dispute.
- Cross-check: the individual feature docs for this same work (`cloud/docs/features/feature-16-billing-and-subscriptions.md`, `feature-19-custom-domain-support.md`, `feature-20-sla-monitoring-status.md` — moved from `spec` to `cloud/docs` 2026-09-18, OQ-002) all say `Status: Built` and accurately match the real code/endpoints. So the underlying Phase 4 work is genuinely done — it's specifically the roadmap-level `phase-04.md` summary (OQ-014) that never got updated, not the feature-level docs.

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

## OQ-019 — No CI/automated test pipeline; phase-completion claims are self-asserted

- Status: Workflows drafted 2026-09-18; not yet installed — blocked on Brock pushing them himself
- Notes: None of `spec`, `core`, or `cloud` has a `.github/` (or other CI config) directory. There's real Go test coverage throughout `cloud` and `core` (`codec_test.go`, `jwt_test.go`, `rbac_test.go`, `webhook_test.go`, `service_test.go` in several packages, etc.), and manual QA artifacts exist (`cloud/docs/phase9-smoke-tests.md` + Postman collection, `cloud/docs/map-qa-checklist.md`), but nothing runs these automatically on push/PR. `phase-06.md` itself already flags this: "Full local `go test ./...` remains dependent on local Go toolchain availability." So the "Completed"/"verified in production" claims in the phase docs (specific dates, specific handles created) are self-reported in the docs themselves, not backed by any CI artifact.
- Fix drafted: a `.github/workflows/ci.yml` per repo. `core`: `go build`/`go vet`/`go test ./...` on push/PR to `main`. `cloud`: same, plus a second checkout of `coordsapp/core` as a workspace sibling (`path: core` alongside `path: cloud`) so the `replace github.com/coordsapp/core => ../core` in `cloud/go.mod` resolves in CI the same way it does locally; `GOFLAGS=-mod=mod` set on the job since neither repo has a committed `go.sum` yet, so Go computes and uses checksums on the fly instead of requiring one. `spec` has no code to test, so its workflow instead validates `v1/test-vectors.json` parses as JSON and that the six required `v1/*.md`/`.json` protocol docs exist — a real check rather than a no-op green checkmark.
- **Blocked**: the device bridge refuses writes under any repo's `.github/workflows/` path ("protected file") — this mirrors GitHub's own restriction that pushing to `.github/workflows/` needs the `workflow` OAuth scope, since these files execute with repo permissions on every push/PR. Sent Brock the three drafted `ci.yml` files directly; he needs to add `.github/workflows/ci.yml` to each repo himself (commit them as-is, or adjust first).

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

## OQ-025 — Consumer map projection (Web Mercator) vs. cadastral-grade geodetic datums

- Status: Open — raised during map-software discussion, not yet scoped
- Notes: Nearly every consumer map renderer (OSM/Leaflet, Google Maps, Mapbox) displays in Web Mercator, which distorts area/distance increasingly with latitude. That's acceptable for "show a pin on a map" but not for a legal property boundary — government cadastral systems intentionally use local geodetic datums instead, specifically to avoid this distortion. Coords URIs are WGS84 lat/lng, which is the right global reference frame, but WGS84-the-datum and Web-Mercator-the-display-projection aren't the same thing, and it's not yet confirmed whether that distinction is documented anywhere in `spec`. Open question for CXS (Phase 10): if a national cadastral registry's source data is in a local datum, does XREF need real datum transformation (not just reformatting), and if so, is that in scope for Coords itself? Esri/ArcGIS-style GIS tooling supports this properly today; worth understanding what they do before designing something new.

## OQ-026 — OpenAPI contracts don't cover billing or warehouse endpoints

- Status: Open
- Notes: `cloud/openapi/` has three files — `v1.yaml` (resolver/status), `v1-phase3.yaml` (alias ownership/auth), `v1-phase9.yaml` (coordination/routing) — but two live parts of the API have no OpenAPI coverage at all: Phase 5's warehouse/dock/carrier endpoints (this gap is actually already acknowledged in `cloud/docs/features/feature-18-openapi-contracts.md`'s own "Current coverage note," dated February 16, 2026, as a follow-up item — but nothing has closed it since) and the billing/checkout endpoints (`POST /v1/billing/checkout-session`, `portal-session`, `GET /v1/billing/subscription`, `GET /v1/billing/invoices`, `POST /v1/billing/webhooks/stripe`), which aren't mentioned as a gap anywhere and I found independently by diffing the spec files' declared paths against the actual shipped endpoints from `cloud/README.md`/Phase 4. Fix: add `v1-phase4-billing.yaml` and `v1-phase5-warehouse.yaml` (or fold both into an existing/expanded contract file) so the OpenAPI contracts actually describe the full live API surface.

## OQ-027 — OpenAPI's "enables SDK/client generation and integration testing" claim is aspirational, not wired up

- Status: Open
- Notes: Feature 18's own description says OpenAPI "enables SDK/client generation and integration testing," but `cloud/Makefile` has exactly three targets (`test`, `run`, `fmt`) and none of them touch the OpenAPI specs — no codegen step, no contract/schema validation against the running API, nothing that would catch the spec drifting out of sync with real behavior (which OQ-026 shows has already happened twice). The specs are accurate for what they cover, they're just disconnected from the build/test pipeline. Related to OQ-019 (no CI at all) — fixing that would be the natural place to also wire in OpenAPI contract testing.
