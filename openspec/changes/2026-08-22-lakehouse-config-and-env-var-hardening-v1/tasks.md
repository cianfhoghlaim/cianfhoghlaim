# Tasks: 2026-08-22-lakehouse-config-and-env-var-hardening-v1

## Phase 1: Openspec change skeleton (3 tasks)

- [ ] **T1.1**: Create `openspec/changes/2026-08-22-lakehouse-config-and-env-var-hardening-v1/proposal.md` (the why + what changes)
- [ ] **T1.2**: Create `openspec/changes/2026-08-22-lakehouse-config-and-env-var-hardening-v1/tasks.md` (this file)
- [ ] **T1.3**: Create `openspec/changes/2026-08-22-lakehouse-config-and-env-var-hardening-v1/specs/infrastructure-stacks/spec.md` (the 2 ADDED Requirements + 1 MODIFIED Requirement)

## Phase 2: Validate (1 task)

- [ ] **T2.1**: Run `openspec validate 2026-08-22-lakehouse-config-and-env-var-hardening-v1 --strict` and verify it passes

## Phase 3: lakehouse/compose.yaml (1 file, 6 modifications)

- [ ] **T3.1**: Switch `postgres:16-alpine` → `pgvector/pgvector:pg17` (line ~208) — single image includes pgvector + postgresql-contrib
- [ ] **T3.2**: Add `depends_on: [lance-namespace: service_healthy]` to cognee service (currently only has `postgres` + `locket`)
- [ ] **T3.3**: Add `deploy.resources.limits: { cpus: "0.5", memory: 512M }` to lance-namespace service
- [ ] **T3.4**: Add `deploy.resources.limits: { cpus: "1.0", memory: 1G }` to memgraph service
- [ ] **T3.5**: Add `deploy.resources.limits: { cpus: "0.5", memory: 256M }` to memgraph-lab service
- [ ] **T3.6**: Replace Memgraph `healthcheck` (line ~XXX) — `["CMD", "echo", ">", "/dev/tcp/localhost/7687"]` → `["CMD-SHELL", "curl -sf http://localhost:7444/status || exit 1"]`

## Phase 4: lakehouse/init-db.sql (1 file, 2 modifications)

- [ ] **T4.1**: Add `CREATE EXTENSION IF NOT EXISTS` for the 6 required extensions AFTER the CREATE DATABASE block, BEFORE the GRANT block:
  - `uuid-ossp`
  - `pgcrypto`
  - `pg_trgm`
  - `btree_gin`
  - `btree_gist`
  - `vector` (pgvector — needed by Cognee)
- [ ] **T4.2**: Add `CREATE DATABASE olake_source;` (after the 12 existing + cognee_cianfhoghlaim) + `GRANT ALL PRIVILEGES ON DATABASE olake_source TO lakekeeper;` — total = 14 databases

## Phase 5: lakehouse/sidecar.yaml (1 file, 1 modification)

- [ ] **T5.1**: Replace hardcoded absolute `infisical_secret` path (line 101):
  ```yaml
  # FROM:
  secrets:
    infisical_secret:
      file: /Users/cianmacandeisigh/dev/kings_college_galway/bonneagar/stacks/infisical/infisical_secret

  # TO:
  secrets:
    infisical_secret:
      file: ${INFISICAL_SECRET_FILE:-./infisical_secret}
  ```

## Phase 6: lakehouse/compose.yaml (continued) — Olake source DB (1 modification)

- [ ] **T6.1**: Update Olake `SOURCE_DB_NAME` env var (line ~XXX):
  ```yaml
  # FROM:
  SOURCE_DB_NAME: ${OLAKE_SOURCE_DB:-staging_pg}

  # TO:
  SOURCE_DB_NAME: ${OLAKE_SOURCE_DB:-olake_source}
  ```

## Phase 7: root .infisical.env (1 file, 8 key removals)

