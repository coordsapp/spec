# Phase 10 - Coords XREF System (CXS): Design and Discussion

## Status
Planning — not started. No code, no schema, no API surface yet. This doc is the discussion space, not a delivery record.

## Why this phase exists
Landos's public whitepaper (`Landos-Foundation/community`, section 3.3) already describes a "Coords XREF System" as if it's an existing part of the Coords protocol: a system that maps every major spatial identifier — H3, What3Words, WGS84, GeoJSON, Plus Codes, MGRS, postal addresses, national cadastral registries — onto one canonical Coords URI. Nothing in `spec` or `core` actually specifies or implements this today. Since Landos is Brock's own project and is already publicly committed to CXS existing, this needs a real design, not just a name.

## Objective
Decide what CXS is before building any of it: what it maps, where it lives (protocol vs. reference implementation vs. hosted service), and what "correct" means when converting between systems with fundamentally different shapes (points vs. cells vs. polygons).

## Open Design Questions

1. **Directionality.** Is CXS one-way (foreign ID → Coords URI) or bidirectional (Coords URI → best-match foreign ID per system)? Bidirectional is more useful but means CXS has to pick a canonical foreign representative when several exist (e.g., which of several overlapping H3 resolutions to return).

2. **Precision and shape mismatch.** Coords URIs are single points (lat/lng/alt, see `spec/v1/geometry.md`). H3 cells, Plus Codes, and MGRS grid squares are areas, not points. GeoJSON can be arbitrary geometry. Converting an area-based ID to a point Coords URI is lossy (which point — centroid?) and converting a Coords point back to an area-based ID is ambiguous (which cell/resolution?). Needs an explicit, documented lossy-conversion policy, not an implicit one.

3. **Scope per foreign system** — these aren't equally tractable:
   - **WGS84 / GeoJSON (points)** — trivial, already the basis of Coords itself.
   - **Plus Codes (Open Location Code)** — open format, Google-published algorithm, safe to implement directly.
   - **MGRS** — open military/NATO standard, well-documented, safe to implement directly.
   - **H3** — open (Uber, Apache 2.0 license), but is a discrete hexagonal grid at 16 resolutions — the precision question above applies directly.
   - **What3Words** — proprietary algorithm; W3W has a history of contesting reverse-engineering. XREF to/from W3W likely means calling their licensed API, not reimplementing their word-grid, which brings in a cost/rate-limit/dependency question rather than a pure protocol question.
   - **Postal addresses** — inherently ambiguous (geocoding, not a coordinate system) and jurisdiction-dependent; probably out of scope for CXS itself and better left to an external geocoder feeding a Coords URI in.
   - **National cadastral registries** — enormous, per-country scope (different schemas, different legal authorities). This may be exactly the kind of thing Landblock's Parcel/Authority Registry model was meant to handle rather than something CXS should absorb directly.

4. **Where does CXS live?**
   - The *mapping rules* (e.g., "a Plus Code of length N converts to a Coords URI how") feel like protocol-level content — CC0, in `spec`, versioned alongside the URI format itself.
   - A *reference converter* (actual conversion code for the open, non-licensed formats: Plus Codes, MGRS, H3, GeoJSON/WGS84) fits `core`, next to the existing encode/decode CLI.
   - A *hosted lookup/batch-conversion service* (especially anything needing a live What3Words API call, or a cross-reference database of already-registered foreign IDs) is a `cloud` feature, not a protocol concern.
   - This split needs to be decided before anything is built, so CXS doesn't repeat the OQ-003 mistake (an independent, less-validated implementation in `cloud` that diverges from the reference).

5. **Versioning.** Coords itself is versioned (`v1` today). Does CXS version independently, or is it pinned to a Coords protocol version? A breaking change to how H3 resolutions map to Coords points would need its own compatibility story.

6. **Relationship to existing test-vector conventions.** `spec/v1/test-vectors.md` / `test-vectors.json` set the precedent for how Coords proves correctness. CXS should probably ship with equivalent cross-system test vectors (a fixed Plus Code ↔ fixed Coords URI ↔ fixed MGRS pair, etc.) rather than relying on prose description alone.

## Explicitly Not Deciding Yet
This doc intentionally stops at open questions. No format, schema, or API shape is proposed here — that comes after the questions above have real answers, so the resulting design doesn't have to be unwound later.

## Next Steps
- Work through the open questions above (in particular #3 and #4 — scope and placement — since they gate everything else).
- Once scope/placement are settled, draft an actual `spec/v1/xref.md` (or similar) the same way `geometry.md`/`checksum.md`/`altitude.md` were written, before any code.
- Revisit `docs/open-questions.md` OQ-020 once this phase has real answers — Landos is currently relying on a system that doesn't exist yet, so it's worth telling that project's team (even if it's you wearing a different hat) roughly when CXS becomes real.
