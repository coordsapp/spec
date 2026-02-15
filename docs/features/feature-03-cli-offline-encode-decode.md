# Feature 03 - Offline CLI Encode/Decode

## Status
Built

## What it does
Provides an offline Go CLI for encoding coordinates into L1 URIs and decoding them back.

## Commands
- `coords encode <lat> <lng> <alt>`
- `coords decode <uri>`

## Key behavior
- Runs without network dependency
- Validates checksum on decode
- Returns structured command errors for invalid input

## Where implemented
- `core/cmd/coords/main.go`
- `core/internal/coords/codec.go`
