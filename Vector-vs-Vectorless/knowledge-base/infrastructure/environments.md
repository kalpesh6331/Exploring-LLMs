# Environments

| Environment | Purpose | Data | Who can deploy |
|-------------|---------|------|----------------|
| `dev` | shared developer sandbox | synthetic | anyone |
| `staging` | pre-production verification | anonymised copy of prod | anyone |
| `prod` | live customers | real | via `ci/deploy` only |

## Differences that bite people

- **Postgres connection limits differ per environment** — 200 in prod, 50 in staging, 20 in
  dev. See `databases/postgres.md`.
- **Network policies are stricter in prod.** "Works in dev" often means a missing policy.
- **Non-prod scales to zero overnight** (22:00–07:00 UTC) — see `operations/cost-controls.md`.
- **Staging has no PgBouncer**, so connection exhaustion shows up there first.

## Data in staging

Staging data is anonymised nightly from production. It is still customer-derived — treat it
as sensitive. Never copy production data into `dev`.

## Promotion path

`dev → staging → prod`. Skipping staging requires an incident and an IC.
