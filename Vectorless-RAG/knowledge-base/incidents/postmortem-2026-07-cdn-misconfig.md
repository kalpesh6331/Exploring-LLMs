# Postmortem — CDN Misconfiguration, 2026-07-09

**Severity:** SEV-2
**Duration:** 1 hour 12 minutes (10:03–11:15 UTC)
**Author:** Web team

## Summary

A storefront deploy shipped with a changed asset path, and the CDN cache was not invalidated.
Customers received a mix of new HTML and old JavaScript, producing a blank page on roughly
40% of sessions.

## Impact

Storefront effectively unusable for affected sessions for 72 minutes. Checkout itself was
healthy — customers simply could not reach it.

## Timeline (UTC)

- **10:03** — Storefront v3.8.0 deployed.
- **10:09** — Support reports "blank page" from customers. No alert fired.
- **10:21** — Web on-call investigates; pods and health checks all green, which delayed
  diagnosis.
- **10:44** — Someone checks the browser console and finds 404s on JS assets.
- **10:58** — CDN cache invalidated manually.
- **11:15** — Confirmed recovered after propagation.

## Root cause

Deploys did not invalidate the CDN cache. Nothing monitored client-side errors, so every
server-side signal looked healthy while customers saw a broken page.

## What went well

Nothing about detection. Mitigation, once identified, was a single command.

## Action items

| Item | Owner | Due | Status |
|------|-------|-----|--------|
| Invalidate CDN as a deploy pipeline step | Web | 2026-07-16 | Done |
| Add client-side error rate monitoring | Web | 2026-08-30 | **In progress** |
| Alert on storefront JS 404s | Platform | 2026-08-30 | **Open** |
| Add "check the browser console" to the storefront runbook | Web | 2026-07-23 | Done |
