# Cost Controls

Cloud spend is reviewed monthly by the Platform team.

Biggest line items, in order: compute (node pools), then egress, then object storage, then
managed services. Compute is roughly 60% of the bill.

Practical rules:

- Non-production environments scale to zero overnight (22:00–07:00 UTC) and on weekends.
  Staging comes back automatically; if you need it overnight, set the `keep-warm` label.
- Node pools use spot instances for stateless workloads only. Never for Postgres.
- Log retention is 30 days hot; anything longer goes to cold storage, which is ~10x cheaper.
  See `databases/data-retention.md`.
- Unattached volumes and old images are garbage collected weekly. If you need something kept,
  tag it `retain=true`.

Anything that will add more than $500/month needs a heads-up in `#engineering` before you
ship it.
