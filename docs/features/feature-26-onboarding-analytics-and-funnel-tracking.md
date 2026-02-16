# Feature 26 - Onboarding Analytics and Funnel Tracking

## Status
Built (Week 3 delivered on February 16, 2026)

## What it does
Adds lightweight, first-party instrumentation for the new landing and onboarding flows so the team can measure conversion and identify drop-off points.

## Key behavior
- Frontend emits structured events from:
1. landing page views and CTA clicks
2. resolver demo attempts/results
3. `/app` mode and preset changes
4. tutorial step outcomes and completion
5. API explorer request/response outcomes
- Backend receives analytics events through:
1. `POST /v1/onboarding/events`
2. `GET /v1/onboarding/summary`
- Event summary includes:
1. event totals and last event timestamp
2. counts by event name/mode/page/step
3. conversion-oriented counters (tutorial completion, primary CTAs)
- Recent events are retained in bounded in-memory storage for quick operational review.

## Primary endpoints
- `POST /v1/onboarding/events`
- `GET /v1/onboarding/summary`

## Where implemented
- `cloud/internal/onboarding/service.go`
- `cloud/handlers/onboarding/handler.go`
- `cloud/handlers/web/handler.go`
- `cloud/cmd/resolver/main.go`
