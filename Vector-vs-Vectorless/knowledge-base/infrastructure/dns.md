# DNS

DNS for shopfast.example is hosted with our cloud provider and managed in Terraform. Nobody
should be editing records by hand in the console — if you do, the next terraform apply will
revert it and you will spend an afternoon confused.

Public records point at the CDN, which fronts the load balancer. Internal service discovery
does not use public DNS at all; it uses cluster DNS inside Kubernetes.

TTLs are deliberately short (300 seconds) on records that point at infrastructure we might
need to move in a hurry, and longer (3600) on things that never change, like MX records.
Before a planned migration, drop the TTL a day ahead so the cutover is quick.

Certificate validation records are managed by cert-manager and must not be deleted, even
though they look like leftover junk. Deleting them breaks renewal silently, and you find out
30 days later when the certificate expires.

If DNS resolution fails cluster-wide, it is almost always CoreDNS rather than the provider.
Check CoreDNS pods in the platform namespace first.
