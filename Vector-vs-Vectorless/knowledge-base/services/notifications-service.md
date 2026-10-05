# Notifications Service

Sends transactional email and SMS (order confirmations, shipping updates, password resets).
Deployment `notifications` in `prod`. Owned by the **Platform team**.

Restart: `kubectl rollout restart deploy/notifications -n prod`. Health on port 8080.

Email goes through SendGrid; SMS through Twilio. Both are external and both fail
independently — a Twilio outage does not stop email.

## Retries and the dead-letter queue

Failed sends retry 5 times with exponential backoff, then land in a Redis dead-letter queue.
Drain it with:

```
ci/notifications drain-dlq --confirm
```

A growing DLQ is usually a bad template, not a provider outage. Check the template render
errors first.

## Do not

Do not replay the DLQ blindly after an incident — customers receive duplicate emails.
Sample it first.
