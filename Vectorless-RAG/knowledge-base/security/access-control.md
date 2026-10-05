# Access Control

## Principles

Least privilege, short-lived credentials, everything audited. No shared accounts, ever.

## Human access

SSO with mandatory MFA. Cluster access issues short-lived credentials (8 hours) — there are
no static kubeconfigs.

| Role | Can do | Who |
|------|--------|-----|
| `viewer` | read non-sensitive resources | all engineers |
| `operator` | restart, scale, read logs | team members for their services |
| `admin` | everything including secrets | Platform team only |
| `break-glass` | full cluster admin | 2 people, audited, alerts on use |

## Production database access

Direct production database access requires an approved ticket and is time-boxed to 4 hours.
Read-only by default; write access needs a second approver.

## The internal admin API

Reachable only from inside the cluster or over VPN, and requires mutual TLS. It listens on
port 8443 — see `reference/ports.md`. It is never exposed publicly, under any circumstances.

## Offboarding

Access is revoked within **4 hours** of an employee leaving, automatically via the identity
provider. Vault tokens and cluster credentials expire on their own within 8 hours.

## Break-glass

Break-glass use pages the security team automatically and requires a written justification
within 24 hours.
