# Deployments & Rollbacks

All ShopFast services deploy through the `ci/deploy` pipeline. Deploys are
image-tag based; every deploy is a new immutable tag.

## Deploy a service
Trigger the pipeline with the service name and the image tag:

```
ci/deploy --service payments --tag v1.42.0
```

The pipeline runs tests, pushes the image, and updates the deployment in `prod`.

## Roll back a bad deploy
To roll back to the previous version quickly:

```
kubectl rollout undo deploy/<service> -n prod
```

For example, to roll back payments:

```
kubectl rollout undo deploy/payments -n prod
```

To roll back to a specific revision, first list revisions:

```
kubectl rollout history deploy/payments -n prod
```

then `kubectl rollout undo deploy/payments --to-revision=<N> -n prod`.

## Deploy freeze
During a SEV-1 incident, all deploys are frozen. Only the incident commander can
lift the freeze. Never deploy during an active SEV-1.
