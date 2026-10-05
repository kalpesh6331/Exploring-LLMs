# Rollbacks

Rolling back is the default response to a bad deploy. Do it first, debug afterwards.

## Roll back to the previous version

```
kubectl rollout undo deploy/<service> -n prod
```

For example:
```
kubectl rollout undo deploy/payments -n prod
```

## Roll back to a specific revision

List revisions, then target one:

```
kubectl rollout history deploy/payments -n prod
kubectl rollout undo deploy/payments --to-revision=<N> -n prod
```

## When a rollback is NOT safe

- **A migration already ran.** Rolling back the app may leave it incompatible with the new
  schema. See `databases/migrations.md` — with expand/contract this is usually fine, but
  check.
- **Data was written in a new format.** Rolling back can make that data unreadable.

If either applies, say so in the incident channel before rolling back.

## After a rollback

- Confirm error rate recovers
- Pin the bad tag so nobody redeploys it: `ci/deploy --block-tag <tag>`
- Open a postmortem if it was customer-visible — see `incidents/postmortem-process.md`
