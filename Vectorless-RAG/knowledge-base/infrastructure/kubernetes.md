# Kubernetes

ShopFast runs on managed Kubernetes, one cluster per environment.

## Namespaces
`prod`, `staging`, `dev`, plus `platform` for shared tooling (monitoring, ingress
controllers). Application workloads never run in `platform`.

## Node pools

| Pool | Instance type | Used for |
|------|---------------|----------|
| `general` | on-demand | stateless services |
| `spot` | spot | batch jobs, non-critical workers |
| `stateful` | on-demand only | Postgres, Elasticsearch, Redis |

**Stateful workloads must never land on spot.** This caused the May 2026 SEV-1 — see
`incidents/postmortem-2026-05-db-failover.md`.

## Common operations

```
kubectl get pods -n prod
kubectl rollout restart deploy/<service> -n prod
kubectl logs -n prod deploy/<service> --tail=200
kubectl describe pod -n prod <pod>
```

## Resource requests

Every workload must set CPU and memory requests. Pods without requests get scheduled
anywhere and are the first evicted under pressure. The admission webhook rejects deployments
without them.

## Access
Cluster access is via SSO + short-lived credentials. See `security/access-control.md`.
