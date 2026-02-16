# 14 - Phase 6 Week 4 Funnel Optimization

## Status
In Progress (started February 16, 2026)

## Why this matters
Week 3 added event capture. Week 4 turns those events into conversion insights directly inside the onboarding experience so teams can optimize quickly.

## New capability
- `GET /v1/onboarding/funnel` for step-level onboarding conversion and drop-off.
- Filtered analytics reads via query parameters:
1. `since_minutes`
2. `mode`
3. `page`
- `/app` includes a live "Onboarding Insights" panel with filters and refresh controls.

## Quick checks
```bash
curl "https://coords.up.railway.app/v1/onboarding/summary?since_minutes=60&mode=sandbox&page=app"
curl "https://coords.up.railway.app/v1/onboarding/funnel?since_minutes=60&mode=sandbox&page=app"
```

## Practical optimization loop
1. Filter to `mode=sandbox` and recent window (15-60 minutes).
2. Identify step with highest `drop_off`.
3. Improve copy/API defaults for that step.
4. Re-check funnel after deploy for conversion movement.

## Where implemented
- `cloud/internal/onboarding/service.go`
- `cloud/handlers/onboarding/handler.go`
- `cloud/handlers/web/handler.go`
- `cloud/cmd/resolver/main.go`
