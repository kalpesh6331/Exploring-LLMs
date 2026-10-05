# Auth Service

Handles login, sessions, and guest→customer cart merge. Deployment `auth` in `prod`.
Owned by the **Platform team**.

## Restart
```
kubectl rollout restart deploy/auth -n prod
```

## Sessions

Sessions are JWTs signed with a key from Vault, cached in Redis for revocation. Token TTL is
**24 hours**; refresh tokens last 30 days.

Rotating the signing key invalidates every active session — it logs out all customers. Only
do this during a security incident, and follow `security/key-rotation.md`.

## Health check
`GET /healthz` on port **8080**.

## Common issues

- **Everyone logged out at once** → signing key was rotated. Check the audit log.
- **Login loops** → clock skew between auth pods and the ingress; check node time sync.
- **Cart emptied on login** → the merge step failed; look for `merge_failed` in auth logs.
