# Monitoring and Alerting

Prometheus for metrics, Loki for logs, Tempo for traces, Grafana on top. Alertmanager routes
to PagerDuty.

## Dashboards

- **Service overview** — request rate, error rate, p50/p99 latency per service
- **Golden signals** — the one to open first during an incident
- **Business** — checkout conversion, orders per minute (fastest way to confirm customer
  impact)

## Alert philosophy

Alert on **symptoms**, not causes. "Checkout error rate above 2%" is a good alert. "CPU above
80%" is not — it wakes people for something that may not matter.

Every alert must link to a runbook. An alert without a runbook gets deleted at the monthly
review.

## Known gap

We have almost no **client-side** monitoring. Every server signal looked green during the
July 2026 CDN incident while customers saw a blank page. Work is in progress — see
`incidents/postmortem-2026-07-cdn-misconfig.md`.

## Silencing

Silence noisy alerts during planned work, with an expiry. Silences without an expiry are
deleted weekly; a permanently silenced alert is just a deleted alert with extra steps.
