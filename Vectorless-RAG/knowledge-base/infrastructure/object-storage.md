# Object Storage and CDN

Static assets, product images, and log archives live in object storage, fronted by the CDN.

## Buckets

| Bucket | Contents | Public? |
|--------|----------|---------|
| `shopfast-assets` | storefront JS/CSS/images | yes, via CDN |
| `shopfast-products` | product imagery | yes, via CDN |
| `shopfast-logs-cold` | archived logs | no |
| `shopfast-backups` | database dumps | no, encrypted |

Never make a bucket public directly. Public access is only ever through the CDN.

## Cache invalidation

The deploy pipeline invalidates the asset cache automatically. This was added after the
July 2026 incident — see `incidents/postmortem-2026-07-cdn-misconfig.md`.

Manual invalidation:
```
ci/cdn invalidate --path "/assets/*"
```

Propagation takes up to 5 minutes globally. A "blank storefront after deploy" is nearly
always this.

## Lifecycle

Log archives move to cold storage after 30 days and are deleted after a year, per
`databases/data-retention.md`.
