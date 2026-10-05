# Reviews Service

Customer product reviews and ratings. Deployment `reviews` in `prod`. Owned by the Web team.

This is a **non-critical** service. If reviews are down the storefront degrades gracefully —
the product page renders without the reviews block. Reviews being down is a **SEV-3**, never
a SEV-1, even though it is customer visible.

Restart: `kubectl rollout restart deploy/reviews -n prod`. Health on port 8080.

Moderation is manual and handled by the support team through the admin API. Review spam
floods happen after big promotions; rate limiting is configured at the ingress, not in the
service.
