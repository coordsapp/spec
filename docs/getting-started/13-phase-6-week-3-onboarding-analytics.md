# 13 - Phase 6 Week 3 Onboarding Analytics

## Status
Delivered (completed February 16, 2026)

## Why this matters
Week 2 delivered a strong onboarding experience. Week 3 makes that experience measurable so product decisions are based on real conversion behavior instead of guesswork.

## New APIs
- `POST /v1/onboarding/events`
- `GET /v1/onboarding/summary`

## Event sources
- Landing page:
1. page view
2. CTA click events
3. resolver demo attempts and outcomes
- Developer app (`/app`):
1. mode changes (sandbox/live)
2. preset changes
3. tutorial step outcomes
4. tutorial completion
5. explorer request/response outcomes

## Sample summary call
```bash
curl "https://coords.up.railway.app/v1/onboarding/summary?limit=20"
```

## What to monitor weekly
1. `tutorial_completed` count and completion ratio vs `app_view`
2. most common failing tutorial step (`by_step` + non-2xx outcomes)
3. sandbox vs live usage mix (`by_mode`)
4. landing CTA performance (`cta_get_started`, `cta_contact_sales`)

## Where implemented
- `cloud/internal/onboarding/service.go`
- `cloud/handlers/onboarding/handler.go`
- `cloud/handlers/web/handler.go`
- `cloud/cmd/resolver/main.go`
