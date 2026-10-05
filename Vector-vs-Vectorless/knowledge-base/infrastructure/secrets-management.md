# Secrets Management

All secrets live in **Vault**. Kubernetes Secrets are populated from Vault by the secrets
operator — they are never created by hand and never committed to git.

## Reading a secret

```
vault kv get secret/prod/payments/stripe
```

Access is role-based and audited. Every read is logged — see `security/audit-logging.md`.

## Adding a secret

```
vault kv put secret/prod/<service>/<name> value=@file
```

Then reference it in the service's `ExternalSecret` manifest. The operator syncs within 60
seconds.

## Rotation

Quarterly for processor credentials, annually for internal service credentials, immediately
on any suspected compromise. Rotation is **write-then-swap**, never delete-then-create —
this exact mistake caused the March 2026 checkout outage
(`incidents/postmortem-2026-03-checkout-outage.md`). Procedure:
`security/key-rotation.md`.

## If a secret leaks

Treat it as a security incident immediately: rotate first, investigate second. See
`security/incident-security-playbook.md`.
