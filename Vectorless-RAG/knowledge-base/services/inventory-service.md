# Inventory Service

Tracks stock levels and reservations. Deployment `inventory` in `prod`. Owned by the
**Orders team**.

Restart: `kubectl rollout restart deploy/inventory -n prod`. Health on port 8080.

## Reservations

When an order is created, stock is *reserved* for **15 minutes**. If payment does not
complete in that window the reservation is released automatically by a sweeper job.

If the sweeper is down, stock appears unavailable even though nothing was sold. Check the
`inventory-sweeper` CronJob before escalating an "out of stock" complaint.

## Oversell

Oversell is possible during a Postgres failover, because reservations are written
synchronously but released asynchronously. This is a known, accepted risk — see
`incidents/postmortem-2026-05-db-failover.md`.
