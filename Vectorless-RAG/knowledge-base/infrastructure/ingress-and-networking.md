# Ingress and Networking

Public traffic: **CDN → load balancer → NGINX ingress → service**.

## NGINX ingress

Runs in the `platform` namespace, 3 replicas minimum. TLS terminates here; certificates are
managed by cert-manager and renew automatically 30 days before expiry.

```
kubectl get ingress -n prod
kubectl logs -n platform deploy/ingress-nginx --tail=200
```

## Rate limiting

Applied at the ingress, not in the services. Defaults: 100 req/min per IP for the storefront,
20 req/min for auth endpoints. Review spam floods are handled here — see
`services/reviews-service.md`.

## Network policies

Default deny between namespaces. A new service needs an explicit policy to reach Postgres or
Redis. "It works in dev but not prod" is very often a missing network policy — dev runs a
looser default.

## Internal traffic

Service-to-service uses cluster DNS (`<service>.<namespace>.svc.cluster.local`). The internal
admin API additionally requires mTLS — see `reference/ports.md`.

## Symptoms worth knowing

- **502 from the ingress** — no healthy pods behind the service
- **504** — backend too slow, check the service's own latency
- **Cert warnings** — cert-manager failed to renew; check its logs before anything else
