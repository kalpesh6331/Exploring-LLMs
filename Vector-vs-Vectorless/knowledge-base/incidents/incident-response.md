# Incident Response

## The process

1. **Declare.** Post in `#incidents` with the severity and a one-line description. Declaring
   early is free; declaring late is expensive.
2. **Assign an Incident Commander** for SEV-1 and SEV-2. The IC coordinates — they do not
   debug. If you are the only person there, you are the IC.
3. **Open a channel** — `#inc-YYYY-MM-DD-short-name`.
4. **Freeze deploys** for SEV-1 (automatic). See `operations/deploy-freeze.md`.
5. **Update every 15 minutes**, even if the update is "no change". Silence makes people
   invent their own updates.
6. **Mitigate before you diagnose.** Roll back, fail over, scale up. Understanding can wait.
7. **Stand down** explicitly, then write the postmortem within 48 hours.

## Roles

- **IC** — coordinates, decides, communicates. One person.
- **Ops lead** — hands on keyboard.
- **Comms** — updates the status page and Support. For SEV-1 this must not be the IC.

## Useful first moves

- What changed? Check recent deploys first — most incidents are a deploy.
- Is it one service or everything? Everything usually means ingress, DNS, or database.
- Roll back before debugging.

## Who to page
See `incidents/on-call-rotation.md`.
