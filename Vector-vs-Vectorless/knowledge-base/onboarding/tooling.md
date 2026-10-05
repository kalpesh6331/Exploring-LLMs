# Tooling

| Tool | Used for |
|------|----------|
| `ci` | the internal CLI — deploys, tests, migrations, dev environments |
| `kubectl` | cluster operations |
| Terraform | all infrastructure |
| Vault | secrets |
| Grafana | dashboards, metrics, logs, traces |
| PagerDuty | on-call and paging |
| GitHub | code and reviews |

## The `ci` CLI

Most of your day. Worth learning properly.

```
ci deploy --service <svc> --tag <tag>
ci migrate --service <svc> --env <env>
ci dev --service <svc>
ci test --service <svc>
ci audit query ...
ci cdn invalidate --path ...
```

`ci <command> --help` works everywhere, and `--dry-run` exists on anything destructive. Use
it.

## Conventions

- Everything is reviewed, including infrastructure
- Anything destructive requires a second approver
- Prefer the CLI over clicking in a console — console changes are invisible to everyone else
