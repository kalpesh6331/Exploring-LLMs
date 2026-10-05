# Capacity Planning

Reviewed quarterly, plus ahead of every major traffic event.

## Baseline

Normal peak is roughly 2,400 requests/second at the ingress, around 19:00–21:00 local in our
largest market. Black Friday peak has historically been **6–8x** normal.

## Headroom targets

- Cluster CPU: stay under 60% at peak, so an AZ can be lost without a capacity event
- Postgres connections: under 170 of 200 in production (see `databases/postgres.md`)
- Redis memory: under 3 GB of the 4 GB limit

## Before a traffic event

1. Pre-scale web, cart, pricing and search (see `operations/scaling.md`)
2. Raise HPA minimums, not just replica counts
3. Confirm the deploy freeze is in place — `operations/deploy-freeze.md`
4. Warm the CDN with the campaign pages
5. Put both Platform and the owning team on standby, not just on-call

## What has bitten us

Pre-scaling the app tier but forgetting the database connection pool. The app scales, opens
more connections, and hits `max_connections`. Scale the pool first.
