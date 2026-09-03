# 2026-08-01-bonneagar-iac-namespace-alignment-v1

## Why

The Bonneagar IaC stack catalogue was NOT renamed by the BIEP v3 Phase 0
rename (which was scoped to the cianfhoghlaim code only, not the IaC).
This means the `oideachais` namespace still appears across 40+ files
in `bonneagar/`, including:

- The entire `bonneagar/stacks/oideachais/` directory (6 files)
- 7 Komodo resource files (stacks + procedures + resource-syncs)
- Cognee dataset names + DB name
- lakehouse init-db.sql + .env.dev
- agent-os compose + secrets + sidecar
- `.infisical.env` runtime vars + 2 secret paths
- motherduck compose
- 5 cross-stack references in `dagster-unified.toml`, `key-stacks.ts`,
  `croilar-glance-regenerate.toml`, `server_id_legend.md`, etc.

This blocks live deploy of the BIEP v3 stack. A2 must land before
A3 (Pangolin hostnames) which depends on the new
`bonneagar/stacks/cianfhoghlaim/` directory created here.

This is the A2 blocker change. It lives in the **bonneagar repo** (not
the cianfhoghlaim repo) per the 2-repo split convention.

## What changes

### 1. Rename `bonneagar/stacks/oideachais/` → `bonneagar/stacks/cianfhoghlaim/`

- `git mv` the entire directory
- 6 files inside: `blueprint.yaml`, `compose.yaml`, `compose.dev.yaml`,
  `pangolin.yaml`, `sidecar.yaml`, `secrets.env` (plus `README.md`)

### 2. Rename 7 Komodo resource files

- `bonneagar/komodo/stacks/oideachais-bunchloch.toml` →
  `bonneagar/komodo/stacks/cianfhoghlaim-bunchloch.toml`
- `bonneagar/komodo/procedures/deploy-oideachais-bunchloch.toml` →
  `bonneagar/komodo/procedures/deploy-cianchfhoghlaim-bunchloch.toml`
- `bonneagar/komodo/procedures/server_id_legend.md` line 42 (rename row)
- `bonneagar/komodo/resource-syncs/bunchloch.toml` line 59 (path)

### 3. Update 8 cross-stack Komodo procedures

- `croilar-glance-regenerate.toml`, `deploy-bunchloch-stack-bootstrap.toml`,
  `deploy-leabharlann-email-inbox-bunchloch.toml`,
  `dagster-unified.toml`, `key-stacks.ts` — 11 `oideachais` refs

### 4. Update Cognee dataset names + DB

- `bonneagar/stacks/cognee/compose.yaml` lines 41, 47, 55, 96, 98:
  6 Cognee dataset names from `oideachais.{aistear,primary,junior_cycle,senior_cycle,tertiary,cross_stage}`
  → `cianfhoghlaim.education.{ireland,england,scotland,wales,northern_ireland,crown_dependencies}`
- DB name `cognee_oideachais` → `cognee_cianfhoghlaim`
- `compose.dev.yaml`, `.env.dev`, `README.md` — 4 additional files

### 5. Update lakehouse init-db.sql + env

- `init-db.sql` lines 27, 59: `ducklake_oideachais` → `ducklake_cianfhoghlaim`
- `.env.dev` lines 7, 9: `CLICKHOUSE_USER` + `CLICKHOUSE_DB` → `cianfhoghlaim`
- `notebooks/lakehouse_pipeline.py` line 54, 127: `lakehouse_oideachais` → `lakehouse_cianfhoghlaim`
- `README.md` lines 101, 105: 2 path references
- 5 files total

### 6. Update agent-os

- `blueprint.yaml` line 44-52: resource name + hostname
- `compose.yaml` lines 5-203: 11 `oideachais` references (images, container names, env vars, volumes)
- `sidecar.yaml` line 32: service name
- `secrets.env` line 18: Infisical path
- `README.md` lines 46, 61
- `.env.example` line 17
- 6 files total

### 7. Update `.infisical.env`

- Lines 173, 261, 270: 3 runtime vars (`DUCKLAKE_POSTGRES_DB`, `DUCKDB_PATH`, `MOTHERDUCK_DATABASE`)
- Lines 685-686: 2 secret paths (`OIDEACHAIS_LLM_API_KEY`, `OIDEACHAIS_LLM_PROVIDER`)

### 8. Update browser agent_os config

- `bonneagar/stacks/browser/agent_os/config.yaml:71` — drop `oideachais`

### 9. Update iac sources

- `bonneagar/iac/sources/key-stacks.ts:55-85` — rename `oideachais` → `cianfhoghlaim`

### 10. Post-rename vault sync

- Run `bun run scripts/init-vault.ts` to mirror the 2 OIDEACHAIS_LLM_*
  secret renames to the Infisical vault

## Dependencies

```yaml
Blocked by: 2026-07-26-biep-v3-root-namespace-rename-v1
Blocked by (soft): 2026-08-01-biep-v3-dlt-jurisdiction-pipeline-bugfix-v1
Affected repos: bonneagar (primary) + cianfhoghlaim (cross-refs)
```

## Acceptance gates

- `grep -r "oideachais" bonneagar/stacks/ bonneagar/komodo/ .infisical.env
  --exclude-dir=_legacy --exclude=*.bak` returns ZERO non-historical matches
- `bun run scripts/init-vault.ts` succeeds cleanly
- `bun run iac:bootstrap-infisical` runs the renamed stack
- `openspec validate 2026-08-01-bonneagar-iac-namespace-alignment-v1 --strict` passes

## Cross-references

- `bonneagar/stacks/oideachais/` (renamed) → `bonneagar/stacks/cianfhoghlaim/`
- `bonneagar/komodo/stacks/oideachais-bunchloch.toml` (renamed)
- `.infisical.env` (renamed secrets)
- `bonneagar/iac/sources/key-stacks.ts` (renamed stack)
- `.agents/skills/infrastructure-stacks/SKILL.md` — the GOLD_STANDARD stack contract