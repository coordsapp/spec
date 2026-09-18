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
- Rejects non-finite values (`NaN`, `Infinity`) at the bounds-validation step, per `spec/v1/boundaries.md` (fixed 2026-09-18, tracked as OQ-001 — see `docs/open-questions.md`)

## Where implemented
- `core/coords/codec.go`
- `core/coords/codec_test.go`
- `cloud/internal/resolver/l1.go` imports this package directly (as of the OQ-003 fix) rather than maintaining its own copy, so `cloud` gets the same validation automatically
