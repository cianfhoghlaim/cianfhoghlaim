# NEW-USER-ONBOARDING.md

> **Comprehensive onboarding for new operators of the Cianfhoghlaim monorepo.**
> This document is the canonical entry point for anyone who has just cloned the repo.

## TL;DR — The 5-Minute Path

If you've cloned this repo and want the absolute minimum to be productive:

```bash
# 1. Install the toolchain (mise + bun + uv + dagger + pulumi + duckdb)
brew install mise
mise install

# 2. Install dependencies
bun install
uv sync

# 3. Hydrate secrets (requires a running Infisical instance — see §1 below)
bun run secrets:env
bun run secrets:init

# 4. Verify the local environment
mise run validate-env
mise run lint:skills
mise run lint:drift-docs
```

If all four steps exit 0, you have a working development environment.
The next sections cover the **full** cluster bringup + the 12-MCP surface
+ the 3 secrets you must populate yourself + the troubleshooting FAQ.

---

## §1 — Pre-requisites

| Tool | Why | Install |
|:--|:--|:--|
| **macOS or Linux** | The whole stack is dockerized; Windows requires WSL2 | n/a |
| **git** | Clone the repo | `brew install git` (macOS) / apt (Linux) |
| **mise** | Tool version manager (replaces asdf/nvm/pyenv) | `brew install mise` |
| **bun ≥1.4** | JS/TS runtime + workspace manager | Installed via mise |
| **uv ≥0.11** | Python package manager | Installed via mise |
| **Docker ≥24** | Stack runtime | `brew install --cask docker` |
| **~50 GB free disk** | Sources + caches + marimo notebooks | n/a |
| **Infisical vault access** | The 200+ secrets are sourced from `dev-baile` | Per §4 below |

Verify the toolchain:

```bash
mise --version    # 2026.5+ recommended
bun --version     # 1.4+
uv --version       # 0.11+
docker --version  # 24+
```

---

## §2 — The 1-Command Setup

```bash
bun run setup
# expands to:
#   mise install && bun install && uv sync && bun run secrets:env && bun run secrets:init
```

What each step does:

| Step | Purpose | Failure mode |
|:--|:--|:--|
| `mise install` | Install pinned tool versions (.mise.toml) | Wrong tool version |
| `bun install` | Install JS workspace deps (Turborepo) | Network/registry |
| `uv sync` | Install Python deps (uv workspace) | Python version mismatch |
| `bun run secrets:env` | Generate `.env` from `.infisical.env` template | Missing `INFISICAL_*` values (see §4) |
| `bun run secrets:init` | Push `infisical://` refs into the dev-baile vault | Vault unreachable |

If `bun run secrets:init` fails (most common in a fresh clone), see §4 below.

---

## §3 — The 10-Step Cluster Bringup

> **This is the full production bringup.** Steps 1-6 must run on a fresh
> cluster; steps 7-10 are orchestration steps. Steps 1-3 can run on any
> host with docker + 8 GB RAM. Steps 4-6 require cloud accounts
> (Cloudflare DNS + Hetzner/OCI compute).

### Step 1 — Local toolchain (5 min)

```bash
brew install mise
mise install
bun install && uv sync
```

### Step 2 — Stand up Infisical (port 8081, 30 min)

The Infisical stack is the source of truth for all 200+ secrets.

```bash
cd bonneagar/stacks/infisical
docker compose -f compose.yaml -f sidecar.yaml up -d
sleep 30  # wait for the first-boot migration
curl -fsS http://localhost:8081/api/status  # returns OK
```

See `bonneagar/deploy-runbooks/local-infisical-as-permanent-dev-env.md`
for the full operator guide.

### Step 3 — Stand up Pocket ID (port 8080, 20 min)

Pocket ID is the OIDC identity provider.

```bash
cd bonneagar/stacks/pocketid
docker compose -f compose.yaml -f sidecar.yaml up -d
# Open https://localhost:8080 in a browser, complete the first-user wizard
```

See `bonneagar/deploy-runbooks/pocketid-pangolin-komodo-onboarding.md`.

### Step 4 — Stand up Tinyauth (port 10000, 10 min)

Tinyauth is the auth proxy for Pangolin.

```bash
cd bonneagar/stacks/tinyauth
docker compose -f compose.yaml -f sidecar.yaml up -d
```

### Step 5 — Stand up Komodo (port 9120, 30 min)

Komodo is the container orchestrator.

```bash
cd bonneagar/stacks/komodo
docker compose -f compose.yaml -f sidecar.yaml up -d
sleep 60
curl -fsS http://localhost:9120/api/v1/system-info
```

