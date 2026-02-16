# 02 - Core Concepts (L1, L2, Handles, Aliases)

## L1 (immutable)
Format:
`coords:l1:v1:<lat>,<lng>,<alt>*<checksum>`

Properties:
- Offline-encodable
- Checksummed for typo detection
- Immutable once created

## L2 (human-friendly)
Examples:
- `J41k@WDC1`
- `@acme/warehouse1`
- `@dock1.locations.acme.com` (custom domain form)

L2 is what humans share; resolver returns canonical L1.

## Organizations and ownership
- Orgs claim aliases
- Claims require verification (geofenced or postal)
- Verified ownership is included in resolver metadata
