# Bunchloch Infisical + Data Plane Bring-Up (2026-07)

> Pre-flight for the 3 openspec changes
> (`2026-07-06-deploy-infisical-bunchloch-local` →
> `2026-07-06-upgrade-4-stacks-with-infisical` →
> `2026-07-06-wire-biep-notebooks-to-lakehouse`).
> Run the phases IN ORDER. Each phase's health gates must pass before
> the next phase begins.

## Phase 1 — Infisical vault up (Change 1)

```bash
# 0. One-time per host
docker network create bunchloch-infra

# 1. Generate the .env.dev with the 5 required secrets
bun run bonneagar/scripts/seed-infisical-vault.sh --env-only
# This writes bonneagar/stacks/infisical/.env.dev (NEVER committed)

# 2. Deploy
cd bonneagar/stacks/infisical
docker compose -f compose.yaml -f sidecar.yaml up -d

# 3. Smoke
docker ps --filter "name=infisical" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
curl -sf http://localhost:8081/api/status | jq
# Expected: 3 containers, status === "ok"

# 4. Sign up + create dev-baile project + machine identity
#    UI: http://localhost:8081 — first user = admin
#    Capture: PROJECT_ID, CLIENT_ID, CLIENT_SECRET

# 5. Seed vault
cd /Users/cianmacandeisigh/dev/kings_college_galway
bun run bonneagar/scripts/seed-infisical-vault.sh \
  --project-id "$PROJECT_ID" \
  --client-id "$CLIENT_ID" \
  --client-secret "$CLIENT_SECRET"

# 6. Verify
infisical secrets list --project-id "$PROJECT_ID" --env=dev | wc -l
# Expected: ≥ 33 (number of seeded secrets across 7 paths)
```

## Phase 2 — Lakehouse data plane up (first half of Change 2)

```bash
cd bonneagar/stacks/lakehouse
docker compose -f compose.yaml -f sidecar.yaml up -d
docker logs lakehouse-locket 2>&1 | tail -3   # confirm "secrets synced"

# Health gates (ALL must be 200 before Phase 3)
curl -sf http://localhost:3900/health           # Garage
curl -sf http://localhost:8181/v1/config        # Lakekeeper
curl -sf http://localhost:8182/v1/info          # Lance-sidecar
curl -sf http://localhost:3018                  # Nimtable

psql postgresql://lakehouse-postgres:5432/postgres -c "\l"
# Expected: 12 DBs (the 6 ducklake_* + dagster_local + olake_state
# + nimtable + langfuse + mlflow + litellm)
```

## Phase 3 — Consumer stacks up (second half of Change 2)

```bash
for stack in mlflow litellm unstract; do
  cd "$HOME/dev/kings_college_galway/bonneagar/stacks/$stack"
  echo "=== bringing up $stack ==="
  case "$stack" in
    mlflow)   docker compose -f compose.yaml -f sidecar.yaml -f compose.dev.yaml up -d ;;
    litellm)  docker compose -f compose.yaml -f compose.dev.yaml -f sidecar.yaml up -d ;;
    unstract) docker compose -f compose.yaml -f sidecar.yaml up -d ;;
  esac
  sleep 8
  docker logs "${stack}-locket" 2>&1 | tail -1
  # Wait for "secrets synced"
done

# Health gates
curl -sf http://localhost:5001/version          # mlflow  → "3.12.0"
curl -sf http://localhost:4000/health/readiness # litellm
curl -sf http://localhost:8000/health           # unstract
```

## Phase 4 — Run the BIEP notebooks (Change 3, ibis-first)

```bash
# 0. Verify the ibis skill is loaded + the lakehouse is reachable
python -c "import ibis; ibis.duckdb.connect('md:oideachais')"  # cloud smoke
python -c "import ibis; ibis.duckdb.connect('ducklake:postgres:host=lakehouse-postgres port=5432 user=lakekeeper password=\${POSTGRES_PASSWORD} dbname=ducklake_oideachais')"  # local smoke

# 1. Run the 6 subject notebooks
bun run opencode/scripts/run-biep-notebooks.sh

# 2. Run the canonical lakehouse pipeline notebook
marimo run bonneagar/stacks/lakehouse/notebooks/lakehouse_pipeline.py
```

### Phase 4 expected output (each notebook)

```
[ok] ibis.duckdb connected (md:oideachais)
[ok] ibis.lancedb connected (rest://lakehouse-lance-namespace:8182)
[ok] found 6 tables: cianfhoghlaim.lc.mathematics.{hl,ol}_en, oideol.lc.mathematics.{hl,ol}_ga
[ok]   - hl_en: 0 rows (expected, pre-ingest)
[ok]   - ol_en: 0 rows
[ok]   - hl_ga: 0 rows
[ok]   - ol_ga: 0 rows
[ok] ibis expression graph compiled: 4 cells, 8 dependencies
[ok] notebook complete in 7.2s
```

## Rollback per phase

```bash
# Phase 1 rollback
cd bonneagar/stacks/infisical && docker compose -f compose.yaml down -v
docker network rm bunchloch-infra
# (irreversible: destroying the fresh vault + seeded secrets)

# Phase 2 rollback
cd bonneagar/stacks/lakehouse && docker compose -f compose.yaml down -v

# Phase 3 rollback (per stack)
cd bonneagar/stacks/<stack> && docker compose \
  -f compose.yaml -f sidecar.yaml -f compose.dev.yaml down
# NOTE: mlflow + litellm were already running pre-change;
# down-ing will return them to the pre-change dev state
```

## Diagnostic reference

| Symptom | Probable cause | Fix |
|---|---|---|
| Locket sidecar logs "no Infisical project id" | `INFISICAL_PROJECT_ID` env var missing in sidecar | re-apply runbook Phase 1 step 6; double-check `INFISICAL_PROJECT_ID` env in Locket command |
| Garages logs "no RPC secret" | `secrets.env` URI not in vault | re-run `seed-infisical-vault.sh`; check `infisical secrets list` for `lakehouse/rpc_secret` |
| `connection refused on 5432` (lakehouse-postgres) | db not yet healthy when init runs | re-run lakehouse `docker compose up -d`; postgres healthcheck must be green |
| Unstract 8000/health returns 503 | Traefik not ready | `docker logs unstract-reverse-proxy` — usually `certbot --register-unsafely-without-email --no-redirect --standalone -d unstract.cianfhoghlaim.ie`; ignore (we're local-only) |
| `mars 0: OAS not found` | mlflow v3 security middleware rejected allowed_hosts | add `--allowed-hosts="localhost,127.0.0.1,mlflow.cianfhoghlaim.ie"` to mlflow container |
| `ModuleNotFoundError: No module named 'ibis'` | ibis-framework not installed | `uv pip install 'ibis-framework[duckdb,lancedb]'` |
| `ibis.lancedb.connect("rest://…")` raises `UnsupportedURI` | the Lance REST sidecar may be < 0.9.0 | bump `lance-sidecar/requirements.txt` to `pylance>=8.0.0` + `lance-namespace-urllib3-client>=0.0.30` per Change 2 §1.6 |