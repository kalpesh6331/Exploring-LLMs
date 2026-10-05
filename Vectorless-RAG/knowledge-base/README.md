# ShopFast Engineering Knowledge Base

Internal documentation for **ShopFast**, our e-commerce platform. Everything runs on
Kubernetes (namespace `prod`), fronted by a CDN and an NGINX ingress.

> ⚠️ This is **fake, synthetic data** for demo purposes. No real company, no real customers.

## How this is organised

| Area | What's in it |
|------|--------------|
| `services/` | One doc per service — restart, health, common issues, dependencies |
| `infrastructure/` | Kubernetes, networking, DNS, Terraform, CI/CD, secrets, storage, monitoring |
| `databases/` | Postgres, Redis, Elasticsearch, migrations, backups, retention |
| `operations/` | Deploys, freezes, rollbacks, scaling, maintenance, capacity, cost |
| `incidents/` | Incident process, severities, on-call, escalation, postmortems |
| `security/` | Access control, PCI, vulnerabilities, audit logging, key rotation |
| `reference/` | Error codes, ports, SLOs, ownership, glossary, API conventions |
| `onboarding/` | New engineer setup, dev environment, teams, tooling, first week |

## Quick links

- Something is on fire → `incidents/incident-response.md`
- Who do I page → `incidents/on-call-rotation.md`
- Restarting or debugging a service → `services/`
- Deploying or rolling back → `operations/deployments.md`, `operations/rollbacks.md`
- What does this error code mean → `reference/error-codes.md`
- Who owns this service → `reference/service-ownership.md`
- New here → `onboarding/README.md`

## Conventions

- All services live in the `prod` namespace
- Deploys go through `ci/deploy`; production deploys are never automatic
- Never run destructive commands against prod without a second engineer
