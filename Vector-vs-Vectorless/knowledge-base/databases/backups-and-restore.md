# Backups and Restore

## Schedule

- Postgres: full nightly dump at **02:00 UTC**, WAL archived continuously
- Retention: **30 days** of nightly dumps, 7 days of WAL
- Redis: not backed up (ephemeral by design)
- Elasticsearch: not backed up — rebuilt from Postgres via reindex

## Manual backup before a risky change

```
kubectl exec -n prod deploy/postgres -- pg_dump -U shopfast shopfast > backup.sql
```

Take one before any migration you are not confident about.

## Restore

Restores are **destructive**. Get a second engineer and confirm the target environment out
loud before running anything.

```
kubectl exec -i -n prod deploy/postgres -- psql -U shopfast shopfast < backup.sql
```

A production restore is automatically a **SEV-1** and requires an incident commander.

## Point-in-time recovery

PITR is possible within the WAL retention window (7 days) but has never been exercised in
production. Treat the runbook as untested — see the open action item in
`incidents/postmortem-2026-05-db-failover.md`.
