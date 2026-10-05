# Maintenance Windows

Standard window: **Tuesdays 02:00–04:00 UTC**. Lowest traffic of the week.

Anything that takes production write capacity offline needs a window:
- Long migrations (over 5 minutes)
- Postgres major version upgrades
- Node pool replacement
- Elasticsearch cluster restarts

## Requesting a window

Post in `#engineering` at least **48 hours** ahead with: what you are doing, expected impact,
rollback plan, and who is on standby. Silence is not approval — get an explicit ack from the
Platform team.

## Customer communication

If customers will see degradation, Support must be told 24 hours ahead so they can prepare a
status page notice. Ops does not post to the status page directly.

## Emergency maintenance

During a SEV-1 you do not need a window. You do need an IC and an incident channel.
