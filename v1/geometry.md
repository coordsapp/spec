# Coords v1 Geometry

## L1 URI
Coords v1 L1 locations are encoded as:

`coords:l1:v1:<lat>,<lng>,<alt>*<checksum>`

Example:

`coords:l1:v1:37.774900,-122.419400,15.25*1c86401e`

## Canonical numeric form
- `lat`: decimal degrees, fixed `6` fractional digits
- `lng`: decimal degrees, fixed `6` fractional digits
- `alt`: meters, fixed `2` fractional digits

All encoded values are canonicalized before checksum calculation.

## Canonical payload
Checksum input payload is:

`v1|<lat>|<lng>|<alt>`

Using the example above:

`v1|37.774900|-122.419400|15.25`
