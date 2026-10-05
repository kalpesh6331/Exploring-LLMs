# CI/CD Pipeline

Every service uses the same pipeline, defined centrally.

## Stages

1. **Lint + unit tests** — fails fast, runs on every push
2. **Build** — container image, tagged with the commit SHA
3. **Security scan** — image vulnerability scan; criticals block the build (see
   `security/vulnerability-management.md`)
4. **Push** — to the internal registry
5. **Deploy to staging** — automatic on merge to `main`
6. **Smoke tests** — against staging
7. **Deploy to prod** — manual trigger via `ci/deploy`

Production deploys are never automatic. Someone presses the button.

## Build times

Typical end-to-end is 8–12 minutes. If a build takes over 25 minutes something is wrong —
usually a cache miss on dependencies.

## Flaky tests

A test that fails intermittently gets quarantined, not ignored. Quarantined tests still run
but do not block; they are reviewed weekly. Using `--skip-smoke` to dodge a flaky test is not
acceptable — see `operations/deployments.md`.

## Secrets in CI
Injected at runtime from Vault. Never committed, never echoed into logs. See
`infrastructure/secrets-management.md`.
