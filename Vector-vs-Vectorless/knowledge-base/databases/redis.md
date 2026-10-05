# Redis

Cache and ephemeral store. Used for sessions, carts, payment token cache, and the
notifications dead-letter queue. Deployment `redis` in each environment.

Redis is **not** a durable store. Anything that must survive a restart belongs in Postgres.

## Restart

```
kubectl rollout restart deploy/redis -n prod
```

Restarting Redis clears all carts and logs customers out (sessions are cached here). Never do
this during peak hours. See `services/cart-service.md`.

## Memory pressure

Eviction policy is `allkeys-lru` with a 4 GB limit in production. When memory is tight you
will see cart data evicted first, because it has the largest footprint.

Check usage:
```
kubectl exec -n prod deploy/redis -- redis-cli INFO memory
```

## What lives where

- `sess:*` — auth sessions (TTL 24h)
- `cart:*` — carts (TTL 30d)
- `tok:*` — payment tokens (TTL 15m)
- `dlq:notifications` — failed notification sends
