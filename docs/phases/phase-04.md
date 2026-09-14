# Phase 4 - Enterprise Features and Scale

## Status
Partially Completed

*(Corrected 2026-09-14 — this doc previously said "Planned" while the phases index said "Completed." Neither was right: 3 of the 5 scoped items shipped and are verified at the feature level; 2 were never built. See "Delivered" and "Not Delivered" below.)*

## Objective
Monetize hosted Coords with enterprise-grade reliability, branding, access control, and analytics while keeping the protocol open.

## Goal
Deliver enterprise features in 6 weeks, with clear paid-tier value while preserving free protocol usage.

## Monetization Model
- `free`: 5 aliases/org, no analytics, community support
- `team` ($29/mo): 100 aliases/org, basic analytics, 99.5% SLA
- `business` ($299/mo): unlimited aliases, usage dashboards, 99.9% SLA
- `enterprise` (custom): custom domain, SAML/SCIM, 99.99% SLA, advanced support

*(Note: the SLA endpoints are gated to `business`/`enterprise` tier only in the actual code — `team` isn't a recognized eligible tier. See `docs/open-questions.md` OQ-015.)*

## Scope

## Delivered
- **Billing and subscriptions** (Stripe checkout, portal, invoices, webhook ingestion) — `Status: Built` per `spec/docs/features/feature-16-billing-and-subscriptions.md`. Implemented in `cloud/internal/billing/`, `cloud/handlers/billing/`.
- **Custom domain support** with DNS verification (`dns_txt`/`cname`) — `Status: Built` per `feature-19-custom-domain-support.md`. Implemented in `cloud/internal/domains/`. Note: TLS certificate provisioning itself is still a no-op stub (`domains/tls.go`) — see OQ-006.
- **SLA instrumentation** (uptime tracking, incident lifecycle, credit-percentage calculation, public status) — `Status: Built` per `feature-20-sla-monitoring-status.md`. Implemented in `cloud/internal/sla/`.

## Not Delivered
- **Enterprise identity features** (SAML 2.0, SCIM, auditability) — no `saml`/`scim`/identity package exists anywhere in `cloud/internal` or `cloud/handlers`.
- **Analytics APIs and dashboard reporting for resolver usage** (`GET /v1/analytics/resolutions`) — no matching endpoint or package exists. (Onboarding funnel analytics from Phase 6 and SLA-compliance analytics from Phase 9 are separate, narrower things and don't cover this.)

## API Surface

Actually shipped:
- `POST /v1/billing/checkout-session`
- `POST /v1/billing/portal-session`
- `GET /v1/billing/subscription`
- `GET /v1/billing/invoices`
- `POST /v1/billing/webhooks/stripe`
- `POST /v1/domains`
- `GET /v1/domains`
- `POST /v1/domains/{id}/verify`
- `GET /v1/sla/summary` (business/enterprise tier)
- `GET /v1/sla/periods` (business/enterprise tier)
- `GET /v1/status/public` (no auth)

Originally planned but not built:
- `DELETE /v1/domains/{id}`
- `GET /v1/analytics/resolutions`
- `GET /v1/sla/status` (the endpoint that shipped is named `/v1/sla/summary`, not `/v1/sla/status`)

## Execution Plan
1. Week 1-2: billing and subscription lifecycle
2. Week 3: custom domains and TLS provisioning
3. Week 4: SLA monitoring and credit pipeline
4. Week 5: SAML/SCIM and enterprise identity controls
5. Week 6: analytics, dashboards, and launch

## Success Metrics
- Enterprise contracts: 3+ in first month after launch
- Active custom domains: 10+
- SLA compliance: 99.9%+ (business), 99.99% target (enterprise)
- New recurring revenue: $5k+ MRR from enterprise tier

*(No evidence in the repo that these metrics were ever measured or reported against — worth tracking as a separate question if they matter.)*

## Outcome
Billing, custom domains, and SLA monitoring shipped and are verified at the feature-doc level. Enterprise identity (SAML/SCIM) and the resolver-usage analytics dashboard were scoped in this phase but never built — if enterprise deals depend on either, that's a real gap, not just a documentation one.
