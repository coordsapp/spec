# Coords v1 Checksum

## Algorithm
Coords v1 uses FNV-1a 32-bit on the canonical payload:

`v1|<lat>|<lng>|<alt>`

## Output format
- Lowercase hexadecimal
- Exactly 8 characters
- Appended as `*<checksum>` in the URI

## Pseudocode
```text
hash = 2166136261
for each byte b in utf8(payload):
  hash = hash XOR b
  hash = (hash * 16777619) mod 2^32
checksum = lowercase_hex_8(hash)
```
