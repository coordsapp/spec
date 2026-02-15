# Feature 10 - JWT Authentication

## Status
Built

## What it does
Provides authenticated org-scoped access for alias and billing operations.

## Endpoints
- `POST /v1/auth/signup`
- `POST /v1/auth/token`

## Key behavior
- Issues signed JWTs with org and role claims
- Validates tokens in middleware
- Supports secured API access for non-public operations

## Where implemented
- `cloud/internal/auth/`
- `cloud/cmd/resolver/main.go`
