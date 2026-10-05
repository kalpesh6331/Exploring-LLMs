# Glossary

**Alias** — an Elasticsearch pointer to a concrete index, so reindexing can swap atomically.

**Deploy freeze** — a period where deploys are blocked. See `operations/deploy-freeze.md`.

**DLQ** — dead-letter queue. Where failed notification sends end up.

**Error budget** — how much unavailability an SLO allows in a window.

**Expand/contract** — the safe schema-change pattern: add the new thing, migrate, then remove
the old thing in a later release.

**IC** — Incident Commander. The one person coordinating a SEV-1/SEV-2.

**PgBouncer** — connection pooler sitting in front of production Postgres.

**Reservation** — temporary stock hold created when an order is placed, 15 minutes.

**SEV** — severity level of an incident, SEV-1 through SEV-3.

**Sweeper** — the CronJob that releases expired stock reservations.

**WAL** — Postgres write-ahead log, used for replication and point-in-time recovery.
