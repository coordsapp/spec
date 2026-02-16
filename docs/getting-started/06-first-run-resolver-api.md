# 06 - First Run: Resolver API

## Health check
```bash
curl https://coords.up.railway.app/healthz
```

## Resolve a handle
```bash
curl https://coords.up.railway.app/v1/resolve/J41k@WDC1
```

## Altitude override
```bash
curl "https://coords.up.railway.app/v1/resolve/J41k@WDC1?alt=42.1"
```

## Key status codes
- `200`: resolved
- `400`: invalid handle or input
- `404`: handle not found
- `429`: rate limit exceeded
