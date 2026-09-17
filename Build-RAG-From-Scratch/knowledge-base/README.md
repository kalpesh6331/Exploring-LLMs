# ShopFast Platform — Runbooks

Internal operations docs for **ShopFast**, our e-commerce platform.
Everything runs on Kubernetes (namespace `prod`), fronted by an NGINX ingress.

## Services
- **web** — the storefront (Next.js)
- **payments** — the payments service (Python), talks to Stripe
- **orders** — order management API (Go)
- **postgres** — primary database (managed by us, `pgvector` enabled)
- **redis** — cache + session store

## Conventions
- All services live in the `prod` namespace.
- Deploys go through the `ci/deploy` pipeline (see `deployments.md`).
- On-call rotation and severities are in `incident-response.md`.
- Never run write/destructive commands against prod without a second engineer.

## Quick links
- Restarting a service or debugging payments → `payments-service.md`
- Deploying / rolling back → `deployments.md`
- Something is on fire → `incident-response.md`
- Database backups / restores → `postgres.md`
