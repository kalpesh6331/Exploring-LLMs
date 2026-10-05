# Payments Service

The **payments** service owns the checkout flow: it validates the cart, creates a payment
intent, and records the transaction. It runs as the `payments` deployment in the `prod`
namespace. Owned by the **Payments team**.

> Not to be confused with the **payments-gateway**, which is the separate outbound adapter
> that actually talks to Stripe and Adyen. See `payments-gateway.md`.

## Restart / bounce the service

```
kubectl rollout restart deploy/payments -n prod
```

This is a rolling restart with zero downtime. Watch it:

```
kubectl rollout status deploy/payments -n prod
```

## Health check

`GET /healthz` on port **8080**. A healthy response is `200 OK` with `{"status":"ok"}`.
Readiness is `/readyz` — it also checks the Redis session store.

## Common issues

### Checkout returns 502
Usually pods are not ready. Check `kubectl get pods -n prod -l app=payments`. If pods are in
`CrashLoopBackOff`, the most common cause is a missing `STRIPE_API_KEY` after a secret
rotation — see `security/key-rotation.md`.

### "Card declined" spike
Check the gateway first (`payments-gateway.md`), then look for a bad deploy and roll back
using `operations/rollbacks.md`.

### High latency
The service caches customer tokens in Redis. If Redis is degraded, p99 latency spikes.
Confirm Redis health before restarting payments.

## Dependencies
- `payments-gateway` (outbound card processing)
- `orders` (to mark an order paid)
- Postgres `shopfast` database
- Redis (session + token cache)

## Escalation
Checkout down is **always at least a SEV-2**. Page the Payments on-call —
see `incidents/on-call-rotation.md`.