### Step 6 — Stand up Pangolin (port 3001 + Cloudflare DNS, 60 min)

Pangolin is the reverse proxy + LetsEncrypt cert manager.

```bash
cd bonneagar/stacks/pangolin
docker compose -f compose.yaml -f sidecar.yaml up -d
# Wire Cloudflare DNS for *.cianfhoghlaim.ie first (manual step)
```

### Step 7 — Deploy Newt on workload host (20 min)

Newt is the Pangolin client for each workload host.

```bash
# On the workload host (bunchloch or arm1-oci)
mise run iac:deploy-newt
```

### Step 8 — Run the 8-phase iac:bootstrap (90 min)

This creates the `dev-baile` environment in Infisical + registers
the 4 resource-syncs + starts the 10 cross-cutting procedures.

```bash
mise run iac:bootstrap
# 1. Pulumi — provision cloud resources
# 2. Infisical — create dev-baile + 8 machine identities
# 3. Pangolin — wire OIDC + create the 3 hosts
# 4. Komodo — register the Periphery agents
# 5. Newt — deploy Pangolin client
# 6. All syncs — register the 4 resource-syncs
# 7. One-shot — run 10 cross-cutting procedures
# 8. First sync — wait for resource-syncs to pull
```

### Step 9 — Run the 10-phase deploy:full (60 min)

This brings up the 12 critical-path stacks in dependency order.

```bash
mise run deploy:full
# 1.  preflight-arm-oci       — 4-check safety gate
# 2.  iac-auth-rotate         — 3-way credential rotation
# 3.  pocketid-oidc-wire      — Pocket ID → Komodo + Pangolin
# 4.  pangolin-client-install — mint Pangolin client + render newt compose
# 5.  control-plane-up        — infisical + pangolin + komodo + pocket-id + tinyauth
# 6.  lakehouse-up            — postgres + garage + clickhouse + redis + lakekeeper + lance-namespace
# 7.  data-stacks-up          — litellm + langfuse + mlflow + logfire + cognee + graphiti + lancedb
# 8.  ocr-backends-up         — paddleocr + dots-ocr + olmocr + docling-serve + mlx-omni + llama-swap + meaisinfoghlaim
# 9.  agent-surfaces-up       — openclaw + openchamber + hermes + ocr-router
# 10. dagster-materialize-and-sensor-health-gate — BIEP v3 materialise + sensor health gate
```

### Step 10 — Verify (15 min)

```bash
# 3 CI gates
mise run lint:skills
mise run lint:drift-docs
mise run cic:stack-doctor

# The 12-MCP smoke harness
mise run lint:mcp-runtime    # 12/12 enabled MCPs have smoke tasks
bash scripts/lint_mcp_gateway.sh  # phantom gateway has KNOWN-ISSUE marker

# One per-MCP smoke (each returns OK or WARN-not-reachable)
for mcp in dlt-workspace-mcp firecrawl motherduck chrome cocoindex-code huggingface crawl4ai cognee graphiti langfuse infisical design-system; do
  echo "=== $mcp ==="
  mise run "mcp:smoke:$mcp"
done
```

---

## §4 — The 3 Secrets You Must Populate Yourself

The 200+ secrets are referenced in `.infisical.env` as `infisical://dev-baile/...`.
The Locket sidecar resolves them at runtime. **Three** require operator-side
generation before the system boots:

| Secret | Source | How to populate |
|:--|:--|:--|
| **`INFISICAL_CLIENT_ID`** | Infisical `dev-baile` vault → Machine Identities | After Step 2 (Infisical up), create a machine identity in the Infisical UI; copy the `client_id` to `.infisical.env` line 699. |
| **`INFISICAL_CLIENT_SECRET`** | Same | Same as above, copy `client_secret`. |
| **`INFISICAL_PROJECT_ID`** | Same | Same as above, copy `project_id`. |
| **`CRAWL4AI_JWT_SECRET`** | Generated locally | `openssl rand -hex 32`; paste into Infisical vault under `cianfhoghlaim/crawl4ai-jwt-secret`. |

After populating, re-run `bun run secrets:init`.

Auto-generated (no action needed):

| Secret | Source | Where it lives |
|:--|:--|:--|
| `KOMODO_JWT_SECRET` | Komodo first-boot | Komodo config (auto-rotated) |
| `GARAGE_RPC_SECRET` | Garage first-boot | Garage config |
| `LITELLM_MASTER_KEY` | LiteLLM first-boot | LiteLLM config |

---

