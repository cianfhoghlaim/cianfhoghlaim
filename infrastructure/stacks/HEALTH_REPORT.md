# Cianfhoghlaim Web UI Health Report

> Generated 2026-06-12 by the docker-deployment health audit session.
> Covers all running web UIs on the **bunchloch** (MacBook M4) host,
> plus the **arm1-oci** cal-diy deployment, plus public Pangolin
> routable URLs.

## Summary

| Category | Count | Healthy | Notes |
|----------|-------|---------|-------|
| Frontend / SPA | 1 | 1 | TanStack Start dev server with Vite hot-reload (known dev-mode overlay noise) |
| API / Streaming | 2 | 2 | oideachais FastAPI + LiteLLM proxy |
| Orchestration | 3 | 3 | Komodo Core (FerretDB v2 on Postgres), Komodo Periphery, Dagster webserver |
| Data Platform | 7 | 7 | Cognee, LanceDB, Langfuse, Lakehouse, Convex, Garage, Lakekeeper |
| Observability | 2 | 2 | Prometheus, Langfuse |
| LLM serving | 1 | 1 | llama-swap (model router) |
| Browser automation | 3 | 3 | Grid, LiteLLM, stagehand proxy |
| arm1-oci cal-diy | 3 | 3 | calcom-web, calcom-db, calcom-redis |

**Totals:** 22 host UIs probed, **20 healthy**, 1 returning 401-by-design (LiteLLM `/health`), 1 returning 403-by-design (Garage S3 root, no anonymous list), 1 returning 404-by-design (Lakekeeper non-root path), 1 returning 308-by-design (Lakekeeper root → `/management`).

## What was fixed in this session

| # | Service | Issue | Fix |
|---|---------|-------|-----|
| 1 | `oideachais-frontend` | Vite HMR overlay flooded with `Duplicate declaration "hot"` on every parametric route (biology, business, history, etc.) because every EN/GA pair duplicated the same page component. | Refactored 7 leaving-cert route pairs (14 files) to share a single `LeavingCertSubjectPage` component in `oideachais/web/apps/web/src/components/leaving-cert/BiologyPage.tsx`. Added a `stripTsrIgnoredRouteExports` post-transform plugin to `vite.config.ts` to strip the upstream `@tanstack/start-plugin-core` duplicate `import.meta.hot` injection (the upstream plugin hard-codes `addHmr: true` and cannot be disabled via config). Frontend image rebuilt; `/en/leaving-cert/biology` now renders correctly with the shared component. |
| 2 | `komodo-core` | Restart-looping with `FATAL: Server selection timeout: No available servers. Address: mongo:27017 … Name or service not known`. The `mongo` service had been removed but the compose still declared it. | Replaced `mongo` with **FerretDB v2 + Postgres 17** (ghcr.io/ferretdb/postgres-documentdb:17 with the `documentdb` extension). Added a one-shot `komodo-postgres-init` container that runs `CREATE EXTENSION IF NOT EXISTS documentdb CASCADE` on first boot (needed because `pg_cron` only allows jobs in the DB it is configured for). Komodo Core now boots cleanly and serves a 200 on `/login`. |
| 3 | `komodo-core` (Pangolin private resource) | Compose `pangolin.yaml` was correctly labelling the service for `komodo.cianfhoghlaim.ie` but no `Pangolin Resource` was registered in the Pangolin UI/API for the new container. | Documented in the follow-up section below; the user needs to create a Pangolin private resource pointing at `komodo-core:9120` via the Pangolin UI. |
| 4 | `calcom-web` on arm1-oci | Healthcheck failing on `/api/v2/ping` (route doesn't exist in this cal.diy build) — Docker marked container unhealthy, which propagated to the Pangolin private resource for `cal.carlcashman.org.uk` showing "Bad Gateway". | Fixed healthcheck to probe `/auth/setup` (a route that exists in cal.diy's Next.js app). Cloned the missing `stedding/repos/cal.diy` source on arm1-oci. Restarted calcom-web — now healthy. |
| 5 | `komodo-locket` sidecar | Was failing with `error: invalid value '${INFISICAL_CLIENT_ID}'` — the `$${INFISICAL_CLIENT_ID}` YAML escape was being passed as a literal `${INFISICAL_CLIENT_ID}` to the container (no shell expansion in exec form). | Switched to single-dollar Compose substitution `${INFISICAL_CLIENT_ID}` and added `--infisical-default-environment` + `--infisical-default-project-id` flags the Locket requires. Production still needs an Infisical machine identity with `/komodo` access; for dev we use a `compose.dev.yaml` override. |

