# Team Structure

Five engineering teams, each owning services end to end — including the on-call for them.

| Team | Owns | Slack |
|------|------|-------|
| **Web** | storefront, cart, reviews | `#team-web` |
| **Payments** | payments, payments-gateway | `#team-payments` |
| **Orders** | orders, inventory, shipping | `#team-orders` |
| **Platform** | Kubernetes, ingress, databases, auth, notifications, CI/CD | `#team-platform` |
| **Search** | search, Elasticsearch | `#team-search` |
| **Pricing** | pricing | `#team-pricing` |

Security is a shared function, not a team that owns services. They review, they do not
implement.

## You build it, you run it

The team that owns a service carries the pager for it. There is no separate ops team — the
Platform team owns platform, not everyone else's incidents.

## Channels

- `#engineering` — general, ask anything
- `#incidents` — incident declarations only, keep it clean
- `#deploys` — automated deploy notifications

Full service→team mapping: `reference/service-ownership.md`.
