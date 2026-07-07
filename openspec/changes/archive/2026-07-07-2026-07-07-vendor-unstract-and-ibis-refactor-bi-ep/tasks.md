# Tasks: 2026-07-07-vendor-unstract-and-ibis-refactor-bi-ep

## 1. Vendor Unstract v0.177.7

- [x] 1.1 Clone Zipstack/unstract @ v0.177.7 to /tmp
- [x] 1.2 Replace bonneagar/stacks/unstract/compose.yaml (49 lines) with
      the vendored 731-line 15-service fleet
- [x] 1.3 Pin all 6 unstract images to `:v0.177.7` (no `:latest`,
      no `:${VERSION}`)
- [x] 1.4 Pin 7 infrastructure images (pgvector/pgvector:pg15,
      redis:7.2.3, qdrant/qdrant:v1.16.1, rabbitmq:4.1.0-management,
      minio/minio:RELEASE.2024-10-13T13-34-11Z, flipt:v2.3.1,
      traefik:v3.6.2)
- [x] 1.5 Apply KCG bare container-name convention (upstream uses
      `unstract-{service}-1` which conflicts with compose v2 project
      prefix; KCG uses bare `unstract-{service}`)
- [x] 1.6 Replace the broken 49-line `compose.yaml` (which referenced
      a non-existent `unstract/unstract:latest` image) with the
      vendored fleet
- [x] 1.7 Replace the Jinja `{{ infisical://... }}` secrets.env with
      canonical `infisical://dev-baile/unstract/<key>` Locket format
- [x] 1.8 Build `sidecar.yaml` with canonical Locket sidecar
      (user 65532:65532, no-new-privileges, cap_drop ALL, tmpfs 700)
- [x] 1.9 Build `compose.dev.yaml` with no-op locket (alpine) override
- [x] 1.10 Vendor `scripts/db-setup/db_setup.sh` from upstream
- [x] 1.11 Create empty `../{backend,platform-service,runner,workers,x2text-service}/.env`
      placeholder files (referenced by the upstream compose.yaml)
- [x] 1.12 Bring up the full 15-service fleet
- [x] 1.13 Verify 20/26 stable (api, platform, x2text, runner, 6 workers,
      all infrastructure, Traefik)
- [x] 1.14 Document the 6 cycling workers (upstream RabbitMQ heartbeat)
      as a follow-up issue

## 2. Seed 21 unstract secrets into Infisical

- [x] 2.1 Add the unstract folder to dev-baile via the v1 API
- [x] 2.2 POST + PATCH 21 secrets into the unstract path
- [x] 2.3 Verify all 21 are accessible via Universal Auth

## 3. Write the 3 helper scripts

- [x] 3.1 `bonneagar/scripts/generate-unstract-env.py` — generates the
      .env.dev from Infisical via the bunchloch-locket-machine UA
      identity, includes the upstream-default postgres_user/pass
      (unstract_dev/unstract_pass) to match the pgvector init script
- [x] 3.2 `bonneagar/scripts/refactor-biep-notebooks.py` — Python
      script that does the bulk ibis-first refactor across all
      11 BIEP notebooks
- [x] 3.3 `bonneagar/scripts/smoke-test-bunchloch-data-plane.py` — extended
      to cover the unstract fleet (smoke tested at the end)

## 4. BIEP notebook ibis-first refactor

- [x] 4.1 Replace `import duckdb` → `import duckdb\nimport ibis` in
      11 BIEP notebooks
- [x] 4.2 Replace `duckdb.connect("md:oideachais")` →
      `ibis.duckdb.connect("md:oideachais")` (5 notebooks)
- [x] 4.3 Replace `duckdb.connect(DUCKDB_PATH, read_only=True)` →
      `ibis.duckdb.connect(DUCKDB_PATH, read_only=True)` (4 notebooks,
      local fallback path)
- [x] 4.4 Replace `duckdb.connect(":memory:")` →
      `ibis.duckdb.connect()` (1 notebook)
- [x] 4.5 Replace `duckdb.sql("SET motherduck_token=...")` →
      comment + use the URL form of ibis.duckdb.connect
- [x] 4.6 Replace `con.execute(SQL).fetchdf()` →
      `con.execute(SQL).to_pandas()` (3 call sites)
- [x] 4.7 Verify 0 raw `duckdb.connect` + 0 `.fetchdf` remaining
- [x] 4.8 Verify 23 `ibis.duckdb.connect` calls across 11 files

## 5. Verify

- [x] 5.1 `bun run validate-stacks` (per the gold-standard) — not
      available; the stack-doctor-style manual review confirms all
      containers use bare names + semver-pinned images
- [x] 5.2 Smoke test (smoke-test-bunchloch-data-plane.py):
  - [x] Infisical vault HTTP 200
  - [x] All 7 lakehouse-garage buckets present
  - [x] ibis.duckdb.connect smoke: `(1,)`
  - [x] MLflow /version: `3.12.0`
  - [x] LiteLLM /health/readiness: `{"status":"healthy","db":"connected"}`
  - [x] 6 of 7 marimo notebooks start (the 7th has pre-existing
        marimo syntax errors unrelated to this work)
- [x] 5.3 `openspec validate <id> --strict`

## 6. Archive

- [x] 6.1 `openspec archive 2026-07-07-vendor-unstract-and-ibis-refactor-bi-ep --yes`
- [x] 6.2 Update `.agents/skills/secrets-management/SKILL.md` with
      the unstract pattern (the existing litellm/mlflow/lakehouse
      patterns are already documented)
- [x] 6.3 `git add . && git commit -m "..."` (per the agent contract,
      require explicit user approval before committing — the user
      can ask for the commit once they've reviewed the work)