## §5 — The 12-MCP Verification Checklist

> **Per `openspec/changes/2026-08-21-mcp-server-revival-overview.md`** —
> 12 MCP servers are now wired via `opencode.json` + `.mcp.json` (as of
> commit `f63c6a57b`). Each MUST have a smoke task. Each MAY need a
> reachable backend service before the smoke returns OK (not WARN).

| MCP | Port / Endpoint | Purpose | Smoke task | Requires |
|:--|:--|:--|:--|:--|
| `cocoindex-code` (ccc) | stdio (`ccc mcp`) | Semantic code search | `mise run mcp:smoke:cocoindex-code` | `ccc` on PATH |
| `firecrawl` | stdio (`bunx firecrawl-mcp`) | Paid anti-bot + research | `mise run mcp:smoke:firecrawl` | `bun` + `bunx` |
| `motherduck` | stdio (`uvx mcp-server-motherduck`) | SQL analytics (in-memory) | `mise run mcp:smoke:motherduck` | `uvx` |
| `chrome-devtools-mcp` | stdio (`bunx chrome-devtools-mcp`) | Local Chrome debugging | `mise run mcp:smoke:chrome` | `bun` + Chrome binary |
| `dlt-workspace-mcp` | stdio (`uv run dlthub ai mcp`) | DLT pipeline workspace | `mise run mcp:smoke:dlt-workspace-mcp` | `uv` + `dlthub` |
| `huggingface` | remote (`huggingface.co/mcp`) | Model + dataset hub | `mise run mcp:smoke:huggingface` | HTTPS to HF |
| `crawl4ai` | remote (`crawl4ai-mcp.cianfhoghlaim.ie/sse`) | Open-source bulk scraping | `mise run mcp:smoke:crawl4ai` | crawl4ai stack + Pangolin route |
| `cognee` | stdio (`uvx cognee-mcp`) | Knowledge graph memory | `mise run mcp:smoke:cognee` | Cognee stack on :8100 |
| `graphiti` | stdio (`uv run graphiti_core.mcp`) | Temporal knowledge graph | `mise run mcp:smoke:graphiti` | Neo4j on :7687 + Graphiti on :8000 |
| `design-system` | stdio (Python FastMCP) | AG-UI self-heal (R23 of 2026-07-18-british-isles-portal-activation-v3) | `mise run mcp:smoke:design-system` | design-system-server.py reachable |
| `langfuse` | stdio (`bunx @langfuse/mcp`) | LLM trace observability | `mise run mcp:smoke:langfuse` | Langfuse stack on :3000 |
| `infisical` | stdio (`bunx @infisical/mcp`) | Runtime secret mutation | `mise run mcp:smoke:infisical` | Infisical stack on :8081 + the 3 INFISICAL_* values populated |

---

## §6 — The 3 Network Dependencies

| Dependency | Why | Setup |
|:--|:--|:--|
| **Cloudflare DNS for `*.cianfhoghlaim.ie`** | LetsEncrypt via Pangolin requires real DNS for cert issuance | Add `*.cianfhoghlaim.ie` CNAME records in Cloudflare pointing at the Pangolin host |
| **Cloudflare API token** | Pangolin DNS-01 ACME challenge | `Cloudflare → My Profile → API Tokens → Create Token → Edit zone DNS` |
| **The 8 third-party API accounts** | Referenced in `.infisical.env` but not auto-provisioned | Firecrawl, HuggingFace, OpenAI, Anthropic, DeepSeek, Gemini, Z.ai, Komodo (admin) |

---

## §7 — Troubleshooting FAQ

### "Mise can't find task X"

The `mise` task catalogue is auto-generated from the openspec changes.
If a task is missing, check whether the change is in `openspec/changes/`
vs `openspec/changes/archive/`.

```bash
openspec list 2>&1 | grep <task-prefix>
```

### "MCP server not registering"

```bash
# Step 1: Is the MCP entry enabled in opencode.json?
grep -A 1 '"<name>":' opencode.json | grep enabled

# Step 2: Does it have a smoke task?
mise run lint:mcp-runtime

# Step 3: Try the smoke task directly
mise run mcp:smoke:<name>
```

### "Stack fails stack-doctor"

```bash
bash scripts/stack-doctor.sh
# CRITICAL = missing compose.yaml or docker compose config --quiet failed
# WARNING = missing one of the 6 GOLD_STANDARD files
# INFO = passes all checks

# Target: 0 CRITICAL, 0 WARNING for production stacks
```

### "Infisical returns 401"