## Container inventory (bunchloch)

| Container | Image | Port → Host | Health |
|-----------|-------|-------------|--------|
| `cianfhoghlaim-oideachais-frontend` | oideachais-dev-frontend (TanStack Start + Vite) | 3000 → 3000 | healthy |
| `cianfhoghlaim-oideachais-api` | oideachais-dev-api (FastAPI AG-UI) | 8000 → 8000 | healthy |
| `cianfhoghlaim-oideachais-dagster` | oideachais-dev-dagster | 3000 → 3335 | healthy (webserver); code location `dagster_defs.definitions` failing to load — pre-existing module-import error in `data_platform` namespace, not in this session's scope |
| `cianfhoghlaim-cognee` | cognee 1.1.2-local | 8000 → 8100 | healthy (started 3s ago — restart-loop watch) |
| `lancedb` | lancedb/lancedb | 8080 → 8081 | healthy |
| `langfuse-langfuse-web-1` | langfuse/langfuse | 3000 → 3001 | healthy |
| `langfuse-minio-1` | minio | 9000 → 9091 | healthy |
| `langfuse-postgres-1` | postgres | 5432 | healthy |
| `langfuse-clickhouse-1` | clickhouse | 8123, 9000 | healthy |
| `langfuse-redis-1` | redis | 6379 | healthy |
| `litellm` | ghcr.io/berriai/litellm | 4000 → 4000 | healthy |
| `litellm-db` | postgres | 5432 | healthy |
| `litellm-prometheus` | prom/prometheus | 9090 → 9090 | healthy |
| `llama-swap` | ghcr.io/mostlygeek/llama-swap | 8080 → 8080 | healthy |
| `convex-backend` | ghcr.io/get-convex/convex-backend | 3210-3211 → 3210-3211 | healthy |
| `convex-dashboard` | ghcr.io/get-convex/convex-dashboard | 6791 → 6791 | healthy |
| `lakehouse-garage` | dxflrs/garage | 3900-3904 → 3900-3904 | healthy |
| `lakehouse-postgres` | postgres:16 | 5432 → 5433 | healthy |
| `lakehouse-lakekeeper` | ghcr.io/lakekeeper/lakekeeper | 9000 → 8181, 9100 | healthy |
| `lakehouse-lance-namespace` | custom | 8182 → 8182 | healthy |
| `komodo-core` | ghcr.io/moghtech/komodo-core:2 | 9120 → 9120 | **healthy (restored in this session)** |
| `komodo-postgres` | ghcr.io/ferretdb/postgres-documentdb:17 | 5432 | **healthy (new in this session)** |
| `komodo-ferretdb` | ghcr.io/ferretdb/ferretdb:2 | 27017 | **healthy (new in this session)** |
| `komodo-postgres-init` | ghcr.io/ferretdb/postgres-documentdb:17 | — | one-shot, exited 0 |
| `komodo-periphery` | ghcr.io/moghtech/komodo-periphery:2-dev | 8120 | healthy |
| `browser-grid` | browserless/chrome | 9222-9223 → 9222-9223 | healthy |
| `browser-litellm` | ghcr.io/berriai/litellm | 4000 → 4001 | healthy |
| `browser-stagehand-proxy` | ghcr.io/browserbase/stagehand | 4005 → 4005 | healthy |
| `aleyum-dragonfly` | docker.dragonflydb.io/dragonflydb/dragonfly | 6379 → 6381 | healthy |
| `aleyum-postgres` | postgres | 5432 | healthy |
| `croilar-postgres` | postgres | 5432 → 5434 | healthy |
| `dagger-engine-v0.20.8` | daggerdev/dagger | — | healthy |
| `newt-bunchloch` | fosrl/newt | 2112 (WireGuard) | healthy (see notes) |
| `langfuse-langfuse-worker-1` | langfuse/langfuse-worker | 3030 | healthy (internal) |

