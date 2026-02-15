# Feature 02 - L1 URI and Checksum Format

## Status
Built

## What it does
Implements canonical L1 URIs in the form:

`coords:l1:v1:<lat>,<lng>,<alt>*<checksum>`

Checksum is generated from canonical payload fields and used for typo/corruption detection during decode/resolve.

## Key behavior
- Canonical numeric formatting for `lat`, `lng`, and `alt`
- Checksum validation on decode
- Rejects malformed URI payloads and checksum mismatches

## Where implemented
- `core/internal/coords/codec.go`
- `core/internal/coords/codec_test.go`
