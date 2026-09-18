# Coords v1 Boundaries

## Allowed ranges
- Latitude: `-90.0` to `90.0` (inclusive)
- Longitude: `-180.0` to `180.0` (inclusive)
- Altitude: `-500.0` to `20000.0` meters (inclusive)

## Validation rules
- Encoders must reject values outside the allowed ranges.
- Decoders must reject URIs containing out-of-range values.
- Latitude, longitude, and altitude must all be finite. `NaN` and `Infinity` (positive or negative) are always invalid, regardless of range checking. This is a normative requirement, not an implementation detail: under IEEE 754, a naive reject-based range check (`value < min || value > max`) silently lets `NaN` through, because every comparison against `NaN` is `false`. Implementations must validate with an accept-based check (`!(value >= min && value <= max)`) and/or explicit finiteness checks, so `NaN`/`Infinity` are always rejected regardless of how the range check is written. A string parser that accepts the literals `"NaN"`, `"Inf"`, `"+Inf"`, `"-Inf"` (as most standard library float parsers do) must still reject them at the bounds-validation step. See `test-vectors.md`'s non-finite negative vectors.
