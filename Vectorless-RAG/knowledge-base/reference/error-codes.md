# Error Code Reference

Internal ShopFast error codes. These appear in API responses, logs, and alerts.

| Code | Meaning | Usual cause | First action |
|------|---------|-------------|--------------|
| ERR-1001 | Invalid request payload | Client bug | Check the request schema |
| ERR-1004 | Authentication failed | Expired/invalid token | See `services/auth-service.md` |
| ERR-2003 | Cart not found | Expired cart (30d TTL) | Expected, not an incident |
| ERR-2010 | Stock reservation failed | Sweeper lag or genuine oversell | See `services/inventory-service.md` |
| ERR-3007 | Pricing unavailable | Currency feed stale > 6h | See `services/pricing-service.md` |
| ERR-4002 | Order state transition invalid | Duplicate/late event | Check consumer acks |
| **ERR-5012** | **Payment gateway timeout** | **Downstream processor (Stripe/Adyen) slow or down** | **Check the processor status page before restarting anything — see `services/payments-gateway.md`** |
| ERR-5019 | Payment declined by processor | Genuine decline | Not an incident on its own |
| ERR-5023 | Settlement webhook backlog | Stuck webhook consumer | Drain the Redis queue |
| ERR-6001 | Search unavailable | Elasticsearch red | See `databases/elasticsearch.md` |
| ERR-7004 | Shipping quote failed | All carriers failing | See `services/shipping-service.md` |
| ERR-9000 | Internal server error | Unclassified | Check logs and traces |

A spike in **ERR-5012** specifically means the gateway is timing out talking to the card
processor. It is almost always upstream — restarting our pods will not help.
