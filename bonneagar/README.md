# `bonneagar/` — Infrastructure as Code (IaC)

> **The Docker Compose stack catalogue + the merged TypeScript IaC + Komodo GitOps + Pangolin reverse-proxy + Infisical secrets for the Cianfhoghlaim self-hosted platform.**
>
> Re-merged into the cianfhoghlaim monorepo on **2026-07-17** per the `2026-07-17-v7-flatten-cianfhoghlaim-merge-bonneagar-rewrite-readme-license-v1` openspec change. Previously a separate GitHub repo at `github.com/cianfhoghlaim/bonneagar` (now an archived read-only remote at `archive-bonneagar`).

## Architecture

```
Pulumi (Cloudflare/Hetzner/OCI)  →  provisions the 2 hosts (arm1-oci, bunchloch)
        │
        ▼
Infisical (dev-baile vault)  ──►  the secrets source of truth
        │  (Locket sidecar hydrates .env on each host)
        ▼
Komodo Core  ◄──── GitOps pull every 60s ────  komodo/ (TOML resource definitions)
        │  deploys via Komodo Periphery on each host
        ▼
93 Docker Compose stacks  ──►  fronted by Pangolin (reverse proxy + WireGuard)
                                gated by Tinyauth (ForwardAuth) + Pocket ID (OIDC)
```

`bonneagar/iac/` is the TypeScript control plane that wires all of the
above together (`bun run iac:*`); it does not run continuously — it's
invoked for bootstrap, plan, and health-check operations. The
continuous GitOps loop is Komodo pulling from `komodo/` directly.

## Implementation decisions

- **Komodo over Portainer/Coolify** — GitOps-first (pulls TOML from
  Forgejo every 60s) rather than a UI-driven container manager, so the
  desired state lives in this repo, not in a database only Komodo can
  read.
- **Pangolin + Newt over `cloudflared`** — self-hosted reverse proxy
  with its own WireGuard tunnel client (Newt), avoiding a hard
  dependency on Cloudflare's tunnel product for the private-resource
  surface; Cloudflare is still used for DNS + WAF (see `iac/pulumi/oci/`
  and `iac/pulumi/hetzner/`, which wire Cloudflare DNS records
  alongside host provisioning).
- **A 6-file "GOLD_STANDARD" per stack** (`compose.yaml` + `sidecar.yaml`
  + `secrets.env` + `.env.example` + `blueprint.yaml` + `pangolin.yaml`)
  — every stack looks the same regardless of what it runs, so
  `stack-doctor` can validate all 93 with one script instead of
  per-stack special cases.

## Quick start — for a new operator

> **If you're new to this subdirectory, start here.** This section gets you from zero to "all 93 stacks validated + IaC plan green" in 6 steps. The entire flow is automated via 6 mise tasks + 1 onboarding wizard + 1 GitOps resource-sync.

The 6 steps:

| # | Step | Mise task |
|---|---|---|
| 1 | Verify mise is installed + secrets hydrated | `mise run validate-env` |
| 2 | Verify the IaC clients can reach Komodo + Pangolin + Infisical + Newt + Pocket ID + Tinyauth | `mise run iac:health` (the 6-way health check) |
| 3 | Plan (read-only diff between IaC-declared and actual state) | `mise run iac:plan` |
| 4 | Validate all 93 stacks against the 6-file GOLD_STANDARD | `mise run cic:stack-doctor` (the stack-doctor audit) |
| 5 | Bootstrap a new cluster (Pulumi → Infisical → Pangolin → Komodo → Newt → all syncs) | `mise run iac:bootstrap` |
| 6 | Arm1-OCI safety preflight (mandatory before any `arm1-oci` mutation) | `mise run preflight-arm-oci` |

---

## 1. Verify mise + secrets

```bash
mise run validate-env
```

This validates that:
- All required env vars are hydrated (via mise + Infisical + Locket sidecar)
- The required CLI tools are installed (bun + uv + dagger + pulumi + duckdb + sops + opencode)
- The 3-way contract is intact (`.infisical.env` template + `.env` hydrated + Infisical source-of-truth)

---

## 2. 6-way health check

```bash
mise run iac:health
```

