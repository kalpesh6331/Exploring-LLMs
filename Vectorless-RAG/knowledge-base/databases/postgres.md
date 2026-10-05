# Postgres

Primary relational store for ShopFast. Self-managed on Kubernetes (deployment `postgres`),
one primary + one hot standby per environment. The `pgvector` extension is enabled.

Owned by the **Platform team**.

## Connection limits

Connection limits differ per environment. Check which environment you are actually in before
quoting a number — this trips people up constantly.

### Production
- `max_connections` = **200**
- PgBouncer pool size = 180, leaving 20 for admin/maintenance
- Alert fires at 170 active connections

### Staging
- `max_connections` = **50**
- No PgBouncer — services connect directly
- Alert fires at 40 active connections

### Development
- `max_connections` = **20**
- Shared by all developers; expect contention
- No alerting

## "Too many connections"

If services report `FATAL: too many connections`, something is leaking. Check current usage:

```
kubectl exec -n prod deploy/postgres -- psql -U shopfast -c "SELECT count(*) FROM pg_stat_activity;"
```

The usual culprit is the `orders` service after a deploy — restart it with
`kubectl rollout restart deploy/orders -n prod`. See `services/orders-service.md`.

## Failover

Failover to the standby is **manual**. Promoting the standby takes about 90 seconds, during
which writes fail. See `incidents/postmortem-2026-05-db-failover.md` for what that looked
like in practice.

## Disk full

Old WAL files are usually the cause. Page Platform on-call — do **not** delete WAL manually.

## Related
- Backups and restore: `databases/backups-and-restore.md`
- Schema changes: `databases/migrations.md`
