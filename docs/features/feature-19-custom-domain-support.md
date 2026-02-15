# Feature 19 - Custom Domain Support

## Status
Built

## What it does
Lets Business and Enterprise organizations claim custom domains and resolve handles like:

`@warehouse1.locations.acme.com`

## Endpoints
- `POST /v1/domains`
- `GET /v1/domains`
- `POST /v1/domains/{id}/verify`

## Key behavior
- Domain claim lifecycle with DNS verification (`dns_txt` or `cname`)
- Verified-domain lookup integrated into resolver path
- Per-org monthly claim cap and tier/subscription checks
- TLS provisioning hook for certificate automation integrations

## Where implemented
- `cloud/storage/schema_phase4_domains.sql`
- `cloud/internal/domains/service.go`
- `cloud/handlers/domains/`
- `cloud/internal/resolver/store_postgres.go`
