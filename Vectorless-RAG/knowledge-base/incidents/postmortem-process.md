# Postmortem Process

Every SEV-1 and SEV-2 gets a written postmortem within **48 hours**. SEV-3 only if something
was genuinely surprising.

## Blameless

We write what the system allowed to happen, not who typed the command. If a person could
cause an outage with one mistake, that is a system problem.

## Template

- **Summary** — one paragraph, no jargon
- **Impact** — who was affected, for how long, what it cost
- **Timeline** — UTC timestamps, detection → mitigation → resolution
- **Root cause** — the actual mechanism
- **What went well** — genuinely, list something
- **Action items** — each with an owner and a due date

## Action items

Action items without an owner are wishes. Every item needs a name and a date, and they are
reviewed in the monthly ops review. Items older than 90 days get escalated or explicitly
dropped — carrying them forever is worse than admitting we will not do them.

## Published postmortems

- `postmortem-2026-03-checkout-outage.md`
- `postmortem-2026-05-db-failover.md`
- `postmortem-2026-07-cdn-misconfig.md`
