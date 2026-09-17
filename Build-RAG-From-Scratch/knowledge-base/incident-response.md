# Incident Response

## Severity levels
- **SEV-1** — full outage or data loss. Customers cannot use ShopFast. Page
  everyone; incident commander required; deploy freeze in effect.
- **SEV-2** — major feature broken (e.g. checkout down). Page the owning team's
  on-call.
- **SEV-3** — minor / degraded, no customer-facing outage. Handle in business hours.

## Who to page
On-call is managed in PagerDuty. The rotations are:
- **Payments on-call** — checkout, payments, Stripe issues
- **Platform on-call** — Kubernetes, ingress, Postgres, Redis
- **Web on-call** — storefront

To page the Payments on-call, trigger the "Payments" service in PagerDuty.

## During an incident
1. Declare severity in `#incidents` on Slack.
2. For SEV-1/SEV-2, assign an incident commander.
3. Freeze deploys for SEV-1 (see `deployments.md`).
4. Post updates every 15 minutes.
5. After resolution, write a postmortem within 48 hours.

## Postmortems
Blameless. Focus on what broke and how to prevent it, not who did it.
