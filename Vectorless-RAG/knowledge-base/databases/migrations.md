# Database Migrations

Schema changes run through the `ci/migrate` pipeline. Migrations are forward-only by default
and must be backwards compatible with the currently deployed code (expand/contract pattern).

## Running a migration

```
ci/migrate --service orders --env prod
```

Migrations run inside a transaction where possible. Index creation uses
`CREATE INDEX CONCURRENTLY`, which cannot run in a transaction — those are flagged and run
separately.

## Rollback procedure for a failed migration

This is the part people get wrong under pressure. Do it in this order:

1. **Stop the deploy pipeline** so no further migrations run: `ci/deploy --pause`.
2. **Check whether the migration actually applied** — a failed migration may be partially
   applied if it created an index concurrently:
   ```
   ci/migrate status --service orders --env prod
   ```
3. **Apply the down-migration** if one exists:
   ```
   ci/migrate down --service orders --env prod --steps 1
   ```
4. **If no down-migration exists** (common for expand/contract), do **not** hand-edit the
   schema. Roll the *application* back instead — see `operations/rollbacks.md` — and fix
   forward in the next release.
5. **Only if the database is genuinely corrupt**, restore from backup. That is a SEV-1 and
   requires a second engineer — see `databases/backups-and-restore.md`.

Never run `ci/migrate down` on production without an incident channel open.

## Long migrations

Anything expected to take over 5 minutes must run in a maintenance window — see
`operations/maintenance-windows.md`.
