# Development Environment

## What you need

- Docker
- `kubectl` and `helm`
- The `ci` CLI (`brew install shopfast/tap/ci`)
- SSO configured

## The model

You do **not** run the whole platform locally — it is a dozen services plus datastores. You
run the one service you are changing and point it at the shared `dev` environment for
everything else.

```
ci dev --service orders
```

This port-forwards dependencies and injects dev credentials.

## Datastores

Local Postgres and Redis run in Docker for unit tests only. Anything integration-shaped runs
against `dev`.

Remember `dev` Postgres allows only **20 connections** total, shared across everyone — see
`databases/postgres.md`. If you cannot connect, someone is probably leaking; ask in
`#engineering` rather than restarting shared infrastructure.

## Tests

```
ci test --service orders          # unit
ci test --service orders --integration
```

Integration tests need `dev` access and are slower. Run unit tests before every push.
