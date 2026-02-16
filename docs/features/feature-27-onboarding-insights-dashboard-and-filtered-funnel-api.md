# Feature 27 - Onboarding Insights Dashboard and Filtered Funnel API

## Status
Completed (delivered February 16, 2026)

## What it does
Turns onboarding analytics into an operational tool by adding live insights in `/app` and filter-aware funnel reporting APIs.

## Key behavior
- Adds filtered analytics queries for:
1. `since_minutes`
2. `mode`
3. `page`
- Adds funnel API:
1. `GET /v1/onboarding/funnel`
- Adds `/app` Week 4 insights panel:
1. mode/time-window filters
2. live summary payload view
3. live funnel payload view with step conversion/drop-off
- Insights refresh is triggered by:
1. manual refresh action
2. tutorial actions
3. explorer request/response workflow

## Primary endpoints
- `GET /v1/onboarding/summary`
- `GET /v1/onboarding/funnel`
- `POST /v1/onboarding/events`

## Where implemented
- `cloud/internal/onboarding/service.go`
- `cloud/handlers/onboarding/handler.go`
- `cloud/handlers/web/handler.go`
- `cloud/cmd/resolver/main.go`
