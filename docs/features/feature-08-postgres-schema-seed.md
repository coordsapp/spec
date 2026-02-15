# Feature 08 - PostgreSQL Schema and Seed Data

## Status
Built

## What it does
Defines persistent relational schema and launch seed data for resolver and alias ownership flows.

## Key assets
- `cloud/storage/schema.sql`
- `cloud/storage/schema_phase3.sql`
- `cloud/storage/schema_phase4_billing.sql`
- `cloud/storage/seed.sql`

## Key behavior
- Constraints for coordinates, ownership, and lifecycle fields
- Indexes for handle lookup and operational queries
- Seed aliases for immediate resolver utility at launch