```bash
# Step 1: Verify the 3 INFISICAL_* values are populated
grep -E "^INFISICAL_" .infisical.env

# Step 2: Re-run the secret sync
bun run secrets:init

# Step 3: Verify the vault is reachable
curl -fsS http://localhost:8081/api/status
```

### "Browser MCP returns 401"

This means the JWT secret isn't populated OR doesn't match the server's.

```bash
# Generate a new one
openssl rand -hex 32

# Push to the Infisical vault under cianfhoghlaim/crawl4ai-jwt-secret
# Set CRAWL4AI_JWT_SECRET in the container's env (matches the v0.9.0 secure-by-default contract)
```

### "Cluster bringup hangs"

```bash
# The arm1-OCI safety preflight gate is mandatory
mise run preflight-arm-oci

# Check the resumable checkpoint
cat ~/.cianfhoghlaim/deploy-state.json
```

### "Skill metadata drift"

```bash
mise run lint:skills        # 65/65 pass
mise run lint:drift-docs    # catches stale number claims in AGENTS.md
```

---

## §8 — The Path Through the Monorepo

| Domain | Entry point |
|:--|:--|
| **Agent fleet** (12 agents + 8 NCCA subjects) | [`agents/AGENTS.md`](../agents/AGENTS.md) |
| **OCR/HTR/alignment** (5-stage BIEP pipeline) | [`agents/meaisinfhoghlaim/AGENTS.md`](../agents/meaisinfhoghlaim/AGENTS.md) |
| **Data platform** (DLT + Dagster + BAML + CocoIndex + MotherDuck + marimo) | [`orchestration/README.md`](../orchestration/README.md) + [`dlt_sources/DATA_PLATFORM_ROUTER.md`](../dlt_sources/DATA_PLATFORM_ROUTER.md) |
| **IaC + 94 Docker stacks** | [`bonneagar/README.md`](../bonneagar/README.md) |
| **Web surface** (TanStack Start + CopilotKit + AG-UI + Hono + Convex) | [`web/`](../web/) + [`web/AGENTS.md`](../web/AGENTS.md) |
| **CCC + Cognee + Firecrawl dual-search** | [`.agents/skills/INDEXING_AND_COGNITION.md`](../.agents/skills/INDEXING_AND_COGNITION.md) |
| **12-MCP surface** | [`openspec/changes/2026-08-21-mcp-server-revival-overview.md`](../openspec/changes/2026-08-21-mcp-server-revival-overview.md) |

---

## §9 — The 7 Deploy Runbooks (for the per-cluster specifics)

For per-cluster deployment specifics beyond what this onboarding covers:

| Runbook | When |
|:--|:--|
| [`bonneagar/deploy-runbooks/pocketid-pangolin-komodo-onboarding.md`](../bonneagar/deploy-runbooks/pocketid-pangolin-komodo-onboarding.md) | The 3-system auth mesh |
| [`bonneagar/deploy-runbooks/local-infisical-as-permanent-dev-env.md`](../bonneagar/deploy-runbooks/local-infisical-as-permanent-dev-env.md) | Stand up Infisical as your dev environment |
| [`bonneagar/deploy-runbooks/openclaw-hermes-bunchloch-local-2026-07.md`](../bonneagar/deploy-runbooks/openclaw-hermes-bunchloch-local-2026-07.md) | Bring up the agent surfaces on bunchloch |
| [`bonneagar/deploy-runbooks/agent-fleet-arm1-oci-2026-08.md`](../bonneagar/deploy-runbooks/agent-fleet-arm1-oci-2026-08.md) | Bring up the agent fleet on arm1-oci |
| [`bonneagar/deploy-runbooks/agent-fleet-bunchloch-2026-08.md`](../bonneagar/deploy-runbooks/agent-fleet-bunchloch-2026-08.md) | Bring up the agent fleet on bunchloch |
| [`bonneagar/deploy-runbooks/repair-pangolin-private-infisical-2026-07.md`](../bonneagar/deploy-runbooks/repair-pangolin-private-infisical-2026-07.md) | Fix a broken Pangolin ↔ Infisical integration |
| [`bonneagar/deploy-runbooks/full-local-agent-platform-stack-2026-07.md`](../bonneagar/deploy-runbooks/full-local-agent-platform-stack-2026-07.md) | The canonical "everything on one host" guide |

---

## §10 — The Cheat Sheet

For the quick-reference card, see [`CHEATSHEET.md`](CHEATSHEET.md).

---

## License

BUSL-1.1 — see [`LICENSE.md`](../LICENSE.md).

Last updated: 2026-08-21.
