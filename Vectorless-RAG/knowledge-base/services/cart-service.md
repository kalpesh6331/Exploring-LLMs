# Cart Service

Holds in-progress carts. Backed entirely by Redis — carts are **not** durable and expire
after 30 days of inactivity. Deployment `cart` in `prod`. Owned by the Web team.

Restart with `kubectl rollout restart deploy/cart -n prod`. Health on port 8080.

Because carts live in Redis only, a Redis flush loses every in-progress cart. This is
accepted — carts are considered disposable — but it does produce a visible drop in
conversion for a few hours, so never flush Redis during peak.

Cart merge (guest cart → logged-in cart) happens in `auth`, not here. If a customer reports
"my cart emptied when I logged in", start with `auth-service.md`.
