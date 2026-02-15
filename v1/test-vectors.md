# Coords v1 Test Vectors

## Positive vectors

| lat | lng | alt | canonical payload | checksum | full URI |
|---|---|---|---|---|---|
| `37.774900` | `-122.419400` | `15.25` | `v1\|37.774900\|-122.419400\|15.25` | `1c86401e` | `coords:l1:v1:37.774900,-122.419400,15.25*1c86401e` |
| `0.000000` | `0.000000` | `0.00` | `v1\|0.000000\|0.000000\|0.00` | `8922cf52` | `coords:l1:v1:0.000000,0.000000,0.00*8922cf52` |
| `-33.868800` | `151.209300` | `58.70` | `v1\|-33.868800\|151.209300\|58.70` | `905f6970` | `coords:l1:v1:-33.868800,151.209300,58.70*905f6970` |
| `48.856600` | `2.352200` | `35.40` | `v1\|48.856600\|2.352200\|35.40` | `ae6c07e1` | `coords:l1:v1:48.856600,2.352200,35.40*ae6c07e1` |

## Negative vectors
- Checksum mismatch (last nibble changed):
  - `coords:l1:v1:37.774900,-122.419400,15.25*1c86401f`
- Out-of-range latitude:
  - `coords:l1:v1:90.100000,0.000000,0.00*2ca9e8f2`
- Non-canonical formatting (wrong precision):
  - `coords:l1:v1:37.7749,-122.4194,15.2*beefbeef`
