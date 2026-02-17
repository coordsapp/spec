# Protocol Compliance Instructions

## L1 URI Specification

### Canonical Format

```
coords:l1:v1:<lat>,<lng>,<alt>*<checksum>
```

**Example:**
```
coords:l1:v1:37.774900,-122.419400,15.25*1c86401e
```

### Canonical Payload (for checksum)

```
v1|<lat>|<lng>|<alt>
```

**Example:**
```
v1|37.774900|-122.419400|15.25
```

### Precision Requirements

| Field | Precision | Example |
|-------|-----------|----------|
| Latitude | 6 decimals | `37.774900` |
| Longitude | 6 decimals | `-122.419400` |
| Altitude | 2 decimals | `15.25` |

**IMPORTANT:** Altitude is REQUIRED (not optional). Default to `0.00` if unknown.

### Checksum Algorithm

```
FNV-1a 32-bit hash
Output: lowercase hex, exactly 8 characters
```

**Pseudocode:**
```
hash = 2166136261 (FNV1_32A_INIT)
for each byte b in utf8(canonical_payload):
    hash = hash XOR b
    hash = (hash * 16777619) mod 2^32
checksum = lowercase_hex_8(hash)
```

### Test Vectors (MUST PASS)

| Input | Expected Checksum | Expected URI |
|-------|-------------------|---------------|
| (37.7749, -122.4194, 15.25) | `1c86401e` | `coords:l1:v1:37.774900,-122.419400,15.25*1c86401e` |
| (0.0, 0.0, 0.0) | `8922cf52` | `coords:l1:v1:0.000000,0.000000,0.00*8922cf52` |
| (-33.8688, 151.2093, 58.7) | `905f6970` | `coords:l1:v1:-33.868800,151.209300,58.70*905f6970` |
| (48.8566, 2.3522, 35.4) | `ae6c07e1` | `coords:l1:v1:48.856600,2.352200,35.40*ae6c07e1` |

### Go Implementation Reference

```go
// From cloud/internal/resolver/l1.go
func EncodeL1(lat, lng, alt float64) string {
    latCanonical := formatFixed(lat, 6)
    lngCanonical := formatFixed(lng, 6)
    altCanonical := formatFixed(alt, 2)
    payload := fmt.Sprintf("v1|%s|%s|%s", latCanonical, lngCanonical, altCanonical)
    return fmt.Sprintf(
        "coords:l1:v1:%s,%s,%s*%s",
        latCanonical,
        lngCanonical,
        altCanonical,
        checksum(payload),
    )
}
```

## L2 Handle Specification

### Format

```
@<tenant>/<path>
```

**Examples:**
```
@acme/warehouse/dock-1
@bridgeflow/terminal-a
@carrier/fastfreight-truck-123
```

### Resolution

L2 handles resolve to L1 coordinates via:
```
GET /v1/resolve/@acme/warehouse/dock-1
```

### Validation Rules

1. Must start with `@`
2. Tenant cannot be empty
3. Path must have at least one segment
4. Characters: alphanumeric, `-`, `_`, `.`

## Implementation Checklist

- [ ] L1 generation uses pipe `|` separator in canonical payload
- [ ] L1 URI uses comma `,` separator in display format
- [ ] Altitude is always included (default 0.00)
- [ ] Precision is exactly 6/6/2 decimals
- [ ] Checksum is lowercase hex, 8 characters
- [ ] All 4 test vectors pass
- [ ] L2 handles start with `@`
- [ ] Resolution returns L1 + coordinates
