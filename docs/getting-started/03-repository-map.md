# 03 - Repository Map

## `coordsapp/spec`
Protocol and documentation source of truth:
- v1 format docs
- test vectors
- phases/features docs

## `coordsapp/core`
Go CLI:
- `coords encode lat lng alt`
- `coords decode <uri>`
- Works offline

## `coordsapp/cloud`
Hosted API and platform services:
- `/v1/resolve/{handle}`
- Auth, orgs, RBAC
- Alias claiming and verification
- Billing, domains, SLA/status
