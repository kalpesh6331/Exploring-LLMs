# Search Service

Product search and autocomplete, backed by Elasticsearch. Deployment `search` in `prod`.
Owned by the **Search team**.

## Restart
```
kubectl rollout restart deploy/search -n prod
```
Health on port **8080**.

## Reindexing

A full catalogue reindex takes roughly **40 minutes** and is safe to run during business
hours — it writes to a new index and flips an alias at the end.

```
ci/reindex --full --confirm
```

Never run two full reindexes concurrently; the second will fail on the alias flip and leave
a dangling index. Clean up with `ci/reindex --gc`.

## Common issues

- **Stale results** — the incremental indexer lagging. Check consumer lag before reindexing.
- **Search 500s** — usually Elasticsearch cluster health; see `databases/elasticsearch.md`.
- **Autocomplete slow** — the suggest index is separate and rebuilt nightly.