Checks all 6 systems and reports OK / WARN / FAIL per system:

| System | Port | What it checks |
|:--|--:|:--|
| **Komodo** | 9120 | `KomodoCore /api/v1/system-info` returns 200 + version |
| **Pangolin** | 3001 | `PangolinCore /api/v1/...` returns 200 + EE licence verified |
| **Infisical** | 8080 | `InfisicalCore /api/status` returns 200 + 8 machine identities exist |
| **Newt** | n/a | `docker ps --filter name=bunchloch-newt` returns running |
| **Pocket ID** | 8080 | `pocketIdHealth()` returns OK + `client_credentials` grant supported |
| **Tinyauth** | 10000 | `fetch(TINYAUTH_URL/api/healthz)` returns 200 |

---

## 3. Plan (read-only diff)

```bash
mise run iac:plan
```

Walks the 4 discoverers (stacks + resources + secrets + key-stacks) and produces a per-system report. In `--dry-run` mode, the API calls are skipped — only the filesystem discoverers run. **Use this as a CI gate** to catch drift before committing.

---

## 4. Validate 93 stacks

```bash
mise run cic:stack-doctor
# alias: bun run validate-stacks
```

The stack-doctor audit walks `bonneagar/stacks/*/compose.yaml` and reports:
- **CRITICAL**: stacks missing `compose.yaml` or failing `docker compose config --quiet`
- **WARNING**: stacks missing one of the 6 GOLD_STANDARD files (sidecar / secrets / pangolin / blueprint / .env.example)
- **INFO**: stacks that pass all checks

The audit is the CI gate (enforced by `bun run validate-stacks` in `.github/workflows/ci.yaml`). Target: **0 CRITICALS**.

---

## 5. Bootstrap a new cluster

```bash
mise run iac:bootstrap
```

The 8-phase bootstrap state machine:

1. **Pulumi** — provision cloud resources (Cloudflare + Hetzner + OCI)
2. **Infisical** — create the `dev-baile` environment + folders + 8 machine identities
3. **Pangolin** — wire the OIDC client + create the 3 hosts (`arm1-oci` + `bunchloch` + `cross-cutting`)
4. **Komodo** — register the Periphery agents
5. **Newt** — deploy the Pangolin client on each workload host
6. **All syncs** — register the 4 Komodo resource-syncs
7. **One-shot bootstrap** — run the 10 cross-cutting prerequisite procedures
8. **First sync** — wait for the resource-syncs to pull + verify each host's stack catalogue

The 3 of 10 phases that are still logWarn placeholders (Komodo Core + Periphery + Tinyauth deploy) are documented as **manual follow-ups** in the bootstrap output.

---

## 6. arm1-OCI safety preflight

```bash
mise run preflight-arm-oci
# alias: bun run preflight:arm-oci  (the docs sometimes use this colon form)
```

**MANDATORY before any `arm1-oci` mutation** (`iac:deploy`, `iac:bootstrap`, `km deploy stack <arm-oci-*>`). The script:

1. Verifies the current PID namespace is NOT shared with `openchamber`, `openclaw`, `hermes`, `komodo`, `pangolin`, or `infisical`
2. Verifies the current user is in the `komodo-admins` Pocket ID group
3. Verifies the current shell is NOT inside an opencode session
4. Emits a `--strict` mode that exits non-zero on any violation
5. Emits a `--dry-run` mode (default) that prints the verdict without blocking

---

## The 93-stack catalogue

The canonical inventory lives at [`stacks/INDEX.md`](stacks/INDEX.md) (auto-generated by `bash scripts/stack-doctor.sh`). Most stacks follow the 6-file GOLD_STANDARD pattern; a handful (`browser`, `chartdb`, `komga`, `ludusavi`, `moonlight`, `storybook`, `wave2`) are missing `blueprint.yaml`/`sidecar.yaml` and are flagged in `INDEX.md`'s WARNING section.

