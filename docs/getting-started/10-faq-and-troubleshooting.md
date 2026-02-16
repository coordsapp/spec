# 10 - FAQ and Troubleshooting

## Why do I get `billing is not configured`?
`STRIPE_SECRET_KEY` is missing in runtime env.

## Why does checkout fail with "No such price"?
Use Stripe **price IDs** (`price_...`), not product IDs (`prod_...`).

## Why do domains/SLA return `402`?
Org tier is not Business/Enterprise, or subscription status is inactive.

## Why does auto-migrate fail with "relation already exists"?
A migration was rerun without idempotent guards. Ensure schema files are safe for repeated startup execution.

## Why does resolve return `404`?
Handle is missing, expired, or not verified in registry.

## Fast debug checklist
- Verify env vars in Railway
- Check `/healthz`
- Check billing subscription payload
- Inspect logs for SQL or webhook signature errors
