# Tasks: pipeline-lakehouse-data-plane

> Cross-batch lakehouse + IaC remediation + edge routing contract.
> Absorbs `2026-08-13-bonneagar-infra-remediation-v3` (0/18) +
> `2026-08-15-lakehouse-unified-data-plane-v1` (0/44) +
> `2026-09-13-delete-deprecated-graph-db-stacks` (0/20) +
> `2026-08-13-edge-routing-and-offline-site-remediation-v1` (0/14).

## 1. Bonneagar infra remediation v3 (from bonneagar-infra-remediation-v3)

- [ ] **L1.1** Fix the 11 litellm model-name mismatches (`-it-GGUF` / `-Instruct-GGUF` suffixes)
- [ ] **L1.2** Fix the llama-swap image tag
- [ ] **L1.3** Reconcile `storage-infrastructure.toml:14` (dead pre-merge `cliste/bonneagar` repo namespace)
- [ ] **L1.4** Automate bootstrap Phases 6/6b/7 (replace 3 `logWarn("not yet automated")` blocks with `deployKomodoCore()` + auto-deployed tiny-auth)
- [ ] **L1.5** Fix the openchamber SHA256 pin (deterministic mock)

## 2. Lakehouse unified data plane (from lakehouse-unified-data-plane-v1)

- [ ] **L2.1** Consolidate `bonneagar/stacks/lakehouse/compose.yaml` (grow from 11 → 16 services)
- [ ] **L2.2** Migrate the 5 graph DB backends (Cognee + Graphiti + FalkorDB + Memgraph + LanceDB Viewer) into the unified lakehouse stack
- [ ] **L2.3** Add deprecation banners to the 4 deprecated standalone stacks (cognee + graphiti + falkordb + memgraph)
- [ ] **L2.4** Verify `docker compose -f compose.yaml -f sidecar.yaml up -d` brings up all 16 services on `lakehouse_lakehouse` network

## 3. Delete the 5 deprecated graph-DB stacks (from delete-deprecated-graph-db-stacks)

- [ ] **L3.1** Delete `bonneagar/stacks/cognee/` (all 6 GOLD_STANDARD files)
- [ ] **L3.2** Delete `bonneagar/stacks/graphiti/` (all 6 GOLD_STANDARD files)
- [ ] **L3.3** Delete `bonneagar/stacks/falkordb/` (all 6 GOLD_STANDARD files)
- [ ] **L3.4** Delete `bonneagar/stacks/memgraph/` (all 6 GOLD_STANDARD files)
- [ ] **L3.5** Delete `bonneagar/stacks/lancedb/` (all 6 GOLD_STANDARD files)
- [ ] **L3.6** Remove deprecation banner references in `bonneagar/stacks/lakehouse/README.md:181` + `infrastructure-stacks/spec.md:73`

## 4. Edge routing + offline-site remediation (from edge-routing-and-offline-site-remediation-v1)

- [ ] **L4.1** Register 7 missing Traefik routers (`litellm` / `langfuse` / `vikunja` / `n8n` / `glance` / `changedetection` / `paperless`)
- [ ] **L4.2** Add 10 NEW Pangolin `siteResources` rows
- [ ] **L4.3** Rebind 3 offline-site rows (`infisical` / `openchamber` / `komodo`) to `arm1-oci`
- [ ] **L4.4** Add `cron-edge-tls-probe-both.toml` Komodo procedure (hourly probe)
- [ ] **L4.5** Update `infrastructure-stacks/spec.md` — new requirement: every `*.cianfhoghlaim.ie` hostname MUST have a live Traefik router AND a live Pangolin siteResource

## 5. Verification

- [ ] Run `openspec validate pipeline-lakehouse-data-plane --strict` — pass
- [ ] Run `docker compose -f bonneagar/stacks/lakehouse/compose.yaml config` — pass
- [ ] Run `curl -kI https://litellm.cianfhoghlaim.ie` — 200 (was verify code 21)
- [ ] Run `curl -kI https://infisical.cianfhoghlaim.ie` — 200 (was HTTP 000)

## Verification

```bash
cd ~/dev/cianchosaint-laim 2>/dev/null || cd ~/dev/cianchoghlaim
openspec validate pipeline-lakehouse-data-plane --strict
```
