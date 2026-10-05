# Security Incident Playbook

For suspected compromise, data exposure, or leaked credentials. This is **in addition to**
the normal incident process in `incidents/incident-response.md`.

## First 15 minutes

1. **Declare a SEV-1.** Any suspected customer data exposure is a SEV-1 regardless of scale.
2. **Page Security** — do not wait for the normal escalation timer.
3. **Preserve evidence.** Do not delete pods, rotate away logs, or "clean up". Snapshot first.
4. **Contain** — revoke the credential, block the IP, disable the account.
5. **Do not communicate externally.** Legal and Comms own external messaging.

## Leaked credential

Rotate first, investigate second. Follow `security/key-rotation.md` — remembering that
rotating the auth signing key logs out every customer.

Then: check audit logs for use of the leaked credential
(`security/audit-logging.md`), and determine the blast radius before declaring it contained.

## Data exposure

Involve Legal immediately. Regulatory reporting deadlines are measured in hours, not days,
and the clock starts at discovery.

## What not to do

- Do not investigate alone
- Do not email about it — use the dedicated incident channel
- Do not assume it is a false positive because the system "looks fine"
