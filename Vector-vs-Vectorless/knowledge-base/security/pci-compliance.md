# PCI Compliance

ShopFast is PCI-DSS SAQ-A eligible because **we never touch raw card data**. Cards are
tokenised in the browser by the processor's SDK; our systems only ever see a token.

## The hard rules

- Never log a card number, CVV, or full token. Log the last 4 digits at most.
- Never store card data in Postgres, Redis, or anywhere else. Payment tokens are cached for
  **15 minutes** only — see `databases/data-retention.md`.
- Never send card data to a third party, including error trackers and analytics.
- The payments path is scoped: only `payments` and `payments-gateway` may talk to the
  processor.

If you think you have found card data in a log, treat it as a security incident immediately —
`security/incident-security-playbook.md`.

## Audit

External assessment annually. Evidence needed: access reviews, change management records,
vulnerability scan results, and audit logs (retained 2 years, see
`security/audit-logging.md`).

## Changes that affect scope

Anything touching the payments path needs Security sign-off before design, not after
implementation. That includes adding a new dependency to those services.
