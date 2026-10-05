# Service Level Objectives

Measured over a rolling 30-day window. Breaching an SLO does not automatically create an
incident, but two consecutive breaches trigger a review.

| Service | Availability SLO | Latency SLO (p99) | Error budget |
|---------|------------------|-------------------|--------------|
| web (storefront) | 99.9% | 800 ms | 43 min/month |
| payments | 99.95% | 500 ms | 21 min/month |
| payments-gateway | 99.9% | 1200 ms | 43 min/month |
| **orders** | **99.9%** | **400 ms** | **43 min/month** |
| cart | 99.5% | 300 ms | 3.6 h/month |
| auth | 99.95% | 250 ms | 21 min/month |
| search | 99.5% | 600 ms | 3.6 h/month |
| inventory | 99.9% | 400 ms | 43 min/month |
| pricing | 99.9% | 350 ms | 43 min/month |
| notifications | 99.0% | n/a (async) | 7.2 h/month |
| reviews | 99.0% | 1000 ms | 7.2 h/month |
| shipping | 99.5% | 1500 ms | 3.6 h/month |

Non-critical services (reviews, notifications) intentionally have looser SLOs — see
`services/reviews-service.md`.

Ownership for each service is in `reference/service-ownership.md`.
