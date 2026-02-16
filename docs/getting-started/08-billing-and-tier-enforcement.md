# 08 - Billing and Tier Enforcement

## Subscription flow
1. Create checkout session (`POST /v1/billing/checkout-session`)
2. Complete payment in Stripe
3. Stripe webhook updates org tier

## Tier impact
- Free/Team: standard platform access
- Business/Enterprise: custom domains + SLA endpoints

## Expected behavior
- Webhook events are idempotent
- Tier updates are reflected in `/v1/billing/subscription`
- Unauthorized paid-feature access returns `402`
