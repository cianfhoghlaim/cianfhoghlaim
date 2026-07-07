# Bonneagar

> **Scottish Gaelic for *infrastructure*.**
> The sovereign, zero-trust, GitOps-first foundation layer for
> the [cianfhoghlaim](https://github.com/cianfhoghlaim/cianfhoghlaim)
> monorepo and its sibling
> [leabharlann](https://github.com/cianfhoghlaim/leabharlann)
> digital library. **No managed cloud. No Kubernetes. Just
> Compose + Ansible + Pulumi + Komodo + Pangolin, deployed
> by hand and by cron.**

---

## What this is

Bonneagar is the **operational foundation** under every Python
service the cianfhoghlaim project ships. If the cianfhoghlaim
monorepo is the application layer — the brains, the agents, the
Dagster code-locations, the BAML contracts — then bonneagar is
the body: the Linux boxes, the Docker Compose stacks, the
service mesh, the TLS certificates, the Prometheus endpoints,
the health checks, the backups, the orchestration, the secrets
backplane, and the GitOps loop that ties them all together.

This repository was extracted from the former `kings_college_galway` /
`cianfhoghlaim` monorepo on **2026-06-28** as part of the *sruth → cianfhoghlaim*
consolidation and the split of `leabharlann/` and `bonneagar/` into
independent, GitOps-managed repositories (BUSL-1.1).

If your question is **"how does langfuse run?"**, the answer lives
here. If your question is **"how does langfuse extract learning
outcomes?"**, the answer lives in
[`cianfhoghlaim`](https://github.com/cianfhoghlaim/cianfhoghlaim).

---

## What lives here (the 4 pillars)

### 1. Compute provisioning — `pulumi/`

Pulumi stacks targeting four providers:

- **Oracle Cloud Infrastructure** (OCI Ampere A1) — the primary
  public-facing ARM host
- **Hetzner Cloud** — the always-on fallback + backup egress
- **Cloudflare R2** — the S3-compatible remote mirror (no egress)
- **Azure** — disaster-recovery region

Stacks are defined in TypeScript and Python; Pulumi's state lives
in Komodo's operator console, not the repo. The IaC topology is
discoverable via `iac/komodo/` (the TS control plane).

### 2. Server bootstrap — `ansible/`

Ansible playbooks + roles that bring a fresh bare-metal host from
zero to fully-running Komodo / Forgejo / Pocket ID / Pangolin
within ~10 minutes. The EE (Execution Environment) builder at
`ansible/ee/` packages the right Python + collections for offline
playbook runs.

### 3. Fleet orchestration — `komodo/`

Komodo GitOps definitions (TOML) for the entire fleet:

- `komodo/procedures/` — per-stack deploy + health-check + migration
  shell scripts. The `deploy-<stack>-bunchloch.toml` files enforce
  the dependency order (foundation → observability → memory →
  surfaces).
- `komodo/stacks/` — the 90+ Compose-stack registrations (each
  pointing at its 6-file GOLD_STANDARD in `stacks/<name>/`).
- `komodo/servers/`, `komodo/sites/`, `komodo/resource-syncs/`,
  `komodo/backups/` — the surrounding fleet definitions.
- **No Kubernetes**. Komodo's strength is "Compose + cron"; we lean
  into it.

### 4. Mesh security — `pangolin/`

The zero-trust mesh:

- **Pangolin** (reverse proxy + resource broker) + **WireGuard**
  (overlay network) + **Traefik** (L7 ingress) + **Pocket ID**
  (OIDC SSO) + **TinyAuth** (Tinyauth reverse-proxy middleware).
- 90+ private resources (one per stack) exposed at
  `<name>.cianfhoghlaim.ie`, all behind Pocket ID SSO.
- Blueprint + resource definitions at `pangolin/*.yaml`.
- Bring-up playbook at [`PANGOLIN-SETUP.md`](./PANGOLIN-SETUP.md).

---

## Stacks (per-stack details)

The 90+ Docker Compose stacks live in [`stacks/`](./stacks). Each
follows the **6-file GOLD_STANDARD pattern**:

```
stacks/<name>/
├── compose.yaml         # services + volumes + networks
├── sidecar.yaml         # Locket sidecar overlay for production secrets
├── secrets.env          # infisical:// URI templates (no plaintext!)
├── pangolin.yaml        # private-resource route for <name>.cianfhoghlaim.ie
├── blueprint.yaml       # Pangolin blueprint registration
└── .env.example         # env-var catalogue (canonical dev defaults)
```

A **per-stack doc** lives at
`../cianfhoghlaim/docs/stacks/<name>.md` (the 4-section Purpose +
Why-GitOps + Cross-references + Tags template). These are the
discoverability surface; do not duplicate their content in this
README.

To find a stack and what it does:

```bash
ls stacks/                                    # full inventory
cat stacks/<name>/compose.yaml | head        # service shape
cat stacks/<name>/secrets.env | grep '^#'    # secret source map
cat stacks/<name>/pangolin.yaml             # public URL + ACL
```

The **stack-doctor** audit (`bash scripts/stack-doctor.sh`) runs
on every CI push; it reports any missing doc, missing
healthcheck, or un-pinned image tag.

---

## The 5-group model

Stacks are clustered (informational only — not a deploy-time
constraint) into 5 groups:

| Group | Stack examples | Host |
|:--|:--|:--|
| **infrastructure** | Pangolin, Pocket ID, TinyAuth, Traefik, Infisical, Locket, Komodo Core + Periphery, Backrest | `arm1-oci` |
| **data-engineering** | Dagster, Lakehouse, Marimo, CocoIndex, Cognify, Litellm, Langfuse, Llama-swap | `bunchloch` |
| **agent-platform** | Agno AgentOS, Google ADK, OpenClaw, OpenChamber, Cognee, Graphiti, Letta | `bunchloch` |
| **language-model** | LiteLLM, llama-swap, MLX-Omni, Logfire, Langfuse, mlflow | `bunchloch` |
| **user-facing-web** | oideachais-web, oideachais-api, oideachais-dagster, oideachais-agent-os, oideachais-adk-agents, openclaw | `bunchloch` |
| **ci** | hf-watchdog | `bunchloch` |

The remaining 80+ stacks are personal/utility (audiobookshelf,
firecrawl, vscode-server, …). See [`AGENTS.md`](./AGENTS.md) for
the full inventory.

---

## Physical hosts

| Host | Provider | Role |
|:--|:--|:--|
| `arm1-oci` | Oracle Cloud (Ampere A1) | Public-facing mesh + the centralised data plane (Postgres + Garage + ClickHouse + Redis). Always-on. |
| `bunchloch` | MacBook M4 (48 GB RAM, 2 TB SSD) | Local dev + LiteLLM gateway + llama-swap + the bulk of the agent-runtime stacks. Restarted when the lid closes. |
| (future `arm2-hetzner`) | Hetzner Cloud CAX21 | Disaster-recovery mirror of `arm1-oci`. Currently unprovisioned. |

---

## Quick start

Read the 4 entry-point docs in order — they're each ~200 lines
and link into the rest of the documentation tree:

1. **[`AGENTS.md`](./AGENTS.md)** — the AI-agent-friendly quick
   reference (4 priority stacks + 4 priority skills + 4 priority
   commands). Read this first.
2. **[`DEPLOYMENT-STRATEGY.md`](./DEPLOYMENT-STRATEGY.md)** — the
   bring-up playbook (host provisioning → mesh → Komodo → first
   stack → cluster health).
3. **[`GOLD_STANDARD.md`](./GOLD_STANDARD.md)** — the 6-file
   per-stack convention. Read before adding a new stack.
4. **[`PANGOLIN-SETUP.md`](./PANGOLIN-SETUP.md)** — the zero-trust
   mesh configuration.
5. **[`SECRETS-MANAGEMENT.md`](./SECRETS-MANAGEMENT.md)** — the
   Infisical + Locket + mise 3-way contract (no manual `.env`).

For day-to-day operations:

```bash
# Run the stack-doctor (lint + health + freshness)
bun run validate-stacks

# Materialise an Infisical entry from the local .env
bun run secrets:init

# Run a one-shot compose stack (with dev secrets)
bun run stack.sh <name> up -d

# Force a Komodo procedure (e.g., redeploy + health check)
km run procedure deploy-lakehouse-bunchloch

# Open the operator consoles
# Komodo:   https://komodo.cianfhoghlaim.ie
# Litellm:  https://litellm.cianfhoghlaim.ie
# Langfuse: https://langfuse.cianfhoghlaim.ie
# Dagster:  https://dagster.cianfhoghlaim.ie
```

---

## Secrets — the 3-way Infisical contract

Bonneagar implements a single invariant: **no plaintext
credentials anywhere in this repo**. Every `secrets.env` is a
template of `infisical://` URI references; every container is
started with a Locket sidecar that resolves those URIs at runtime
against the `dev-baile` Infisical vault. The CI never sees
secrets; the dev workflow never sees secrets; the ops console
never sees secrets.

The 3 stages:

1. **Source** — `secrets.env` files declare `infisical://dev-baile/<svc>/<key>`
   references
2. **Transport** — Locket (the sidecar at `compose -f sidecar.yaml`)
   resolves the URIs to env vars, writes them to a tmpfs volume
3. **Hand-off** — Komodo procedure `secrets:init` syncs the local
   `.env` (when present) up to the vault, not the other way around

See [`SECRETS-MANAGEMENT.md`](./SECRETS-MANAGEMENT.md) for the
full contract.

---

## Recent major changes

A condensed history. The full openspec change set lives at
`openspec/changes/` (from the sibling monorepo).

| Date | Change | What |
|:--|:--|:--|
| **2026-07-30** | **centralise-data-plane** (7-stack ops rewrite) | The most consequential stack refactor: langfuse, litellm, mlflow migrated off per-stack Postgres / Minio / Redis / ClickHouse onto the shared `lakehouse` data plane. `lakehouse` is now 11 services (added `clickhouse` + `redis`), 12 databases, 7 buckets (added langfuse-events/-media/-exports + mlflow-artifacts). One service tier collapsed into one. |
| **2026-07-30** | **graphiti Neo4j removal** | Graphiti's broken Neo4j profile removed. Only the FalkorDB profile remains, and `falkordb` is now a Stage 1 prerequisite for the cluster procedure. |
| **2026-06-29** | **v4 canonical stack migration** | The 90+ Compose stacks all migrated to `bonneagar/stacks/`. The `infrastructure/` + `cianfhoghlaim/stacks/` legacy paths removed. `stack-doctor.sh` is now the canonical audit. |
| **2026-06-29** | **`iac-merge-komodo-pangolin-infisical`** | The 3 separate IaC clients merged into a single TS client in `iac/komodo/`. |
| **2026-06-26** | **archive-celtic-baml-orphans** | Final cleanup of orphan BAML clients after the v4 `baml-reorganize-by-cluster` change. |
| **Earlier** | **cleanup-and-boot-stacks** + **centralize-agent-context** | The original re-afford + Dagger pipeline readiness work. Both complete. |

---

## Related repos

| Repo | Domain |
|:--|:--|
| [**cianfhoghlaim/cianfhoghlaim**](https://github.com/cianfhoghlaim/cianfhoghlaim) | The application monorepo — Python package, Dagster code-locations, agent fleet, web apps, BAML contracts, per-subject pipelines. The "what runs the platform" |
| [**cianfhoghlaim/leabharlann**](https://github.com/cianfhoghlaim/leabharlann) | The digital library — 6-domain personal corpus of curated PDFs. The "what the platform reads" |
| Sub-embedded repos | `bonneagar/stacks/<name>/` may contain `git submodule` references for state-only submodules; see the `iac/README.md` for the list |

---

## License

BUSL-1.1 — see [`LICENSE`](../LICENSE).

Source-available; not an Open Source licence. Re-use permitted for
non-commercial purposes; commercial re-use requires written
agreement. The codebase contains operational credential material
(secrets paths + Komodo inventory) that must not be re-deployed
in derived work without explicit written consent.
