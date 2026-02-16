# 09 - Custom Domains and SLA

## Custom domains
Endpoints:
- `POST /v1/domains`
- `POST /v1/domains/{id}/verify`
- `GET /v1/domains`

Verification methods:
- DNS TXT token
- CNAME target validation

## SLA monitoring
Endpoints:
- `GET /v1/sla/summary`
- `GET /v1/sla/periods`
- `GET /v1/status/public` (public)

SLA access is gated to eligible paid tiers.
