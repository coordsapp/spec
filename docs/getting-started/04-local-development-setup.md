# 04 - Local Development Setup

## Prerequisites
- Go 1.22+
- PostgreSQL (for cloud postgres mode)
- Railway CLI (optional for deployment checks)

## Core CLI setup
From `coordsapp/core`:
```bash
go test ./... -v
go build -o bin/coords ./cmd/coords
```

## Cloud setup (postgres mode)
From `coordsapp/cloud`, set env vars:
- `STORE_MODE=postgres`
- `DATABASE_URL=postgres://...`
- `AUTO_MIGRATE=true`

Then run:
```bash
go test ./... -v
go run ./cmd/resolver
```

## Minimum production envs
- `JWT_SECRET`
- `STRIPE_SECRET_KEY`
- `STRIPE_WEBHOOK_SECRET`
- `STRIPE_TEAM_PRICE_ID`
- `STRIPE_BUSINESS_PRICE_ID`
- `STRIPE_ENTERPRISE_PRICE_ID`
