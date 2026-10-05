# Audit Logging

## What is audited

- Every Vault secret read and write
- Kubernetes API calls that mutate state
- Production database access
- Admin API calls
- Authentication events (success and failure)
- Break-glass usage

## Properties

Audit logs are **append-only and immutable**, written to a separate account that application
engineers cannot write to. Retention is **2 years** — see `databases/data-retention.md`.

If audit logs could be edited by the people being audited, they would not be audit logs.

## Querying

```
ci/audit query --actor alice@shopfast.example --since 24h
```

Access to audit queries is itself audited.

## Alerts

Automatic alerts on: break-glass use, failed auth spikes, secret reads outside business hours
by a human account, and any change to the audit configuration itself.

## During an incident

Audit logs answer "what changed and who changed it" faster than asking around. Check them
early — see `incidents/incident-response.md`.
