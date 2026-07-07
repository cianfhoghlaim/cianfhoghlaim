# Tasks: 2026-07-06-upgrade-4-stacks-with-infisical

## 0. Source URLs (for traceability)

All versions verified via Firecrawl against the canonical docs on
2026-07-06:

- Lakehouse: <https://docs.lakekeeper.io/> +
  <https://github.com/lakekeeper/lakekeeper/releases> +
  <https://hub.docker.com/r/dxflrs/garage> +
  <https://github.com/ClickHouse/ClickHouse/releases> +
  <https://github.com/nimtable/nimtable> +
  <https://github.com/datazip-inc/olake>
- LiteLLM: <https://docs.litellm.ai/docs/proxy/deploy> +
  <https://docs.litellm.ai/docs/proxy/prod> +
  <https://github.com/BerriAI/litellm/releases> (v1.91.0 on 2026-07-06)
- MLflow: <https://mlflow.org/docs/latest/> +
  <https://github.com/mlflow/mlflow/releases> (v3.12.0 on 2026-07-06)
- Unstract: <https://github.com/Zipstack/unstract> (v0.177.7 on 2026-07-06)
  + <https://docs.unstract.com/unstract/editions/open_source_edition/>

## 1. Bring up the data plane FIRST (lakehouse)

- [ ] 1.1 Pull all 11 lakehouse images locally (`docker compose pull`)
- [ ] 1.2 `cd bonneagar/stacks/lakehouse`
- [ ] 1.3 Verify `garage.toml` is v2 schema (rewrite using the official
      Garage v1→v2 migration helper if needed)
- [ ] 1.4 `docker compose -f compose.yaml -f sidecar.yaml up -d`
- [ ] 1.5 `docker logs lakehouse-locket` — confirm `secrets synced`
      (means the Locket sidecar resolved every `infisical://dev-baile/lakehouse/*`
      URI in `secrets.env`)
- [ ] 1.6 Healthcheck Gate A: `curl -sf http://localhost:3900/health` → 200
      (Garage S3 API)
- [ ] 1.7 Healthcheck Gate B: `curl -sf http://localhost:8181/v1/config` → 200
      (Lakekeeper REST catalog)
- [ ] 1.8 Healthcheck Gate C: `curl -sf http://localhost:8182/v1/info` → 200
      (Lance REST namespace sidecar)
- [ ] 1.9 Healthcheck Gate D: `curl -sf http://localhost:3018` → 200
      (Nimtable UI)
- [ ] 1.10 Healthcheck Gate E: `psql postgresql://lakehouse-postgres:5432 -c "\l"`
      — confirm 11 databases present
      (ducklake_{oideachais,crypteolas,aleyum,croilar,tuath,meaisinfhoghlaim},
      dagster_local, olake_state, nimtable, langfuse, mlflow, litellm)

## 2. Upgrade mlflow (already running — graceful restart)

- [ ] 2.1 `cd bonneagar/stacks/mlflow`
- [ ] 2.2 Rewrite `compose.yaml` per the per-stack upgrade list (image pin
      + new envs + new arg `--allowed-hosts=…`)
- [ ] 2.3 `docker compose -f compose.yaml -f sidecar.yaml -f compose.dev.yaml up -d`
      (overrides the existing dev container)
- [ ] 2.4 `docker logs mlflow-locket-dev` — confirm secrets synced
- [ ] 2.5 Healthcheck Gate F: `curl -sf http://localhost:5001/api/2.0/mlflow/experiments/list` → 200
      + returns valid JSON
- [ ] 2.6 New: `curl -sf http://localhost:5001/version` — confirm returns
      `{"version": "3.12.0"}`

## 3. Upgrade litellm (already running — graceful restart)

- [ ] 3.1 `cd bonneagar/stacks/litellm`
- [ ] 3.2 Rewrite `compose.yaml` per the per-stack upgrade list
- [ ] 3.3 `docker compose -f compose.yaml -f compose.dev.yaml -f sidecar.yaml up -d`
- [ ] 3.4 `docker logs litellm-locket-dev` — confirm secrets synced
- [ ] 3.5 Healthcheck Gate G: `curl -sf http://localhost:4000/health/liveliness` → 200
- [ ] 3.6 Healthcheck Gate H: `curl -sf http://localhost:4000/health/readiness` → 200
      (new endpoint per upstream docs)
- [ ] 3.7 `docker exec litellm psql postgresql://lakehouse-postgres:5432/litellm -c "\dt"`
      — confirm Prisma created the schema (LITELLM_MODE=PRODUCTION +
      USE_PRISMA_MIGRATE=True)

## 4. Vendor unstract (15 services from scratch)

- [ ] 4.1 `cd /tmp && git clone --depth=1 --branch=v0.177.7 https://github.com/Zipstack/unstract.git unstract-src`
- [ ] 4.2 `cp /tmp/unstract-src/docker/docker-compose.yaml bonneagar/stacks/unstract/compose.yaml`
- [ ] 4.3 `cp /tmp/unstract-src/docker/sample.env bonneagar/stacks/unstract/.env.example`
- [ ] 4.4 Rewrite the image references in the vendored compose.yaml to be
      KCG-canonical: `unstract-backend`, `unstract-db`, etc. (override
      the upstream's `unstract-backend-1` defaults — per user decision)
- [ ] 4.5 Change `postgres:16` → `pgvector/pgvector:pg15` in the db service
- [ ] 4.6 Strip the network declarations; replace with
      `networks: { stack: { external: true, name: bunchloch-infra } }`
- [ ] 4.7 Add a `pangolin.yaml` (the original stack did not have one)
- [ ] 4.8 Build the new `secrets.env` covering ALL the env vars the
      vendored compose references (≥ 20 keys)
- [ ] 4.9 Add the Locket sidecar in `sidecar.yaml` (the upstream does
      not ship one)
- [ ] 4.10 Delete `/tmp/unstract-src` after vendoring
- [ ] 4.11 `docker compose -f compose.yaml -f sidecar.yaml up -d`
- [ ] 4.12 Healthcheck Gate I: `curl -sf http://localhost:8000/health` → 200
- [ ] 4.13 Login UI at `http://localhost:8000` with `unstract`/`unstract`
      (OSS default credentials per docs.unstract.com)
- [ ] 4.14 Re-seed the dev-baile vault with the new Unstract secret paths

## 5. Cross-stack verification

- [ ] 5.1 `docker compose ls -a` — confirm 5 stacks running
      (infisical + lakehouse + mlflow + litellm + unstract) [NO paddleocr]
- [ ] 5.2 `bun run validate-stacks` — confirm zero
      `console.error(\`unpinned image…\`)` warnings for any of these 5
- [ ] 5.3 `openspec validate 2026-07-06-upgrade-4-stacks-with-infisical --strict`
- [ ] 5.4 `mise run lint:skills` — confirm no regression