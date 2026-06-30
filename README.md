# Bonneagar — Infrastructure GitOps

> **Bonneagar** — Scottish Gaelic for *infrastructure*. The sovereign,
> zero-trust, GitOps-first foundation layer that the
> [cianfhoghlaim](https://github.com/cianfhoghlaim/cianfhoghlaim) monorepo
> and its sibling [leabharlann](https://github.com/cianfhoghlaim/leabharlann)
> digital library run on.

This repository was extracted from the former `kings_college_galway` /
`cianfhoghlaim` monorepo on **2026-06-28** as part of the *sruth → cianfhoghlaim*
consolidation and the split of `leabharlann/` and `bonneagar/` into
independent, GitOps-managed repositories (BUSL-1.1).

It contains:

- **Compute provisioning** — Pulumi stacks targeting Oracle Cloud (OCI Ampere A1),
  Hetzner Cloud, Cloudflare R2, and Azure.
- **Server bootstrap** — Ansible playbooks + roles for Pangolin, Komodo,
  Forgejo, Pocket ID, and the rest of the zero-trust mesh.
- **Fleet orchestration** — Komodo GitOps definitions (procedures, servers,
  sites, stacks, backups, resource-syncs) — no Kubernetes.
- **Mesh security** — Pangolin + WireGuard + Traefik + Pocket ID SSO +
  TinyAuth.
- **Secrets** — Infisical `dev-baile` vault + Locket sidecar pattern;
  every `secrets.env` in `stacks/` is a template that resolves at container
  runtime (no plaintext credentials in this repo).
- **Image pipelines** — Dagger module with 4 pipelines + 8 callable functions.
- **Compose stacks** — 90 pre-configured stacks under `stacks/` (the canonical
  6-file `GOLD_STANDARD` pattern: `compose.yaml`, `compose.dev.yaml`,
  `sidecar.yaml`, `pangolin.yaml`, `secrets.env`, `blueprint.yaml`).

## Physical hosts

| Host | Provider | Role |
|---|---|---|
| `arm1-oci` | Oracle Cloud (Ampere A1) | Public-facing mesh + data plane |
| `bunchloch` | MacBook M4 (48 GB) | Local dev + LiteLLM gateway + llama-swap |

## Quick start

Read [`AGENTS.md`](./AGENTS.md) for the agent-friendly priority quick
reference (4 compose stacks, 4 skills, 3 commands).

The detailed bring-up playbook is [`DEPLOYMENT-STRATEGY.md`](./DEPLOYMENT-STRATEGY.md).
Per-stack conventions live in [`GOLD_STANDARD.md`](./GOLD_STANDARD.md).
The Pangolin mesh setup is [`PANGOLIN-SETUP.md`](./PANGOLIN-SETUP.md).
Secrets management is documented in [`SECRETS-MANAGEMENT.md`](./SECRETS-MANAGEMENT.md).

## Layout

```
.
├── README.md             # this file
├── AGENTS.md             # AI agent quick reference
├── DEPLOYMENT-STRATEGY.md
├── GOLD_STANDARD.md      # 6-file stack template
├── PANGOLIN-SETUP.md
├── SECRETS-MANAGEMENT.md
├── QUADRANT-TO-STACK-MAP.md
├── ansible/              # playbooks, roles, inventory, EE builder
├── audit/                # stack-doctor, cost-reporter
├── ci/                   # GitHub Actions / Forgejo workflows
├── dagger/               # cianchoghlaim_dagger module (4 pipelines, 8 fns)
├── deploy-runbooks/      # per-host deploy procedures
├── docs/                 # long-form ops + design docs
├── firecrawl/            # scrape jobs for site verification
├── iac/                  # IaC shared modules (komodo, etc.)
├── komodo/               # GitOps fleet definitions (TOML)
├── observability/        # langfuse, mlflow, logfire wiring
├── pangolin/             # blueprint + resource definitions
├── pulumi/               # OCI / Cloudflare / Azure stacks
├── scripts/              # dev.sh, deploy-cf.sh, sync-blueprints.sh, stack.sh
├── secrets/              # .env.enc + encryption tooling
├── stacks/               # 90 compose stacks
└── templates/            # stack scaffolding templates
```

## License

BUSL-1.1 — see [`LICENSE`](./LICENSE).

## Related repositories

| Repo | Domain |
|---|---|
| [cianfhoghlaim/cianfhoghlaim](https://github.com/cianfhoghlaim/cianfhoghlaim) | Application monorepo (Python package, agents, web apps, Dagster pipelines) |
| [cianfhoghlaim/leabharlann](https://github.com/cianfhoghlaim/leabharlann) | Digital library (Gaeilge, mata, aigne, ollscoil, Zotero, Gemini research) |