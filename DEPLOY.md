# DEPLOY.md — End-to-End Deploy Playbook

> The 8-phase + 1 rollback procedure for deploying the entire
> Cianfhoghlaim monorepo to a fresh `bunchloch` (MacBook M4)
> + `arm1-oci` (Oracle Cloud Ampere A1) cluster. **Read this
> before** running any of the 5 quadrant deploys.

This playbook is the canonical deploy procedure for the
Cianfhoghlaim platform. It is duplicated in `README.md` §
"8-phase end-to-end deploy playbook". The standalone version
is here for users who want the playbook without the monorepo
overview.

---

## Phase 0: Pre-flight (~10 minutes)

Before deploying anything, verify the toolchain, the secrets,
and the 2 hosts.

### 0.1 Toolchain

```bash
# 1. Install mise (the toolchain manager)
curl https://mise.run | sh
eval "$(mise activate bash)"

# 2. Install the toolchain (python 3.12, uv, bun, dagger, pulumi,
#    duckdb, sops, opencode)
cd /Users/cianmacandeisigh/dev/kings_college_galway
mise install

# 3. Verify
mise list          # should show 8+ tools
mise doctor        # should return 0
```

### 0.2 Workspace

```bash
# 4. Install the bun + uv workspaces
bun install        # the TypeScript graph (3 workspaces)
uv sync            # the Python graph (6 workspace members)

# 5. Verify
bun run turbo build --dry-run   # should show 8+ build tasks
uv run python -c "import oideachais; import meaisinfhoghlaim; import tuatha; import croilar"  # should succeed
```

### 0.3 Secrets

```bash
# 6. Hydrate the .env from .infisical.env
bun run secrets:env       # copies the template to .env

# 7. Sync .env to the Infisical dev-baile vault
bun run secrets:init      # idempotent; safe to re-run

# 8. Verify
cat .env | head -10       # should show resolved secrets (not infisical:// URIs)
mise run infisical:list   # should list 30+ secrets in the vault
```

### 0.4 Hosts

```bash
# 9. Verify the 2 hosts are reachable
ssh arm1-oci              # should connect to the OCI Ampere A1
ssh bunchloch             # should connect to the MacBook M4

# 10. Verify the Docker daemons
ssh arm1-oci "docker ps"  # should show 10+ running containers
docker ps                 # should show 35+ running containers on bunchloch
```

**If any of these fail, fix before continuing to Phase 1.**

---

## Phase 1: Infrastructure (~30 minutes)

The infrastructure phase is the foundation. Everything else
depends on it. The 5 sub-phases are:

### 1.1 Infisical vault (~5 min)

```bash
# 1. Start the local Infisical dev server (if not already running)
cd infrastructure/infisical
docker compose up -d
sleep 5

# 2. Verify
curl -s http://localhost:8888/api/status | jq  # should return 200

# 3. Create the dev-baile environment (first time only)
bun run scripts/create-env.ts

# 4. Sync the .env + .infisical.env to the vault
cd /Users/cianmacandeisigh/dev/kings_college_galway
bun run secrets:init
```

### 1.2 Komodo control plane (~5 min)

```bash
# 1. Deploy the Komodo stack
cd infrastructure/stacks/komodo
docker compose up -d
sleep 10

# 2. Verify
curl -s http://komodo.cianfhoghlaim.ie/api/status  # should return 200

# 3. Verify the 2 hosts are registered
curl -s -H "X-Api-Key: $KOMODO_API_KEY" \
  http://komodo.cianfhoghlaim.ie/api/servers | jq  # should show 2 servers
```

### 1.3 Pangolin mesh (~5 min)

```bash
# 1. Deploy the Pangolin stack (VPN + Traefik + Pocket ID)
cd infrastructure/stacks/pangolin
docker compose up -d
sleep 10

# 2. Verify
curl -s https://pangolin.cianfhoghlaim.ie/api/health | jq  # should return 200

# 3. Verify the WireGuard tunnel is up
sudo wg show  # should show the bunchloch + arm1-oci peers
```

### 1.4 Locket sidecar (~5 min)

```bash
# 1. Verify Locket is injected into all the 4 quadrant stacks
cd infrastructure/stacks/litellm
docker compose ps | grep locket    # should show 1 locket container per stack

# 2. Test the secret injection
docker exec litellm-locket-1 locket inject --service=litellm --secret=LITELLM_MASTER_KEY
# should print the resolved secret (not the infisical:// URI)
```

### 1.5 4 quadrant stacks (~10 min)

