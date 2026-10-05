# Deployments

All ShopFast services deploy through the `ci/deploy` pipeline. Deploys are image-tag based;
every deploy produces a new immutable tag.

## Deploy a service

```
ci/deploy --service payments --tag v1.42.0
```

The pipeline runs unit tests, builds and pushes the image, runs **pre-deploy smoke tests**
against staging, then updates the deployment in `prod`.

## Flags

| Flag | Effect | When to use |
|------|--------|-------------|
| `--tag` | image tag to deploy | always |
| `--service` | which service | always |
| `--canary` | route 5% of traffic first | risky changes |
| `--skip-smoke` | **skips the pre-deploy smoke tests** | emergencies only |
| `--pause` | halt the pipeline | during an incident |
| `--dry-run` | print the plan, change nothing | when unsure |

**`--skip-smoke` skips the pre-deploy smoke tests.** It exists for genuine emergencies —
shipping a fix during an active incident — and every use is logged and reviewed. Do not use
it to get around a flaky test; fix the test.

## Canary deploys

```
ci/deploy --service payments --tag v1.42.0 --canary
```

Sends 5% of traffic to the new version for 10 minutes, then promotes automatically if error
rate stays flat. Canary is mandatory for payments-path services.

## After deploying

Watch the rollout and the error rate for at least 10 minutes. If it looks wrong, roll back
immediately — see `operations/rollbacks.md`. Rolling back is cheap; debugging in production
is not.

## Freezes
Deploys are blocked during a freeze. See `operations/deploy-freeze.md`.
