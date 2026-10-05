# Orders Service

Order lifecycle API (Go). Creates orders, tracks state transitions, and emits order events
for downstream consumers. Deployment `orders` in `prod`.

**Owner:** the **Orders team** (Slack `#team-orders`). See `reference/service-ownership.md`
for the full ownership table and `reference/slos.md` for its SLO.

## Order states

`created → paid → picked → shipped → delivered`, plus terminal `cancelled` and `refunded`.
State transitions are one-way; a stuck order is almost always a consumer that failed to ack.

## Restart

```
kubectl rollout restart deploy/orders -n prod
```

## Health check
`GET /healthz` on port **8080**.

## Known quirk: connection leak after deploy

The orders service is the usual culprit behind `FATAL: too many connections` on Postgres.
After a deploy it occasionally fails to drain its old pool. Restarting orders releases the
connections — see `databases/postgres.md` for how to confirm.

## Dependencies
- Postgres `shopfast`
- `inventory` (stock reservation)
- `notifications` (order emails)
