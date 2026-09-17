# Payments Service — Runbook

The **payments** service handles checkout and talks to Stripe. It runs as the
`payments` deployment in the `prod` namespace.

## Restart / bounce the service
To restart (bounce) the payments service safely:

```
kubectl rollout restart deploy/payments -n prod
```

This does a rolling restart with zero downtime. Watch it roll out:

```
kubectl rollout status deploy/payments -n prod
```

## Health check
The service exposes a health endpoint on `/healthz` (port 8080). A healthy
response is `200 OK` with body `{"status":"ok"}`.

## Common issues

### Checkout returns 502
Usually the pods are not ready. Check pod status with `kubectl get pods -n prod`.
If pods are in `CrashLoopBackOff`, check logs (`kubectl logs`) — the most common
cause is a missing `STRIPE_API_KEY` env var after a secret rotation.

### "Card declined" spike
Check the Stripe dashboard first. If Stripe is healthy, look for a bad deploy —
roll back using the steps in `deployments.md`.

### High latency
The payments service caches customer tokens in Redis. If Redis is down, latency
spikes. Confirm Redis is up before restarting payments.

## Escalation
If a restart and rollback don't fix checkout, page the Payments on-call
(see `incident-response.md`) — checkout down is always at least a SEV-2.
