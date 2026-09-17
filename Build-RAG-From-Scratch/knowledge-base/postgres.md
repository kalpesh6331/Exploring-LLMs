# Postgres — Runbook

The primary database is a self-managed Postgres in the `prod` namespace
(deployment `postgres`). The `pgvector` extension is enabled.

## Take a manual backup
Backups run nightly, but to take a manual one before a risky change:

```
kubectl exec -n prod deploy/postgres -- pg_dump -U shopfast shopfast > backup.sql
```

## Restore from a backup
Restores are destructive — get a second engineer and confirm the target.

```
kubectl exec -i -n prod deploy/postgres -- psql -U shopfast shopfast < backup.sql
```

## "Too many connections" errors
The connection limit is 200. If services report `FATAL: too many connections`,
a service is likely leaking connections. Check current connections:

```
kubectl exec -n prod deploy/postgres -- psql -U shopfast -c "SELECT count(*) FROM pg_stat_activity;"
```

The usual culprit is the `orders` service after a deploy — restart it with
`kubectl rollout restart deploy/orders -n prod`.

## Disk full
If the Postgres pod is out of disk, old WAL files are usually the cause. Page
Platform on-call — do NOT delete WAL files manually.
