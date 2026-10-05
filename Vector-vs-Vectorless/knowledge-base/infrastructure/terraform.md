# Terraform

All infrastructure is defined in the `shopfast-infra` repository. Manual changes in the cloud
console are not permitted — they get reverted on the next apply.

## Layout
```
environments/prod/
environments/staging/
environments/dev/
modules/
```

## Workflow

1. Branch, change, open a PR
2. CI runs `terraform plan` and posts the plan on the PR
3. **A human reads the plan.** Destroy operations require a second approver.
4. Merge triggers `terraform apply`

## State

Remote state in object storage with locking. If a run dies mid-apply the lock persists:

```
terraform force-unlock <LOCK_ID>
```

Only force-unlock when you are certain no apply is running. Breaking a live lock corrupts
state.

## Dangerous resources

Anything with `prevent_destroy = true` — databases, storage buckets, the DNS zone. If a plan
proposes destroying one of these, stop and ask. That is almost always a mistake in the
configuration, not an intended change.
