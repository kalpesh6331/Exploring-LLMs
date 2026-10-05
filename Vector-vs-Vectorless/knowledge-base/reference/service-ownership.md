# Service Ownership

Who owns what. The owning team is responsible for the on-call rotation, the SLO, and the
runbook for that service.

| Service | Owning team | Slack channel |
|---------|-------------|---------------|
| web (storefront) | Web | `#team-web` |
| cart | Web | `#team-web` |
| reviews | Web | `#team-web` |
| payments | Payments | `#team-payments` |
| payments-gateway | Payments | `#team-payments` |
| **orders** | **Orders** | **`#team-orders`** |
| inventory | Orders | `#team-orders` |
| shipping | Orders | `#team-orders` |
| auth | Platform | `#team-platform` |
| notifications | Platform | `#team-platform` |
| search | Search | `#team-search` |
| pricing | Pricing | `#team-pricing` |
| postgres / redis / elasticsearch | Platform | `#team-platform` |
| Kubernetes / ingress / CI-CD | Platform | `#team-platform` |

If you cannot tell who owns something, ask in `#engineering` — do not guess and page the
wrong rotation. On-call mapping is in `incidents/on-call-rotation.md`.
