# Coords v1 Boundaries

## Allowed ranges
- Latitude: `-90.0` to `90.0` (inclusive)
- Longitude: `-180.0` to `180.0` (inclusive)
- Altitude: `-500.0` to `20000.0` meters (inclusive)

## Validation rules
- Encoders must reject values outside the allowed ranges.
- Decoders must reject URIs containing out-of-range values.
