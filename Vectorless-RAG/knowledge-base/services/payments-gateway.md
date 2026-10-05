# Payments Gateway

The **payments-gateway** is the outbound adapter between ShopFast and our card processors
(Stripe primary, Adyen failover). It is a separate deployment from the payments service —
it holds the processor credentials and does retry/backoff on processor errors.

Owned by the **Payments team**. Runs as `payments-gateway` in the `prod` namespace.

## Restart / bounce the gateway

```
kubectl rollout restart deploy/payments-gateway -n prod
```

Restarting the gateway drops in-flight processor calls. Those are retried by the payments
service, but you will see a brief error spike. Prefer to restart during low traffic.

## Health check

`GET /healthz` on port **8081** (note: different from the payments service, which uses 8080).

## Processor failover

If Stripe is degraded, flip to Adyen:

```
kubectl set env deploy/payments-gateway PROCESSOR=adyen -n prod
```

Failover is **not** automatic. It is a deliberate manual step, because switching processors
mid-incident changes settlement behaviour. Announce it in `#incidents` first.

## Common issues

- **ERR-5012 storm** — the gateway is timing out talking to the processor. See
  `reference/error-codes.md`. Usually upstream; check the processor status page before
  restarting anything.
- **Credential expiry** — processor keys rotate quarterly; see `security/key-rotation.md`.
- **Webhook backlog** — settlement webhooks queue in Redis; a backlog means the consumer is
  stuck, not that payments are failing.

## Dependencies
- Stripe / Adyen (external)
- Redis (webhook queue)
