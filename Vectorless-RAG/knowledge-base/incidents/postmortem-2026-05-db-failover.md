# Postmortem — Database Failover, 2026-05-22

**Severity:** SEV-1
**Duration:** 22 minutes of write unavailability (03:41–04:03 UTC)
**Author:** Platform team

## Summary

The Postgres primary lost its underlying node during a spot-instance reclaim. Failover to the
standby is manual, so writes failed until an engineer promoted it.

## Impact

22 minutes with no writes: no orders created, no payments recorded. Reads continued from the
standby. Roughly 140 orders lost at a low-traffic hour. A small number of stock oversells
occurred because reservations are written synchronously but released asynchronously.

## Timeline (UTC)

- **03:41** — Node reclaimed. Primary disappears.
- **03:43** — Write error alerts fire, Platform on-call paged.
- **03:48** — On-call acks; confirms primary is gone, not partitioned.
- **03:55** — Standby promoted manually.
- **04:01** — Applications reconnect after connection pools recycle.
- **04:03** — Writes confirmed healthy.

## Root cause

Postgres was running on a node pool that permitted spot instances, contrary to policy.
Combined with manual-only failover, a routine reclaim became a SEV-1.

## What went well

The standby was healthy and current — replication lag was under a second. Data loss was
limited to in-flight transactions.

## Action items

| Item | Owner | Due | Status |
|------|-------|-----|--------|
| Move Postgres to on-demand node pool only | Platform | 2026-05-29 | Done |
| Automate failover with a health-checked promoter | Platform | 2026-08-01 | **In progress** |
| Make reservation release synchronous | Orders | 2026-07-15 | Won't fix — accepted risk |
| Exercise point-in-time recovery in staging | Platform | 2026-08-15 | **Open — PITR still untested** |
