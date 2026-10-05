# Deploy Freeze

A freeze blocks all production deploys. The pipeline refuses to run, it is not an honour
system.

## When a freeze is in effect

- **During any active SEV-1.** Automatic — declaring a SEV-1 freezes deploys.
- **Black Friday week** and the two weeks before Christmas.
- **Ad-hoc**, when announced by an engineering lead in `#engineering`.

## Who can lift it

**Only the Incident Commander can lift a freeze during a SEV-1.** Not the service owner, not
the on-call engineer, not whoever wrote the fix. If there is no IC assigned yet, assign one
first — see `incidents/incident-response.md`.

For a calendar freeze (Black Friday, Christmas), only an engineering lead can grant an
exception.

## Shipping a fix during a freeze

This happens — the fix for the incident often needs to deploy. The sequence is:

1. IC explicitly approves the deploy in the incident channel.
2. IC lifts the freeze: `ci/deploy --unfreeze --reason "SEV-1 fix"`.
3. Deploy **only** the fix, canary if at all possible.
4. Re-freeze immediately: `ci/deploy --freeze`.

Never deploy anything unrelated while the freeze is lifted. That is how a second incident
starts inside the first one.

## Checking freeze status

```
ci/deploy --status
```
