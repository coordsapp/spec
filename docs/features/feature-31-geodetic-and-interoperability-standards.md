# Feature 31 - Geodetic and Interoperability Standards Alignment

## Status
Not Started — this page identifies a documentation gap, not a shipped feature. No content below is yet reflected in `spec/v1/`.

## What it does (intended)
Documents which established geodetic, surveying, and geospatial-interoperability standards Coords is built on, aligned with, or intentionally diverges from — so anyone adopting Coords (including Landos, Landblock, and any future government/registry consumer) can verify exactly what it does and doesn't already conform to, rather than taking "open standard" on faith.

## Why this exists
Coords is positioned as a global standard for geographic location, but none of the existing feature or protocol docs state its relationship to the standards that already exist in this space. That's a real gap, not a cosmetic one — surfaced during the September 2026 review's discussion of map rendering and the Coords XREF System (see `docs/open-questions.md` OQ-025, and Phase 10).

## Standards Coords should explicitly document its relationship to

- **WGS84 (World Geodetic System 1984)** — the datum Coords lat/lng values are presumed to be defined against. `spec/v1/geometry.md` should state this explicitly rather than leave it implicit; right now nothing in `spec` confirms it in writing.
- **Web Mercator (EPSG:3857)** — the display projection nearly every consumer map renderer uses (OSM/Leaflet, Google Maps, Mapbox), and explicitly *not* the same thing as WGS84. Web Mercator distorts area/distance with latitude, which is fine for showing a pin on a map but not for anything precision-sensitive. Coords needs to state plainly that its lat/lng values are WGS84 datum coordinates, not Web Mercator projected coordinates, so no adopter conflates "how it's drawn on a map" with "what the coordinate actually is."
- **ISO 19111 (Geographic information — Referencing by coordinates)** — the international standard for spatial reference systems. Coords doesn't need to adopt its full machinery, but should state where its own model maps onto or departs from ISO 19111 terms, for credibility with any standards-literate adopter.
- **National geodetic control network standards** (e.g., US NGS/FGCC "Standards and Specifications for Geodetic Control Networks") — the established precedent for deriving new survey points from a small set of trusted reference points via triangulation/trilateration. Relevant to any Coords point captured through ground survey rather than a raw GPS reading.
- **Geodesic distance calculation** — Vincenty's formulae (or Karney's method for edge cases near antipodal points) as the standard for accurate ellipsoidal-earth distance between two Coords points, rather than a flat-plane or spherical (haversine) approximation. Relevant to Phase 9's routing work and any future distance calculation built on Coords.
- **Cross-referenced identifier formats** (Open Location Code / Plus Codes, MGRS, H3, GeoJSON) — the external formats the Coords XREF System (Phase 10, CXS) is meant to map to/from. Not part of Coords itself, but part of the interoperability surface Coords needs to document clearly.

## What's explicitly out of scope here
This feature is about *documenting alignment*, not adopting or reimplementing any of the above wholesale. Coords stays its own lightweight format; this is about being honest and precise regarding where it sits relative to the standards that predate it.

## Next steps
1. Add an explicit WGS84 statement to `spec/v1/geometry.md`.
2. Write a new `spec/v1/standards-alignment.md` (or similar) laying out the relationship to each item above.
3. Reference this feature page and that new spec doc from Phase 10 (CXS) once CXS design work resumes.

## Related
- `docs/open-questions.md`: OQ-025
- `docs/phases/phase-10.md` (Coords XREF System)
