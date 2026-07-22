# 2026-08-01-bonneagar-iac-namespace-alignment-v1 — Tasks

## Pre-implementation

- [ ] Verify openspec CLI ≥1.4: `openspec --version` → 1.4.1
- [ ] Verify A1 (dlt bugfix) merged
- [ ] Verify the ccc code index is fresh: `bun run ccc:index`

## Stage 1 — Rename stack directory

- [ ] `git mv bonneagar/stacks/oideachais bonnegar/stacks/cianfhoghlaim`
  (must be done first; A3 depends on it)

## Stage 2 — Rename Komodo resource files

- [ ] `git mv bonneagar/komodo/stacks/oideachais-bunchloch.toml
  bonneagar/komodo/stacks/cianfhoghlaim-bunchloch.toml`
- [ ] `git mv bonnegar/komodo/procedures/deploy-oideachais-bunchloch.toml
  bonnegar/komodo/procedures/deploy-cianchfhoghlaim-bunchloch.toml`
- [ ] Update `bonneagar/komodo/procedures/server_id_legend.md:42`
- [ ] Update `bonneagar/komodo/resource-syncs/bunchloch.toml:59`

## Stage 3 — Update Komodo procedure content

- [ ] Edit `bonneagar/komodo/procedures/croilar-glance-regenerate.toml:6` — update
  the comment that mentions "tuatha, oideachais, croilar, meaisínfhoghlaim"
- [ ] Edit `bonneagar/komodo/procedures/deploy-bunchloch-stack-bootstrap.toml:194,207`
  — update docs that reference `md:oideachais`
- [ ] Edit `bonneagar/komodo/procedures/deploy-leabharlann-email-inbox-bunchloch.toml:10-112`
  — update 5 `oideachais` references in comments + stack targets
- [ ] Edit `bonneagar/komodo/stacks/dagster-unified.toml:5,43-86` — replace
  `OIDEACHAIS_ENABLED=true` + the `oideachais: Celtic education curriculum`
  comment

## Stage 4 — Update Cognee stack

- [ ] Edit `bonneagar/stacks/cognee/compose.yaml:41,47,55,96,98` —
  rename `cognee_oideachais` → `cognee_cianfhoghlaim` and the 6
  Cognee dataset names from `oideachais.{aistear,primary,junior_cycle,senior_cycle,tertiary,cross_stage}`
  to `cianfhoghlaim.education.{ireland,england,scotland,wales,northern_ireland,crown_dependencies}`
- [ ] Edit `bonnegar/stacks/cognee/compose.dev.yaml:7` — `db=cognee_cianfhoghlaim`
- [ ] Edit `bonnegar/stacks/cognee/.env.dev:3,6,11,17` — 4 vars
- [ ] Edit `bonnegar/stacks/cognee/README.md:145-150` — 6 dataset names

## Stage 5 — Update lakehouse stack

- [ ] Edit `bonnegar/stacks/lakehouse/init-db.sql:27,59` — `ducklake_oideachais` →
  `ducklake_cianfhoghlaim` + the GRANT clause
- [ ] Edit `bonnegar/stacks/lakehouse/compose.yaml:189` — comment
- [ ] Edit `bonnegar/stacks/lakehouse/.env.dev:7,9` — `CLICKHOUSE_USER` + `CLICKHOUSE_DB`
- [ ] Edit `bonnegar/stacks/lakehouse/notebooks/lakehouse_pipeline.py:54,127` — `lakehouse_oideachais` → `lakehouse_cianfhoghlaim`
- [ ] Edit `bonnegar/stacks/lakehouse/README.md:101,105` — 2 path references

## Stage 6 — Update agent-os stack

- [ ] Edit `bonnegar/stacks/agent-os/blueprint.yaml:44-52` — resource name +
  hostname `agents.oideachais.cianfhoghlaim.ie` → `agents.cianfhoghlaim.ie`
- [ ] Edit `bonnegar/stacks/agent-os/compose.yaml:5-203` — 11 `oideachais` references
- [ ] Edit `bonnegar/stacks/agent-os/sidecar.yaml:32` — service name
- [ ] Edit `bonnegar/stacks/agent-os/secrets.env:18` — Infisical path
- [ ] Edit `bonnegar/stacks/agent-os/README.md:46,61`
- [ ] Edit `bonnegar/stacks/agent-os/.env.example:17`

## Stage 7 — Update `.infisical.env`

- [ ] Edit `.infisical.env:173` — `DUCKLAKE_POSTGRES_DB=ducklake_cianfhoghlaim`
- [ ] Edit `.infisical.env:261` — `DUCKDB_PATH=./storage/data/cianfhoghlaim.duckdb`
- [ ] Edit `.infisical.env:270` — `MOTHERDUCK_DATABASE=cianfhoghlaim`
- [ ] Edit `.infisical.env:685-686` — rename the 2 OIDEACHAIS_LLM_* secret paths

## Stage 8 — Update browser agent_os config

- [ ] Edit `bonnegar/stacks/browser/agent_os/config.yaml:71` — drop `oideachais`

## Stage 9 — Update iac sources

- [ ] Edit `bonnegar/iac/sources/key-stacks.ts:55-85` — rename `oideachais` → `cianfhoghlaim`

## Stage 10 — Post-rename vault sync

- [ ] Run `bun run scripts/init-vault.ts` to mirror the 2 OIDEACHAIS_LLM_*
  secret renames to the Infisial vault

## Stage 11 — Spec delta + validation

- [ ] Write the spec delta to
  `openspec/changes/2026-08-01-bonneagar-iac-namespace-alignment-v1/specs/infrastructure-stacks/spec.md`
- [ ] Run `openspec validate 2026-08-01-bonneagar-iac-namespace-alignment-v1 --strict`
- [ ] Commit the change on a dedicated branch
- [ ] Open a PR on `origin/main` referencing this change
- [ ] After the PR merges and the change is deployed, run
  `openspec archive 2026-08-01-bonneagar-iac-namespace-alignment-v1 --yes`

## Post-implementation hand-off

- [ ] File any remaining bugs as GitHub issues
- [ ] Run `./scripts/sync_agent_docs.sh` per the global agent protocol