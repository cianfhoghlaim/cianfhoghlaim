# Phase 0.3 Deploy Runbook — Tier 1 + Tier 2 Stacks on bunchloch

**Date:** 2026-06-28
**Scope:** Bring up the data plane (lakehouse + LiteLLM + Cognee) and the
agent memory plane (Graphiti + FalkorDB + Dragonfly + RisingWave) on the
MacBook M4 Max (bunchloch) so the BrowserBase 43-prompt research program
can execute against real infrastructure.

**Pre-flight:**
- ✅ Phase 0.4 done — `litellm` default_model = `minimax` (alias with 7-tier fallback)
- ✅ Phase 0.4 done — `cognee` LLM_MODEL default = `minimax`
- ✅ `agent-registry` spec registered; `research` subagent dispatchable
- ✅ BrowserBase MCP working (`type: local`, bunx + --modelName deepseek/deepseek-chat)
- ⏳ This runbook — you execute

---

## Step 1 — SSH to bunchloch

```bash
ssh cianmacandeisigh@bunchloch.local
# or whatever the alias is in your ~/.ssh/config
```

## Step 2 — Sync the latest infra branch

```bash
cd /Users/cianmacandeisigh/dev/kings_college_galway    # or wherever the monorepo lives on bunchloch
git fetch origin
git checkout infra/pangolin-newt-infisical-upgrade-2026-06-28
git pull --ff-only
```

Verify:
- `git log --oneline -1` → `chore(litellm+cognee): switch default model to minimax alias`
- `git log --oneline -2` → `feat(agents): rewrite subagent foundation for cianfhoghlaim v4 consolidation`

## Step 3 — Hydrate Infisical secrets

```bash
# Make sure mise is loaded
eval "$(mise activate bash)"

# Re-hydrate the .env from .infisical.env (Infisical → Locket → .env)
bun run secrets:init
```

This populates `.env` with all the `infisical://dev-baile/<svc>/<key>` references
for the 7 stacks (lakehouse, litellm, cognee, graphiti, falkordb, dragonfly, risingwave).

Verify:
- `head .env | grep LITELLM_MASTER_KEY` → should be set (not the literal `infisical://...`)
- `grep POSTGRES_PASSWORD .env` → should be set for lakehouse + cognee
- `grep NEO4J_PASSWORD .env` → should be set for graphiti

## Step 4 — Deploy Tier 1 stacks (Lakehouse + LiteLLM + Cognee)

```bash
# Use Komodo if available (preferred)
komodo deploy lakehouse-bunchloch
komodo deploy litellm-bunchloch
komodo deploy cognee-bunchloch

# OR manually via stack.sh + Locket
./scripts/stack.sh lakehouse up -d
./scripts/stack.sh litellm up -d
./scripts/stack.sh cognee up -d
```

Verify:
```bash
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | grep -E "lakehouse|litellm|cognee"
# Expect 13 lakehouse services + 2 litellm (proxy + postgres) + 2 cognee (cognee + cognee-postgres)
```

Test LiteLLM:
```bash
curl -s -H "Authorization: Bearer $LITELLM_MASTER_KEY" http://localhost:4000/v1/models | jq '.data[] | .id'
# Expect: opencode-go/minimax-m3-slot0, slot1, slot2, qwen3.7-max, kimi-k2.6, minimax (alias), etc.
```

Test Cognee:
```bash
curl -s http://localhost:8100/health
# Expect: {"status":"ok"} or similar
```

## Step 5 — Deploy Tier 2 stacks (Graphiti + FalkorDB + Dragonfly + RisingWave)

```bash
komodo deploy graphiti-bunchloch     # Neo4j graph for temporal knowledge graph
komodo deploy falkordb-bunchloch     # Vector + graph hybrid for GraphRAG
komodo deploy dragonfly-bunchloch    # In-memory store for agent state
komodo deploy risingwave-bunchloch   # Streaming for change-data-capture
```

Verify:
```bash
docker ps --format "table {{.Names}}\t{{.Status}}" | grep -E "graphiti|falkordb|dragonfly|risingwave"
# Expect 4 stacks running
```

## Step 6 — Restart opencode with new MCP servers

The agent-registry spec includes 9 MCPs:
- browserbase, firecrawl, infisical, motherduck, chrome, cocoindex-code, cognee, graphiti, langfuse

After deployment, all 9 should connect cleanly. Restart opencode:

```bash
# If running interactively: kill the opencode process and relaunch
# If running as a daemon: ./scripts/restart-opencode.sh (or similar)
```

