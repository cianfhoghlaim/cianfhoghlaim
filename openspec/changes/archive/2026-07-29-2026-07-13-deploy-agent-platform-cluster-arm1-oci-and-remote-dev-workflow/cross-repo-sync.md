# Cross-repo sync plan: 2026-07-13-deploy-agent-platform-cluster-arm1-oci-and-remote-dev-workflow

This change touches **2 of the 3 repos**: cianfhoghlaim (this repo) + bonneagar (the IaC + stack repo).

## Repo 1: `cianfhoghlaim` (this repo)

**Branch**: `pick-4-biep-v1`
**Remote**: `origin` → `https://github.com/cianfhoghlaim/cianfhoghlaim.git`

### Files created (5)

1. `openspec/changes/2026-07-13-deploy-agent-platform-cluster-arm1-oci-and-remote-dev-workflow/{proposal,tasks,cross-repo-sync}.md`
2. `openspec/changes/2026-07-13-deploy-agent-platform-cluster-arm1-oci-and-remote-dev-workflow/specs/{agent-platform-cluster,infrastructure-stacks,agentic-frontend-frameworks}/spec.md`

### Files edited (0)

None on this repo.

### Commit shape

```
feat(openspec): deploy agent-platform-cluster to arm1-oci + newt remote-dev workflow

- New openspec change: 2026-07-13-deploy-agent-platform-cluster-arm1-oci-and-remote-dev-workflow
- 3 spec deltas: agent-platform-cluster + infrastructure-stacks + agentic-frontend-frameworks
```

### Push target

`git push origin pick-4-biep-v1`

## Repo 2: `bonneagar` (separate worktree at `./bonneagar/`)

**Branch**: `pick-5b-bonneagar-v5-continuation`
**Remote**: `bonneagar` → `https://github.com/cianfhoghlaim/bonneagar.git`

### Files created (20)

**Stacks (3 new files):**
1. `bonneagar/stacks/openchamber/Dockerfile.openchamber-web` (multi-stage Node 22 build)
2. `bonneagar/stacks/openclaw/Dockerfile.openclaw` (synthetic Dockerfile)
3. `bonneagar/stacks/newt/{docker-compose,sidecar,secrets.env,pangolin,blueprint}.yaml` + `.env.example` (6 files for the newt 6-file GOLD_STANDARD contract)

**Komodo (12 new files):**
4. `bonneagar/komodo/stacks/hermes-arm1-oci.toml`
5. `bonneagar/komodo/stacks/newt-bunchloch.toml`
6. `bonneagar/komodo/procedures/{deploy-hermes-arm1-oci,deploy-langfuse-arm1-oci,deploy-observability-arm1-oci,deploy-agent-platform-cluster-arm1-oci,deploy-newt-bunchloch}.toml` (5 new procedures)
7. `bonneagar/komodo/procedures/{pangolin-first,komodo-core,infisical-first,locket-deploy}.toml` (4 cross-cutting prerequisites)
8. `bonneagar/komodo/procedures/server_id_legend.md` (convention doc)
9. `bonneagar/komodo/builds/{openchamber-arm1-oci,openclaw-arm1-oci,hermes-arm1-oci}.toml` (3 new build resources)

### Files edited (17)

- `bonneagar/komodo/stacks/openchamber-arm1-oci.toml` — point image at `ghcr.io/cianfhoghlaim/openchamber:1.14.1-arm1`
- `bonneagar/komodo/stacks/openclaw-arm1-oci.toml` — point image at `ghcr.io/cianfhoghlaim/openclaw:2026.6-arm1`
- `bonneagar/komodo/resource-syncs/{bunchloch,arm1-oci,cross-cutting}.toml` — comment blocks + resource_path updates
- 14 existing bunchloch `komodo/procedures/*-bunchloch.toml` get `server_id = "bunchloch"` (+1 line each)

### Commit shape

```
feat(komodo): deploy agent-platform-cluster to arm1-oci + newt remote-dev workflow

- New stacks: openchamber/Dockerfile.openchamber-web, openclaw/Dockerfile.openclaw, newt/* (6 GOLD_STANDARD files)
- New Komodo stacks: hermes-arm1-oci, newt-bunchloch
- New Komodo procedures: deploy-{hermes,langfuse,observability,agent-platform-cluster}-arm1-oci,
  deploy-newt-bunchloch, {pangolin-first,komodo-core,infisical-first,locket-deploy}, server_id_legend
- New Komodo Build resources: {openchamber-arm1-oci,openclaw-arm1-oci,hermes-arm1-oci}
- Update openchamber-arm1-oci + openclaw-arm1-oci stack TOMLs to point at code-owned images
- Update 3 resource-sync TOMLs (bunchloch + arm1-oci + cross-cutting) with server_id convention + new paths
- Backfill server_id = "bunchloch" on 14 existing bunchloch procedures
```

### Push target

`git -C bonneagar push bonneagar pick-5b-bonneagar-v5-continuation`