Deploy the 4 quadrant stacks (infra-first, then the 4
quadrants in dependency order):

```bash
# 1. The infrastructure-first stacks
for stack in garage lakehouse litellm lancedb langfuse; do
  cd infrastructure/stacks/$stack
  docker compose up -d
done

# 2. Verify each
for stack in garage lakehouse litellm lancedb langfuse; do
  echo "=== $stack ==="
  docker compose -f infrastructure/stacks/$stack/compose.yaml ps
done
```

**If any stack fails, fix before continuing to Phase 2.**

---

## Phase 2: Oideachais (~20 minutes)

The oideachais phase deploys the lakehouse (Dagster + FastAPI
+ TanStack Start + Agno AgentOS + Google ADK).

```bash
# 1. Build the 4 docker images
cd /Users/cianmacandeisigh/dev/kings_college_galway
mise run turbo build --filter=oideachais

# 2. Deploy the oideachais stack
cd infrastructure/stacks/oideachais
docker compose up -d
sleep 30

# 3. Verify the 5 services
curl -s http://oideachais.cianfhoghlaim.ie:8000/health | jq
curl -s http://oideachais.cianfhoghlaim.ie:3335/server_info | jq
curl -s http://oideachais.cianfhoghlaim.ie:7777/health | jq
curl -s http://oideachais.cianfhoghlaim.ie:7778/health | jq
curl -s http://oideachais.cianfhoghlaim.ie:3080/ | head -5

# 4. Run the Dagster materialise
curl -s -X POST -H "Content-Type: application/json" \
  -d '{"job": "oideachais_full_etl"}' \
  http://oideachais.cianfhoghlaim.ie:3335/graphql \
  | jq .data.launchPipelineExecution.run.runId
```

---

## Phase 3: Meaisínfhoghlaim (~15 minutes)

The meaisínfhoghlaim phase deploys the AI/ML services
(llama-swap + mlx-omni + invokeai + the 12 agents).

```bash
# 1. Build the docker images
cd /Users/cianmacandeisigh/dev/kings_college_galway
mise run turbo build --filter=meaisinfhoghlaim

# 2. Deploy the meaisínfhoghlaim stack
cd infrastructure/stacks/meaisinfhoghlaim
docker compose up -d
sleep 15

# 3. Verify the 4 inference backends
curl -s http://llama-swap.cianfhoghlaim.ie:8080/health | jq
curl -s http://mlx-omni.cianfhoghlaim.ie:10240/health | jq
curl -s http://invokeai.cianfhoghlaim.ie:9090/health | jq
curl -s http://litellm.cianfhoghlaim.ie:4000/health | jq

# 4. Run the 4 heartbeat Dagster assets
curl -s -X POST -H "Content-Type: application/json" \
  -d '{"job": "meaisin_heartbeat"}' \
  http://oideachais.cianfhoghlaim.ie:3335/graphql \
  | jq .data.launchPipelineExecution.run.runId
```

---

## Phase 4: Tuatha (~15 minutes)

The tuatha phase deploys the MMO + the crypteolas
achievement ledger.

```bash
# 1. Build the docker images
cd /Users/cianmacandeisigh/dev/kings_college_galway
mise run turbo build --filter=tuatha

# 2. Deploy the tuatha stack
cd infrastructure/stacks/tuatha
docker compose up -d
sleep 15

# 3. Verify the 4 sub-modules
curl -s http://tuatha.cianfhoghlaim.ie:8000/health | jq
curl -s http://tuatha.cianfhoghlaim.ie:3335/server_info | jq
curl -s http://tuatha.cianfhoghlaim.ie:7777/health | jq
curl -s http://tuatha.cianfhoghlaim.ie:3080/ | head -5

# 4. Start the SpacetimeDB server (the MMO server)
cd sruth/tuatha/crates/game_server
cargo run --release &
sleep 10

# 5. Verify
curl -s http://localhost:3000/v1/identity | jq  # should return the server identity
```

---

## Phase 5: Croílár (~15 minutes)

The croílár phase deploys the 3-persona portfolio +
the DevTools Hub.

```bash
# 1. Build the bun workspaces
cd /Users/cianmacandeisigh/dev/kings_college_galway
bun run turbo build --filter=croilar

# 2. Deploy the croílár stack (5 sub-stacks)
for stack in croilar-web croilar-portal croilar-dagster croilar-hono-api croilar-marimo; do
  cd infrastructure/stacks/$stack
  docker compose up -d
done

# 3. Verify
curl -s http://croilar-web.cianfhoghlaim.ie/ | head -5
curl -s http://croilar-portal.cianfhoghlaim.ie/ | head -5
curl -s http://croilar-dagster.cianfhoghlaim.ie:3335/server_info | jq
curl -s http://croilar-hono-api.cianfhoghlaim.ie/api/health | jq
```

