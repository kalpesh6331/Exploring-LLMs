# Port Reference

Ports used across ShopFast services. Internal only unless marked public.

| Service | Port | Exposure | Notes |
|---------|------|----------|-------|
| web (storefront) | 3000 | public (via ingress) | Next.js |
| payments | 8080 | internal | health `/healthz` |
| payments-gateway | 8081 | internal | different from payments |
| orders | 8080 | internal | |
| cart | 8080 | internal | |
| auth | 8080 | internal | |
| search | 8080 | internal | |
| inventory | 8080 | internal | |
| notifications | 8080 | internal | |
| pricing | 8082 | internal | |
| reviews | 8080 | internal | |
| shipping | 8080 | internal | |
| **internal admin API** | **8443** | **internal, mTLS only** | **Never expose publicly. Used by the support tool.** |
| postgres | 5432 | internal | |
| redis | 6379 | internal | |
| elasticsearch | 9200 | internal | |
| prometheus | 9090 | internal | |

The **internal admin API listens on port 8443** and requires mutual TLS. It is reachable only
from inside the cluster and from the VPN — see `security/access-control.md`.
