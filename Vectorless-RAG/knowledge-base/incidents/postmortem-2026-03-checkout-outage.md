# Postmortem — Checkout Outage, 2026-03-14

**Severity:** SEV-1
**Duration:** 47 minutes (14:12–14:59 UTC)
**Author:** Payments team

## Summary

A secret rotation removed the `STRIPE_API_KEY` from the payments namespace before the new
value was written. Payments pods entered `CrashLoopBackOff` and checkout failed completely.

## Impact

Checkout unavailable for 47 minutes at peak. Approximately 3,100 failed checkouts and an
estimated £68,000 in deferred revenue. No data loss, no card data exposure.

## Timeline (UTC)

- **14:10** — Quarterly key rotation runs.
- **14:12** — Payments pods begin crash-looping. Error rate hits 100%.
- **14:14** — Alert fires, Payments on-call paged.
- **14:19** — On-call acks, declares SEV-1, deploys freeze automatically.
- **14:26** — Root cause found: rotation job deletes then writes; the write failed silently.
- **14:41** — Key restored manually from Vault.
- **14:52** — Pods healthy, error rate recovering.
- **14:59** — Checkout confirmed normal, incident closed.

## Root cause

The rotation job used delete-then-create rather than an atomic update, and did not verify the
new secret existed before allowing pods to restart. The failure was silent.

## What went well

Alerting fired in two minutes. The automatic deploy freeze prevented a well-meaning engineer
from shipping an unrelated change into the outage.

## Action items

| Item | Owner | Due | Status |
|------|-------|-----|--------|
| Make rotation atomic (write-then-swap) | Platform | 2026-03-28 | Done |
| Verify secret exists before pod restart | Platform | 2026-03-28 | Done |
| Alert on payments CrashLoopBackOff specifically | Payments | 2026-04-11 | Done |
| Document rotation runbook | Security | 2026-04-11 | Done — `security/key-rotation.md` |