---

## Phase 6: Spaces (~5 minutes)

The spaces phase deploys the 4 active HuggingFace Spaces
(sync via the reusable workflow).

```bash
# 1. Trigger the 4 per-Space sync workflows
for space in an_scrudu meaisin_cliste cianfhoghlaim anam_tuatha; do
  gh workflow run "Sync $space to HF" \
    --repo cianfhoghlaim/kings_college_galway \
    --ref main
done

# 2. Verify
gh run list --workflow="Sync *_to HF" --limit=4
# All 4 should show "completed" within 5 minutes
```

---

## Phase 7: Verify (~5 minutes)

Run the 4 audit scripts + the `stack-doctor` CI gate:

```bash
# 1. Inventory the bunchloch host
bash infrastructure/audit/scripts/inventory-bunchloch.sh \
  | tee /tmp/bunchloch-inventory.json
cat /tmp/bunchloch-inventory.json | jq '.containers | length'
# should show 35+ containers

# 2. Inventory the arm1-oci host
bash infrastructure/audit/scripts/inventory-arm1-oci.sh \
  | tee /tmp/arm1-inventory.json
cat /tmp/arm1-inventory.json | jq '.containers | length'
# should show 10+ containers

# 3. Diff against the compose files
bash infrastructure/audit/scripts/diff-against-composes.sh
# should return exit 0 (no orphan / missing / conflict)

# 4. Probe the public URLs
bash infrastructure/audit/scripts/probe-public-urls.sh
# should return exit 0 (all <service>.cianfhoghlaim.ie URLs are 200)

# 5. The stack-doctor CI gate
bun run validate-stacks
# should return exit 0 (no stack-doctor failures)
```

---

## Phase 8: Rollback (~5 minutes)

If any phase fails, the canonical rollback procedure is:

```bash
# 1. Locket sidecar auto-rollback
# (each sidecar keeps a 24-hour history of injected secrets;
#  the rollback restores the last-known-good secret)
docker exec <stack>-locket-1 locket rollback --service=<stack>

# 2. Infisical version restore
# (each secret keeps a version history; restore the last-known-good)
infisical secrets revert \
  --projectId=<project-id> \
  --environment=dev-baile \
  --secretName=<secret-name> \
  --version=<last-known-good-version>

# 3. Komodo stack disable
curl -s -X POST -H "X-Api-Key: $KOMODO_API_KEY" \
  "http://komodo.cianfhoghlaim.ie/api/stack/<stack>/disable" | jq

# 4. Verify the rollback
bash infrastructure/audit/scripts/diff-against-composes.sh
# should return exit 0
```

---

## Cross-references

- [`README.md`](README.md) — the monorepo overview (duplicates this playbook)
- [`infrastructure/README.md`](infrastructure/README.md) — the 94-stack inventory
- [`sruth/oideachais/README.md`](sruth/oideachais/README.md) — the lakehouse quadrant
- [`sruth/meaisinfhoghlaim/README.md`](sruth/meaisinfhoghlaim/README.md) — the AI/ML quadrant
- [`sruth/tuatha/README.md`](sruth/tuatha/README.md) — the MMO + crypto quadrant
- [`sruth/croilar/README.md`](sruth/croilar/README.md) — the portfolio quadrant
- [`spaces/README.md`](spaces/README.md) — the HuggingFace Spaces
- [`.agents/skills/kcg-pangolin-stack/SKILL.md`](.agents/skills/kcg-pangolin-stack/SKILL.md) — the Pangolin pattern
- [`.agents/skills/kcg-locket-sidecar/SKILL.md`](.agents/skills/kcg-locket-sidecar/SKILL.md) — the Locket pattern
- [`.agents/skills/kcg-infrastructure-audit/SKILL.md`](.agents/skills/kcg-infrastructure-audit/SKILL.md) — the 4 audit scripts
- [`.agents/skills/stack-ops/SKILL.md`](.agents/skills/stack-ops/SKILL.md) — the stack-ops pattern
- [`openspec/changes/kcg-monorepo-readme-expansion/`](openspec/changes/kcg-monorepo-readme-expansion/) — the round 13 openspec change
