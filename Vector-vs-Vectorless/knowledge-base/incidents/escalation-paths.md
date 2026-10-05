# Escalation Paths

## Paging escalation

1. Primary on-call — 15 minutes to ack
2. Secondary on-call — 10 minutes to ack
3. Engineering lead for that team
4. Head of Engineering

PagerDuty handles steps 1–3 automatically. Step 4 is manual and should be rare.

## When to escalate early

Do not wait for the timer if:
- The incident is a SEV-1 and you are alone
- Customer data may be exposed — involve Security immediately, see
  `security/incident-security-playbook.md`
- You are out of ideas after 20 minutes

Escalating is not failure. Sitting on a SEV-1 alone for an hour is.

## Non-engineering escalation

- **Support** — for anything customer-visible, so they can respond consistently
- **Legal / Comms** — data exposure, or a regulatory reporting deadline
- **Finance** — payment settlement problems lasting over an hour

The IC decides who gets pulled in. If there is no IC, assign one first.
