# Scaling

Most services scale horizontally with HPA on CPU. A few need manual attention.

## Horizontal pod autoscaling

Defaults: min 3 replicas, max 20, target 70% CPU.

```
kubectl get hpa -n prod
kubectl scale deploy/web --replicas=10 -n prod
```

Manual scaling survives until the HPA next reconciles — if you need it to stick, change the
HPA min, not the replica count.

## Services that do not autoscale well

- **payments-gateway** — scaling out increases concurrent processor connections, which the
  processor rate-limits. Max 8 replicas.
- **search** — indexing is stateful; scale the query pods, not the indexer.
- **postgres** — does not scale horizontally at all. Read load goes to the standby.

## Traffic events

For a known spike (campaign launch, Black Friday) pre-scale the day before rather than
relying on the HPA to catch up. See `operations/capacity-planning.md`.
