# Severity Levels

| Severity | Definition | Response | Deploy freeze? |
|----------|------------|----------|----------------|
| **SEV-1** | Full outage or data loss. Customers cannot use ShopFast. | Page everyone, IC required, status page updated | **Yes, automatic** |
| **SEV-2** | Major feature broken (e.g. checkout down). Revenue impacting. | Page the owning rotation, IC required | No, but be careful |
| **SEV-3** | Minor or degraded, no revenue impact. | Business hours only | No |

## Examples

- Checkout completely failing → **SEV-2** minimum, SEV-1 if it persists past 30 minutes
- Site fully down → SEV-1
- Search returning stale results → SEV-3
- Reviews service down → SEV-3 (non-critical, see `services/reviews-service.md`)
- Customer data exposed → SEV-1 regardless of scale, and involve Security immediately

## Escalating a severity

Anyone can raise a severity. Only the IC can lower one. If you are unsure between two levels,
pick the higher one — it is easier to stand people down than to spin them up.
