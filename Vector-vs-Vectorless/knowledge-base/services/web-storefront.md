# Web Storefront

The customer-facing storefront (Next.js), served behind the NGINX ingress. Deployment `web`
in `prod`. Owned by the **Web team**.

## Restart

```
kubectl rollout restart deploy/web -n prod
```

## Build & deploy notes

The storefront is statically built at deploy time; a config change requires a redeploy, not
just a restart. Assets are served from the CDN — a stale asset after deploy usually means the
CDN cache wasn't invalidated. See `infrastructure/object-storage.md`.

## Health check
`GET /healthz` on port **3000**.

## Common issues

- **Blank page after deploy** — almost always a CDN cache/invalidation problem, not the pods.
- **Slow first paint** — check whether `search` or `pricing` is timing out; the homepage
  blocks on pricing.
- **Session lost on refresh** — Redis session store; see `databases/redis.md`.
