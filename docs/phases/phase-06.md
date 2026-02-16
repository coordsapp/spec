# Phase 6 - Landing Experience and Developer Onboarding

## Status
Completed (Weeks 1-4 delivered by February 16, 2026)

## Objective
Turn `coords.up.railway.app` into a clear product entry point that communicates value quickly and drives developers into successful integration workflows.

## Goal
Move visitors from discovery to first useful API usage in under 10 minutes.

## Scope
- Landing page redesign at `/`
- Developer onboarding dashboard at `/app`
- Documentation hub routes under `/docs/*`
- In-browser resolver demo and starter code samples
- Enterprise pathway messaging and conversion links
- Interactive tutorial flow for warehouse onboarding
- Rich API explorer with preset endpoints and code generation
- Sandbox mode with no-account required trial workflow
- Onboarding event instrumentation and funnel analytics summary

## Initial Route Set
- `GET /`
- `GET /app`
- `GET /docs`
- `GET /docs/quickstart`
- `GET /docs/api-reference`
- `GET /docs/use-cases/logistics`
- `GET /docs/protocol`
- `POST /v1/onboarding/events`
- `GET /v1/onboarding/summary`
- `GET /v1/onboarding/funnel`

## Week 1 Delivered
- Root landing page with value proposition, live resolver demo, and protocol vs hosted service positioning
- Docs hub and Phase 6 route structure (`/docs`, `/docs/quickstart`, `/docs/api-reference`, `/docs/use-cases/logistics`, `/docs/protocol`)
- Developer app entry page at `/app`
- JSON compatibility preserved for existing root integrations via `/?format=json` and `Accept: application/json`

## Week 2 Delivered
- Tutorial runner in `/app` with stateful steps:
1. signup
2. create warehouse
3. create dock
4. verify dock
5. issue carrier token
6. arrive
7. depart
8. list operations
- API explorer mode switching:
1. `sandbox` local simulation
2. `live` real API execution
- Auto-generated request snippets for:
1. cURL
2. JavaScript
3. Python
4. Go
- Local state persistence for sandbox resources and tutorial progress (browser local storage)

## Week 3 Delivered
- Add conversion instrumentation on:
1. landing page CTA clicks
2. resolver demo runs
3. `/app` mode switching and preset selection
4. tutorial step outcomes and completion
5. API explorer request/response outcomes
- Add backend onboarding analytics APIs:
1. `POST /v1/onboarding/events`
2. `GET /v1/onboarding/summary`
- Add in-memory funnel summary for immediate monitoring of onboarding drop-off
- Keep root/API compatibility fully unchanged for existing integrations

## Week 4 Delivered
- Add filtered analytics query support (`since_minutes`, `mode`, `page`) for summary and funnel reads
- Add dedicated funnel endpoint:
1. `GET /v1/onboarding/funnel`
- Add live onboarding insights panel in `/app`:
1. filter controls for mode and time window
2. summary payload visibility
3. step conversion and drop-off visibility
- Add refresh hooks after tutorial and explorer actions so optimization loops happen in-product

## Operational Notes
- Week 2/3/4 web UX work is implemented in `cloud/handlers/web/handler.go`
- Week 3/4 onboarding analytics service is implemented in:
1. `cloud/internal/onboarding/service.go`
2. `cloud/handlers/onboarding/handler.go`
- Route wiring remains in `cloud/cmd/resolver/main.go`
- Full local `go test ./...` remains dependent on local Go toolchain availability
- Railway deployment verification should be run after each Week 4 update

## Success Metrics
- Landing-to-signup/docs click-through >= 25%
- Onboarding flow completion >= 60%
- Time to first successful resolver call < 10 minutes
- Measurable increase in enterprise inquiry volume