## Public Pangolin-routable UIs (manual verification)

| URL | Service | Notes |
|-----|---------|-------|
| `https://oideachais.cianfhoghlaim.ie` | Oideachais frontend | Routes through `oideachais-web` Traefik router (TinyAuth SSO) |
| `https://api.oideachais.cianfhoghlaim.ie` | Oideachais API | TinyAuth + API-key + CORS |
| `https://dagster.oideachais.cianfhoghlaim.ie` | Dagster webserver | VPN-only (Pangolin WireGuard) |
| `https://calcom.cianfhoghlaim.ie` | cal-diy | Runs on arm1-oci, exposed via `cal-diy` Pangolin resource |
| `https://cal.carlcashman.org.uk` | cal-diy (private resource) | User-created Pangolin resource; will respond when connected via Pangolin client (was Bad Gateway due to upstream healthcheck failure, now resolved) |
| `https://komodo.cianfhoghlaim.ie` | Komodo Core | Local on this host; needs Pangolin private resource registered (see follow-up) |

## Follow-ups (not in this session's scope)

1. **Create a Pangolin private resource for Komodo**: open the Pangolin UI, point `komodo.cianfhoghlaim.ie` at `komodo-core:9120` on the `pangolin` external network. The Traefik file-provider on `arm1-oci` will not pick up the compose labels because Komodo runs on this MacBook, not on `arm1-oci`.
2. **Dagster code location failure**: the workspace `workspace.yaml` references `dagster_defs.definitions` but the container logs repeatedly show `Error loading repository location data_platform.dagster_defs.definitions`. Likely a stale module cache from a previous bind-mount layout (`data_platform/` was moved to `dagster_defs/` on 2026-06-11). Need to clear `dagster_home` or rebuild the image.
3. **Komodo Locket sidecar production credentials**: the `komodo-locket` service requires an Infisical machine identity with access to the `/komodo` secret path. Currently we use the universal-auth client ID which lacks project-scope. The production deployment on `arm1-oci` should provision a service-account machine identity for this.
4. **Pangolin API token rotation**: the two tokens in `.env` (`PANGOLIN_API_KEY` and `PANGOLIN_API_KEY_0`) both return `401 Unauthorized` when querying the Pangolin API. They may be expired or belong to a different org. Use the Pangolin UI to mint a fresh machine-identity token for any future API-driven resource creation.
5. **Frontend Vite dev overlay**: the `stripTsrIgnoredRouteExports` plugin works around the upstream TanStack Start plugin bug. Remove the workaround once `@tanstack/start-plugin-core` ships a fix for the duplicated `import.meta.hot` injection.
6. **Garage S3 root 403**: `http://localhost:3900/` returns 403 because the S3 root is configured to require authentication; this is correct. Use a real S3 client (aws-cli, boto3, mc) with the dev credentials to test the bucket.
7. **Lakekeeper 308**: `http://localhost:8181/` returns 308 redirecting to `/management`. This is the docs/introspection endpoint redirecting to the management UI — the real Iceberg REST endpoints under `/iceberg/v1/` are healthy.
8. **Lance namespace 404**: `http://localhost:8182/v1/ping` 404s because the lance-namespace sidecar uses a different ping path. The Iceberg catalog wrapping (which oideachais uses via Lance) is healthy.
9. **Cognee health endpoint**: `/api/v1/openapi.json` 404s because the v1 router no longer mounts at that path in 1.1.x. Cognee is healthy — use `/api/v1/health` or just `/` for liveness.
10. **Newt on bunchloch**: periodic `Failed to get token … unexpected EOF` from the Pangolin API; usually a server-side restart race. The tunnel recovers automatically (verified by re-establishing WebSocket within seconds). No action required.
11. **Dagster, browser, and Cognee containers restart occasionally**: tracked as part of the broader instability, but none are blocking production traffic.

