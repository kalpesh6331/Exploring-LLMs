# Shipping Service

Rate quotes, label generation, and carrier tracking. Deployment `shipping` in `prod`.
Owned by the **Orders team**.

Restart: `kubectl rollout restart deploy/shipping -n prod`. Health on port 8080.

## Carriers

Three carriers are integrated. Each has its own credentials and its own failure mode:

| Carrier | Used for | Fails as |
|---------|----------|----------|
| UPS | domestic standard | timeouts |
| FedEx | domestic express | 4xx on bad addresses |
| DHL | international | slow label generation |

If one carrier is down, quotes still return from the others — the customer just sees fewer
options. This is not an incident unless **all** carriers fail.

## Label generation stuck

Labels generate asynchronously. A stuck label is usually an address validation failure, not a
carrier outage. Check `shipping` logs for `address_invalid` before paging anyone.
