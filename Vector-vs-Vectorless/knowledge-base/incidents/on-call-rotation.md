# On-Call Rotation

On-call is managed in PagerDuty. One week per rotation, handover Mondays at 10:00 local.

## The rotations

| Rotation | Covers | Page it for |
|----------|--------|-------------|
| **Payments on-call** | payments, payments-gateway | **checkout down**, card failures, settlement issues |
| Platform on-call | Kubernetes, ingress, Postgres, Redis, auth, notifications | cluster, database, networking, login |
| Web on-call | storefront, cart, reviews | storefront errors, cart problems |
| Orders on-call | orders, inventory, shipping | stuck orders, stock, labels |
| Search on-call | search, Elasticsearch | search down or degraded |

## How to page

Trigger the matching service in PagerDuty, or in Slack: `/page payments`.

**If checkout is down, page the Payments on-call.** That is the single most common page and
it is always at least a SEV-2 — see `incidents/severity-levels.md`.

If you genuinely cannot tell which rotation owns the problem, page **Platform** — they can
route. Do not page everyone.

## Escalation

No ack in 15 minutes escalates to the rotation's secondary, then to the engineering lead.
See `incidents/escalation-paths.md`.

## Out of hours

Only SEV-1 and SEV-2 page out of hours. SEV-3 waits for business hours — genuinely, do not
wake someone for a SEV-3.
