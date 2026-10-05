# Data Retention

What we keep, and for how long. Driven by legal and PCI requirements — do not change these
without sign-off from Security. See `security/pci-compliance.md`.

| Data | Retention | Notes |
|------|-----------|-------|
| Orders | 7 years | Legal requirement |
| Payment tokens | 15 minutes | Never store raw card data |
| Customer accounts | Until deletion request | GDPR erasure within 30 days |
| Application logs | 30 days | Then archived to cold storage for 1 year |
| Audit logs | 2 years | Immutable, see `security/audit-logging.md` |
| Carts | 30 days inactive | Ephemeral, Redis only |
| Analytics events | 13 months | Aggregates kept indefinitely |

Deletion requests are processed by a weekly job. A customer asking "delete my data" starts
in the support tool, not in the database.
