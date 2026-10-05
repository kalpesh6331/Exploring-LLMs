# Key Rotation

Written after the March 2026 checkout outage, which was caused by a bad rotation —
see `incidents/postmortem-2026-03-checkout-outage.md`.

## The rule

**Write-then-swap. Never delete-then-create.** The new value must exist and be verified
before anything starts using it, and the old value stays until the new one is confirmed live.

## Schedule

| Credential | Frequency |
|------------|-----------|
| Payment processor keys (Stripe, Adyen) | quarterly |
| JWT signing key (auth) | annually, or on incident |
| Internal service credentials | annually |
| Database passwords | annually |
| TLS certificates | automatic (cert-manager) |

## Procedure

1. Write the new secret alongside the old: `vault kv put secret/prod/<svc>/<name>-next ...`
2. **Verify it reads back correctly.**
3. Swap the alias so services resolve the new value.
4. Roll the deployment and confirm health before continuing.
5. Only then remove the old value.

## JWT signing key — read this first

Rotating the auth signing key **logs out every customer immediately**. Only rotate it during
a security incident, and tell Support before you do — see `services/auth-service.md`.

## If rotation fails halfway

Stop. Restore the old value. Do not attempt to roll forward during customer impact.
