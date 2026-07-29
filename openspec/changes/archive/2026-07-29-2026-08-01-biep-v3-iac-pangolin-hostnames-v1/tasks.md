# 2026-08-01-biep-v3-iac-pangolin-hostnames-v1 — Tasks

## Pre-implementation

- [ ] Verify openspec CLI ≥1.4: `openspec --version` → 1.4.1
- [ ] Verify A2 (bonneagar IaC rename) merged
- [ ] Verify the ccc code index is fresh: `bun run ccc:index`

## Stage 1 — Update the 5 Pangolin router hostnames

- [ ] Edit `bonnegar/stacks/cianfhoghlaim/pangolin.yaml:8-112`
  - Router 1 (`oideachais-web`): `hostname: oideachais-web.cianfhoghlaim.ie` → `hostname: web.cianfhoghlaim.ie`
  - Router 2 (`oideachais-api`): `hostname: api.oideachais.cianfhoghlaim.ie` → `hostname: api.cianfhoghlaim.ie`
  - Router 3 (`oideachais-dagster`): `hostname: dagster.oideachais.cianfhoghlaim.ie` → `hostname: dagster.cianfhoghlaim.ie`
  - Router 4 (`oideachais-agent-os`): `hostname: agents.oideachais.cianfhoghlaim.ie` → `hostname: agents.cianfhoghlaim.ie`
  - Router 5 (`oideachais-adk-agents`): `hostname: adk-agents.oideachais.cianfhoghlaim.ie` → `hostname: adk-agents.cianfhoghlaim.ie`
- [ ] Verify the corresponding service URLs are updated (e.g.
  `url: http://cianchfhoghlaim-oideachais-web:port` → `url: http://cianchfhoghlaim-cie-web:port`)

## Stage 2 — Update CORS middleware name

- [ ] Edit `bonnegar/stacks/cianfhoghlaim/pangolin.yaml` line ~50 —
  rename `oideachais-cors` → `cianfhoghlaim-cors`

## Stage 3 — Spec delta + validation

- [ ] Write the spec delta to
  `openspec/changes/2026-08-01-biep-v3-iac-pangolin-hostnames-v1/specs/infrastructure-stacks/spec.md`
- [ ] Run `openspec validate 2026-08-01-biep-v3-iac-pangolin-hostnames-v1 --strict`
- [ ] Commit the change on a dedicated branch
- [ ] Open a PR on `origin/main` referencing this change
- [ ] After the PR merges and the change is deployed, run
  `openspec archive 2026-08-01-biep-v3-iac-pangolin-hostnames-v1 --yes`

## Post-implementation hand-off

- [ ] File any remaining bugs as GitHub issues
- [ ] Run `./scripts/sync_agent_docs.sh` per the global agent protocol