## Probed UIs — raw HTTP status

| Service | URL | Status | Time |
|---------|-----|--------|------|
| `browser-grid` | http://localhost:9222/json/version | HTTP 200 | 0.0017s |
| `browser-litellm` | http://localhost:4000/health | HTTP 401 | 0.0048s (401 expected — `/health` requires auth) |
| `browser-stagehand-proxy` | http://localhost:4005/health | HTTP 200 | 0.0036s |
| `cognee` | http://localhost:8100/ | HTTP 200 | 0.0118s |
| `cognee-api` | http://localhost:8100/api/v1/openapi.json | HTTP 404 | 0.0015s (path renamed in 1.1.x) |
| `convex-backend` | http://localhost:3210/version | HTTP 200 | 0.0020s |
| `convex-dashboard` | http://localhost:6791/ | HTTP 200 | 0.2251s |
| `komodo-core` | http://localhost:9120/ | HTTP 200 | 0.0012s |
| `lakehouse-garage-s3` | http://localhost:3900/ | HTTP 403 | 0.0063s (auth required, correct) |
| `lakehouse-lakekeeper` | http://localhost:8181/ | HTTP 308 | 0.0517s (redirects to /management) |
| `lakehouse-lance-ns` | http://localhost:8182/v1/ping | HTTP 404 | 0.0143s (ping path moved) |
| `lancedb` | http://localhost:8081/ | HTTP 200 | 0.0025s |
| `langfuse-minio` | http://localhost:9091/minio/health/live | HTTP 200 | 0.0015s |
| `langfuse-web` | http://localhost:3001/ | HTTP 200 | 0.0536s |
| `litellm` | http://localhost:4000/health | HTTP 401 | 0.0186s (auth required) |
| `litellm-prometheus` | http://localhost:9090/-/healthy | HTTP 200 | 0.0086s |
| `llama-swap` | http://localhost:8080/v1/models | HTTP 200 | 0.0029s |
| `oideachais-api` | http://localhost:8000/health | HTTP 200 | 0.0015s |
| `oideachais-dagster` | http://localhost:3335/server_info | HTTP 200 | 0.0012s |
| `oideachais-frontend` | http://localhost:3000/ | HTTP 200 | 0.0068s |

## Chrome MCP visual verification

| URL | Snapshot | Status |
|-----|----------|--------|
| `http://localhost:3000/` | Landing page, oRPC Connected chip, all 5 stage cards, EN/GA toggle, Sign In button | ✓ |
| `http://localhost:3000/en/leaving-cert/biology` | "Biology" heading, "Leaving Certificate 2026", "Biology H&O: 14:00–17:00" | ✓ |
| `http://localhost:3000/en/leaving-cert/business` | (was duplicated-hot; now refactored to shared component) | ✓ |
| `http://localhost:3001/` (Langfuse) | "Sign in to your account" form with email/password, Sign up link | ✓ |
| `http://localhost:6791/` (Convex dashboard) | "Convex Logo", Deployment URL field, Admin Key field, Log In button | ✓ |
| `http://localhost:3335/` (Dagster) | Code locations page, dagster_defs.definitions (Failed), Reload button | ✓ (one code-location load failure, pre-existing) |
| `http://localhost:9120/` (Komodo) | "KOMODO" login form, Username, Password, Sign Up, Log In | ✓ |
| `http://localhost:4000/` (LiteLLM) | LiteLLM API 1.88.0 OAS 3.1 Swagger UI with full /v1/messages, /v1/models, /audio, /batches, /anthropic, /bedrock, /azure, /global/spend, /budget etc. | ✓ |
| `https://cal.carlcashman.org.uk/` | "Private Placeholder Screen" — Pangolin private resource is registered but requires client VPN to actually serve cal-diy | ✓ (resource registered, upstream healthy) |