- [ ] **T7.1**: Remove `COGNEE_API_URL=http://localhost:8001` (cognee is now at :8000 in lakehouse)
- [ ] **T7.2**: Remove `COGNEE_DB_USERNAME=cognee` (now `POSTGRES_USER: lakekeeper` in shared lakehouse-postgres)
- [ ] **T7.3**: Remove `COGNEE_DB_PASSWORD=devpassword` (cognee uses shared `POSTGRES_PASSWORD` via Locket)
- [ ] **T7.4**: Remove `COGNEE_DB_NAME=cognee` (now `cognee_cianfhoghlaim` in lakehouse)
- [ ] **T7.5**: Remove `FALKORDB_URL=redis://localhost:6379` (graphiti uses Docker DNS `falkordb:6379` inside lakehouse)
- [ ] **T7.6**: Remove `FALKORDB_GRAPH=curriculum_cache` (lakehouse uses `FALKORDB_GRAPHITI_DB`)
- [ ] **T7.7**: Remove `MEMGRAPH_URI=bolt://localhost:7687`, `MEMGRAPH_USER=memgraph`, `MEMGRAPH_PASSWORD=devpassword` (lakehouse has its own `MEMGRAPH_*` keys)
- [ ] **T7.8**: Remove `R2_DUCKLAKE_BUCKET=ducklake` (consolidate to `DUCKLAKE_BUCKET=ducklake` only)
- [ ] **T7.9**: Consolidate `LANCEDB_API_KEY=infisical://dev-baile/lancedb-cloud/api_key` → remove (canonical path is `infisical://dev-baile/lancedb/api_key` in lakehouse)

## Phase 8: .env.dev → empty-value template (1 file rewrite)

- [ ] **T8.1**: Rewrite `bonneagar/stacks/lakehouse/.env.dev` as empty-value template:
  - Keep ALL the keys (POSTGRES_PASSWORD, GARAGE_ACCESS_KEY_ID, etc.)
  - Clear all values to blank
  - Add inline `# DEV: populate from Infisical via 'mise run secrets:init' or copy from .env.local` comments
  - Add a header comment explaining: ".env.dev is the empty-value template. Plaintext secrets live in .env.local (gitignored)."

## Phase 9: .env.local (1 file NEW — gitignored)

- [ ] **T9.1**: Create `bonneagar/stacks/lakehouse/.env.local` (gitignored per `.gitignore:177`) with:
  - All 26 keys from the old `.env.dev`
  - Real plaintext secret values from `dev-baile/lakehouse/*` (operator populates via `mise run secrets:init`)
  - Header comment: "Local secrets — populated by 'mise run secrets:init' from dev-baile vault. NEVER commit. .env.local is in .gitignore."
- [ ] **T9.2**: Add `INFISICAL_SECRET_FILE=./infisical_secret` to `.env.local` (new env var from T5.1)

## Phase 10: CI secret-scan (1 file NEW)

- [ ] **T10.1**: Create `.github/workflows/lakehouse-secret-scan.yml`:
  - Trigger: PR + push to main
  - Job: runs `gitleaks` against `bonneagar/stacks/lakehouse/` + `dlt_sources/common/destinations_cianfhoghlaim.py` + `notebooks/_shared/schema.py`
  - On detection: fail the workflow
  - Allowlist: `.env.local`, `.env.example`, `.env.local.example`, `.env.dev` (the empty template)

## Phase 11: Quality gates (4 tasks)

- [ ] **T11.1**: Run `openspec validate 2026-08-22-lakehouse-config-and-env-var-hardening-v1 --strict` and verify it passes
- [ ] **T11.2**: Run `docker compose -f compose.yaml -f sidecar.yaml config --quiet` (in `bonneagar/stacks/lakehouse/`) and verify it passes
- [ ] **T11.3**: Run `mise run cic:stack-doctor` and verify no new critical/warnings
- [ ] **T11.4**: Run `mise run lint:skills`, `mise run lint:drift-docs`, `mise run lint:registry` and verify all green

## Phase 12: Commit + push (2 tasks)

- [ ] **T12.1**: Stage only the 11 PR #1 files:
  - `openspec/changes/2026-08-22-lakehouse-config-and-env-var-hardening-v1/{proposal.md, tasks.md, specs/infrastructure-stacks/spec.md}`
  - `bonneagar/stacks/lakehouse/{compose.yaml, sidecar.yaml, init-db.sql, .env.dev}`
  - `.infisical.env`
  - `.github/workflows/lakehouse-secret-scan.yml`
  - DO NOT stage: 15+ pre-existing uncommitted changes from earlier sessions
- [ ] **T12.2**: Commit with descriptive message + push to `origin/token-plan-lc-pipeline-2026-08`

## Total: 24 tasks across 12 phases

Estimated effort: ~4 hours of file edits + ~30 minutes for openspec validate + CI gates.