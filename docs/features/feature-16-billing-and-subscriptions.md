# Feature 16 - Billing and Stripe Subscription Endpoints

## Status
Built

## What it does
Adds hosted billing workflows for paid tiers while keeping protocol usage open.

## Endpoints
- `POST /v1/billing/checkout-session`
- `POST /v1/billing/portal-session`
- `GET /v1/billing/subscription`
- `GET /v1/billing/invoices`
- `POST /v1/billing/webhooks/stripe`

## Key behavior
- Stripe checkout and customer portal integration
- Subscription state tracking for tier enforcement
- Webhook ingestion with idempotency protections
- Invoice and subscription visibility for org admins

## Where implemented
- `cloud/internal/billing/`
- `cloud/handlers/billing/`
- `cloud/storage/schema_phase4_billing.sql`
