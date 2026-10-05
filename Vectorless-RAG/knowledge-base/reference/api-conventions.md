# API Conventions

All internal ShopFast HTTP APIs follow these rules.

## Versioning
Path-based: `/v1/orders`. Breaking changes require a new version; additive changes do not.

## Errors
Every error response carries a machine-readable code from `reference/error-codes.md`:

```json
{ "error": { "code": "ERR-2003", "message": "Cart not found" } }
```

Never return a bare 500 with an HTML body.

## Idempotency
Any endpoint that creates or charges must accept an `Idempotency-Key` header and return the
original result on replay. This is mandatory for anything in the payments path.

## Pagination
Cursor-based: `?limit=50&cursor=...`. Offset pagination is not allowed on large tables.

## Timeouts
Internal calls default to a **3 second** timeout with 2 retries and jittered backoff.
Payments-path calls use **10 seconds** with no automatic retry — retrying a charge is unsafe.

## Health endpoints
`/healthz` (liveness) and `/readyz` (readiness) on every service. Ports are listed in
`reference/ports.md`.
