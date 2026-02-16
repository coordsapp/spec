# 05 - First Run: CLI

## Encode coordinates into L1
```bash
coords encode 38.8976763 -77.0365328 12.3
```
Expected shape:
`coords:l1:v1:38.8976763,-77.0365328,12.3*<checksum>`

## Decode L1
```bash
coords decode "coords:l1:v1:38.8976763,-77.0365328,12.3*a7f3b912"
```

## Validation behavior
- Invalid checksum should fail decode
- Lat/lng/alt bounds are enforced
