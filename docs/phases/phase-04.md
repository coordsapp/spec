# Phase 4 - Enterprise Features and Scale

## Status
Planned

## Objective
Monetize hosted Coords with enterprise-grade reliability, branding, access control, and analytics while keeping the protocol open.

## Goal
Deliver enterprise features in 6 weeks, with clear paid-tier value while preserving free protocol usage.

## Monetization Model
- `free`: 5 aliases/org, no analytics, community support
- `team` ($29/mo): 100 aliases/org, basic analytics, 99.5% SLA
- `business` ($299/mo): unlimited aliases, usage dashboards, 99.9% SLA
- `enterprise` (custom): custom domain, SAML/SCIM, 99.99% SLA, advanced support

## Scope
- Billing and subscriptions (Stripe checkout, portal, invoices, usage/overage)
- Custom domain support with DNS ownership verification and TLS automation
- SLA instrumentation with uptime tracking and automated service credits
- Enterprise identity features (SAML 2.0, SCIM, auditability)
- Analytics APIs and dashboard reporting for resolver usage

## API Surface
- `POST /v1/billing/checkout-session`
- `POST /v1/billing/portal-session`
- `GET /v1/billing/subscription`
- `GET /v1/billing/invoices`
- `POST /v1/domains`
- `GET /v1/domains`
- `DELETE /v1/domains/{id}`
- `GET /v1/analytics/resolutions`
- `GET /v1/sla/status`

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

## Outcome Target
Enterprise-ready hosted platform with recurring revenue, contractual uptime, and operational visibility, while keeping the protocol and base tooling open.