For the full stack list, see [`AGENTS.md`](AGENTS.md#the-93-stack-inventory).

---

## The IaC TypeScript sub-package

The merged TypeScript IaC lives at [`iac/`](iac/). It orchestrates Komodo + Pangolin + Infisical + Newt + Pocket ID + Tinyauth from a single `bun run iac:*` surface.

For the CLI commands + the 3 typed clients + the 4 source-discoverers, see [`iac/README.md`](iac/README.md).

---

## The Komodo GitOps fleet

The 4 resource-syncs + 111 stacks + 63 procedures + 4 builds + 1 server live at [`komodo/`](komodo/). `komodo/README.md` itself is stale (claims 17 stack files / 56 procedures and the pre-v7 `infrastructure/komodo/` path) — not yet fixed, see Known gaps. The IaC does not own these — they're pulled from Forgejo by Komodo Core every 60s.

For the canonical GitOps pattern, see [`komodo/README.md`](komodo/README.md).

---

## The Pangolin config

The 3 YAML files (`agent-fleet.yaml` + `blueprint.yaml` + `private-resources.blueprint.yaml`) + 4 sub-dirs live at [`pangolin/`](pangolin/). The IaC owns the `blueprint.yaml` import surface (via the Pangolin Enterprise Edition Integrations API).

---

## The deploy runbooks

7 markdown runbooks at [`deploy-runbooks/`](deploy-runbooks/) cover the user-named deploy targets:

- `full-local-agent-platform-stack-2026-07.md` — cold-boot of the entire agent-platform stack
- `local-infisical-as-permanent-dev-env.md` — use a local Infisical as the perpetual dev environment
- `openclaw-hermes-bunchloch-local-2026-07.md` — OpenClaw + Hermes on `bunchloch` (local)
- `pocketid-pangolin-komodo-onboarding.md` — the most-documented runbook (176 lines)
- `repair-pangolin-private-infisical-2026-07.md` — surgical fix for the Pangolin private-Infisical mismatch
- `agent-fleet-arm1-oci-2026-08.md` — step-by-step for the 12-agent fleet on `arm1-oci`
- `agent-fleet-bunchloch-2026-08.md` — same for `bunchloch`

---

## Known gaps

- **`komodo/README.md` and `iac/README.md` are stale** — they claim
  17 stack files / 56 procedures (real: 111 / 63) and 24 CLI commands
  (real: 26) respectively; `komodo/README.md` still uses the pre-v7
  `infrastructure/komodo/` path. Not fixed as part of this pass — this
  file (the hub) now has the correct numbers; the nested sub-docs
  don't yet.
- **`dagger/README.md` claims "8 callable functions"**; the Python
  Dagger module has 27 `@function`-decorated methods. Unclear whether
  "8" meant something narrower (top-level composed pipelines vs.
  internal helpers) — not verified.
- **3 of 10 bootstrap phases are still `logWarn` placeholders**
  (Komodo Core deploy, Periphery deploy, Tinyauth deploy) — see step 5
  above.

## Cross-references

- [`AGENTS.md`](AGENTS.md) — the canonical quadrant overview (the agent-facing entry point)
- [`iac/README.md`](iac/README.md) — the IaC sub-package doc (26 commands + 3 clients + 4 discoverers; iac/README.md itself still says 24, see Known gaps)
- [`stacks/README.md`](stacks/README.md) — the stacks sub-package doc (6-file GOLD_STANDARD + critical path)
- [`stacks/GOLD_STANDARD.md`](stacks/GOLD_STANDARD.md) — the 6-file template
- [`stacks/INDEX.md`](stacks/INDEX.md) — the live stack inventory (auto-generated by stack-doctor)
- [`komodo/README.md`](komodo/README.md) — the Komodo sub-package doc
- [`pangolin/blueprint.yaml`](pangolin/blueprint.yaml) — the public Pangolin resources (pangolin + tinyauth + middleware-manager)
- [`pangolin/agent-fleet.yaml`](pangolin/agent-fleet.yaml) — the 12-agent private resources
- [`locket-shim/`](locket-shim/) — the Infisical v0.161+ sidecar shim
- [`dagger/README.md`](dagger/README.md) — the Dagger CI/CD module (8 callable functions)
- [`../.agents/skills/stacks-sync/SKILL.md`](../.agents/skills/stacks-sync/SKILL.md) — the agent skill for validating/syncing stacks against the GOLD_STANDARD pattern