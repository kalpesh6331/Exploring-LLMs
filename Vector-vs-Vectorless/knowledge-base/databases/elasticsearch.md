# Elasticsearch

Backs product search and autocomplete. Three-node cluster per environment.

## Cluster health

```
kubectl exec -n prod deploy/elasticsearch -- curl -s localhost:9200/_cluster/health
```

- **green** — all good
- **yellow** — replicas unassigned; search still works, do not page anyone at 2am
- **red** — primary shards missing; search is broken, this is a SEV-2

Yellow after a node restart is normal and self-heals within a few minutes.

## Indices

- `products-v*` — the catalogue, written by the reindex job, read through the `products` alias
- `suggest-v*` — autocomplete, rebuilt nightly

Never write to an index directly; always go through the alias.

## Disk watermarks

Elasticsearch stops allocating shards at 85% disk and goes read-only at 95%. If search
suddenly refuses writes, check disk before anything else.

Related: `services/search-service.md`.