Verify:
- opencode MCP list shows all 9 MCPs (browserbase working as `type: local`)
- Cognee MCP connects to `localhost:8100` (the cognee stack)
- Graphiti MCP connects to `bolt://localhost:7687` (the graphiti stack)

## Step 7 — Run Phase 0.8 dry-runs (2 prompts)

Per the BrowserBase 43-prompt budget plan:
- 3,960 credits across the 43 prompts
- 2,040 credits reserve for drift re-looks + 2 dry-runs

The 2 dry-runs are:
1. **P1A-01 dlt + dlthub-pro** — 180 credits (calibrate: 1-2 hours of work × 4 sub-skills × code search)
2. **P3-S02 examinations.ie** — 75 credits (calibrate: SPA cascade with Gemini Flash Lite via browserbase)

Run these via the `research` subagent:
```bash
# Dispatch from opencode (after restart):
# - subagent_type: research
# - prompt: "Run the Phase 0.8 dry-run for P1A-01 per openspec/changes/2026-06-28-browserbase-phase-1a-decisions/specs/cianfhoghlaim-pipeline/spec.md"
# - then: "Run the Phase 0.8 dry-run for P3-S02 per openspec/changes/2026-06-28-browserbase-phase-3-decisions/specs/cianfhoghlaim-pipeline/spec.md"
```

Each dry-run outputs to:
- `openspec/research/2026-06-28-browserbase-credit-program/phase-1a/P1A-01-dlt-dlthub-pro.md`
- `openspec/research/2026-06-28-browserbase-credit-program/phase-3/P3-S02-examinations-ie.md`

Use the dry-runs to calibrate per-item credit caps before bulk launch.

## Step 8 — Bulk launch: 3-batch 43-prompt execution

After dry-runs confirm budget + quality, launch the 43 prompts in 3 multi-agent batches.

**Batch A (25 parallel):**
- data-platform × 5 (Phase 1A prompts)
- research × 5 (Phase 1B prompts)
- infrastructure × 6 (pangolin, komodo, infisical, litellm, planetscale, postgresql)
- agent-platform × 9 (olake, mlflow, langfuse, openchamber, openclaw, llama-swap, huggingface, mlx-omni, invokeai)

**Batch B (16 parallel):**
- data-platform × 4 (marimo, nimtable, dagster recheck, motherduck recheck)
- research × 12 (Phase 3 site-by-site)

**Batch C (2 parallel):**
- agent-platform × 2 (unsloth, modal)

Output: 43 `.md` files in `openspec/research/2026-06-28-browserbase-credit-program/phase-{1a,1b,2,3}/`

## Step 9 — Phase 4 OpenSpec closure

After all 43 prompts return:
- Fill the 4 stub changes (Phase 1A/1B/2/3) with ADDED Requirements derived from the research output
- `openspec validate <change-id> --strict` × 4 — every change must pass before commit
- Archive the 4 changes + the agent-registry change

## Risk register (for the deploy)

- **Tier 1 deploy hits Infisical secret gap** → re-run `bun run secrets:init` (Phase 0.6 added 18 secret URIs; should be sufficient)
- **Lakehouse on bunchloch RAM contention** → 13 services designed for ≤16GB combined; Phase 0.7 stress-test before bulk launch
- **Cognee API rejects DeepSeek API key** → already mitigated by `LLM_API_KEY: no-key-needed` + `minimax` alias
- **BrowserBase session quota hit** → Coordinator monitors for 429s; if exceeded, swap to self-hosted STDIO + Anthropic

## Files referenced by this runbook

- `infrastructure/komodo/stacks/storage-lakehouse.toml` — Komodo lakehouse definition
- `infrastructure/komodo/procedures/storage-lakehouse.toml` — Komodo lakehouse procedure
- `infrastructure/komodo/stacks/cognee-bunchloch.toml` — Komodo cognee definition
- `infrastructure/komodo/procedures/deploy-cognee-bunchloch.toml` — Komodo cognee procedure
- `infrastructure/stacks/litellm/config/config.yaml` — LiteLLM gateway config (default_model: minimax)
- `cianfhoghlaim/stacks/cognee/compose.yaml` — Cognee compose (LLM_MODEL default: minimax)
- `openspec/changes/2026-06-28-rewrite-subagent-foundation-for-cianfhoghlaim-consolidation/` — agent-registry change
- `openspec/changes/2026-06-28-browserbase-phase-{1a,1b,2,3}-decisions/` — research stubs

## Next after Phase 0.3-0.8: Tier 2 + bulk launch

Once the Tier 1 deploy is verified (Cognee responds, LiteLLM routes to
minimax, BrowserBase session works), proceed to Tier 2 (graphiti +
falkordb + dragonfly + risingwave). Then the 43-prompt bulk launch.
