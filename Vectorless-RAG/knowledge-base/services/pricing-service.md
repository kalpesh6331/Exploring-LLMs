# Pricing Service

Computes final price: base price, promotions, regional tax, and currency conversion.
Deployment `pricing` in `prod`. Owned by the **Pricing team**.

Restart: `kubectl rollout restart deploy/pricing -n prod`. Health on port **8082**.

## Promotion cache

Promotions are cached in-process for **60 seconds**. A promotion change therefore takes up to
a minute to appear storefront-wide. This is deliberate — do not "fix" it by restarting pods
during a campaign launch, you will just stampede the database.

## Currency rates

Rates refresh hourly from an external feed. If the feed is stale for more than 6 hours the
service falls back to the last known good rates and raises a warning alert. Prices are never
served without a rate.

## Common issues
- **Wrong price shown** — nearly always the 60s promo cache, or a stale CDN page.
- **Tax wrong for a region** — check the region config, not the code.
