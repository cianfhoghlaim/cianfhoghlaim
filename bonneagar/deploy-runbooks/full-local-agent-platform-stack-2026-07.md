# Full Local Agent Platform Stack — Deploy Runbook (2026-07-24)

## When to use

This runbook brings up the full Cianfhoghlaim local dev stack
(Infisical + Pangolin-via-fallback + OpenClaw + Hermes + LiteLLM +
Langfuse + Lakehouse + Komodo-via-iac) on `bunchloch` (MacBook M4) when:

- The OCI Infisical private resource is returning 502 Bad Gateway (the
  original blocker)
- You need openclaw + hermes + litellm + langfuse all running locally
- You want a permanent dev environment on the MacBook (not just a
  temporary fallback)

## Prerequisites

- `bunchloch` (MacBook M4) running OrbStack (or any Docker)
- ~25 GB free disk + ~8 GB RAM headroom
- `mise install` run (mise.toml pins Python 3.12, uv, bun, docker)
- `bun install` run (root-level package.json deps)
- The `dev-baile` Infisical workspace created (via the
  `2026-07-24-deploy-openclaw-hermes-bunchloch-local-infisical-fallback-v1`
  openspec change)
- The bons-iac machine identity created in that workspace
  (the universal-auth client_id + client_secret are in `~/.locket/infisical_secret`)

## The 7 phases (60-90 minutes total)

### Phase A — Foundations (20 min)

```bash
# A1. Verify lakehouse has the 12 databases + 7 buckets
docker exec lakehouse-postgres psql -U lakekeeper -d postgres -c '\l' | grep -E "(litellm|langfuse)"
docker exec lakehouse-garage /garage bucket list | grep -E "langfuse"

# A1.1: Create missing DBs (if not already done)
docker exec lakehouse-postgres createdb -U lakekeeper -O lakekeeper litellm
docker exec lakehouse-postgres createdb -U lakekeeper -O lakekeeper langfuse

# A2. Bulk-seed 35 secrets into local Infisical via the user's JWT
INFISICAL_USER_JWT="<paste from local Infisical UI>"
bash bonneagar/scripts/seed-bunchloch-litellm-langfuse-fallback.sh
# Expect: "Result: 35 ok, 0 failed"

# A3. Bons-iac credential is already in ~/.locket/infisical_secret (mode 0600)
ls -la ~/.locket/infisical_secret
```

### Phase B — Bring up LiteLLM (30 min)

```bash
# B1. Symlink the stack dir (this is the pattern that worked for openclaw + hermes)
mkdir -p ~/.komodo-stacks/litellm
for f in ~/dev/kings_college_galway/bonneagar/stacks/litellm/* ~/dev/kings_college_galway/bonneagar/stacks/litellm/.[!.]*; do
  [ -e "$f" ] && ln -sf "$f" ~/.komodo-stacks/litellm/
done

# B2. Create the local .env (REAL lakehouse creds + local Infisical fallback)
cat > ~/.komodo-stacks/litellm/.env <<'EOF'
INFISICAL_URL=http://host.docker.internal:8081
INFISICAL_PROJECT_ID=d900f50a-acbf-446b-b4f6-e439710253e4
INFISICAL_ENV=dev
INFISICAL_CLIENT_ID=7177c4ef-2688-4afa-982b-cc749d3ea3ad
INFISICAL_SECRET_FILE=/Users/cianmacandeisigh/.locket/infisical_secret
LOCKET_MODE=watch
POSTGRES_USER=lakekeeper
POSTGRES_PASSWORD=805c7a4565f7ddf9bea11b6ffbd9a11f536cfe3beaaee7f9
CLICKHOUSE_USER=oideachais
CLICKHOUSE_PASSWORD=062974092ef788bf2e402790481386f23503758dd3271b06
GARAGE_ACCESS_KEY_ID=GK3b427f19ad3fd54647e9a1ac
GARAGE_SECRET_ACCESS_KEY=6fd34220da97ec87dcc8707e0b930f6d7a431df9742ccf556cc801c87e245435
REDIS_PASSWORD=18418e0af8227b72b6fcbb39fa2da50115f156c07dfc7870
LITELLM_MASTER_KEY=sk-litellm-master-bb06b71044e9c018b08e72b4d4c8da42ddfaaef6
LITELLM_SALT_KEY=0b4c81e2bf5dd86d
LITELLM_LOG=INFO
LITELLM_DATABASE_URL=postgresql://lakekeeper:805c7a4565f7ddf9bea11b6ffbd9a11f536cfe3beaaee7f9@lakehouse-postgres:5432/litellm
MLFLOW_TRACKING_URI=http://mlflow:5000
LANCEDB_API_KEY=
EOF

# B3. Force cianfhoghlaim as external (avoid collision with openclaw's external)
cat > ~/.komodo-stacks/litellm/compose.local.yaml <<'EOF'
networks:
  cianfhoghlaim:
    external: true
    name: cianfhoghlaim
  lakehouse:
    external: true
    name: lakehouse_lakehouse
EOF

# B4. Bring it up
cd ~/.komodo-stacks/litellm
set -a; . ./.env.local; . ./.env; set +a
docker compose -f compose.yaml -f sidecar.yaml -f compose.local.yaml up -d

# B5. Wait + verify
sleep 60
curl -sS -o /dev/null -w "LiteLLM /health/liveliness: HTTP %{http_code}\n" http://localhost:4000/health/liveliness
# Expect: HTTP 200, "I'm alive!"
```

### Phase C — Bring up Langfuse (30 min)

```bash
# C1. Create the langfuse stack dir + .env + compose.local.yaml
mkdir -p ~/.komodo-stacks/langfuse
for f in ~/dev/kings_college_galway/bonneagar/stacks/langfuse/* ~/dev/kings_college_galway/bonneagar/stacks/langfuse/.[!.]*; do
  [ -e "$f" ] && ln -sf "$f" ~/.komodo-stacks/langfuse/
done

# CRITICAL: Use the ACTUAL Redis password (from --requirepass in the container)
# NOT the devpassword in .env.dev
cat > ~/.komodo-stacks/langfuse/.env <<'EOF'
INFISICAL_URL=http://host.docker.internal:8081
INFISICAL_PROJECT_ID=d900f50a-acbf-446b-b4f6-e439710253e4
INFISICAL_ENV=dev
INFISICAL_CLIENT_ID=7177c4ef-2688-4afa-982b-cc749d3ea3ad
INFISICAL_SECRET_FILE=/Users/cianmacandeisigh/.locket/infisical_secret
LOCKET_MODE=watch

# Lakehouse Postgres (db=langfuse)
DATABASE_URL=postgresql://lakekeeper:805c7a4565f7ddf9bea11b6ffbd9a11f536cfe3beaaee7f9@lakehouse-postgres:5432/langfuse
POSTGRES_USER=lakekeeper
POSTGRES_PASSWORD=805c7a4565f7ddf9bea11b6ffbd9a11f536cfe3beaaee7f9

# Lakehouse Redis (CORRECT port: internal 6379, NOT host-mapped 6381)
REDIS_HOST=lakehouse-redis
REDIS_PORT=6379
REDIS_AUTH=c9f2e6ea1204a94234d7fba213dc7a7b
REDIS_PASSWORD=c9f2e6ea1204a94234d7fba213dc7a7b

# Lakehouse ClickHouse (CORRECT user: "clickhouse", NOT "oideachais")
CLICKHOUSE_MIGRATION_URL=clickhouse://clickhouse:ae57586ac13250297988258bf39a0365@lakehouse-clickhouse:9000
CLICKHOUSE_URL=http://clickhouse:ae57586ac13250297988258bf39a0365@lakehouse-clickhouse:8123
CLICKHOUSE_USER=clickhouse
CLICKHOUSE_PASSWORD=ae57586ac13250297988258bf39a0365
CLICKHOUSE_CLUSTER_ENABLED=false

# Lakehouse Garage
AWS_ACCESS_KEY_ID=GK3b427f19ad3fd54647e9a1ac
AWS_SECRET_ACCESS_KEY=6fd34220da97ec87dcc8707e0b930f6d7a431df9742ccf556cc801c87e245435
GARAGE_ACCESS_KEY_ID=GK3b427f19ad3fd54647e9a1ac
GARAGE_SECRET_ACCESS_KEY=6fd34220da97ec87dcc8707e0b930f6d7a431df9742ccf556cc801c87e245435
LANGFUSE_S3_EVENT_UPLOAD_BUCKET=langfuse-events
LANGFUSE_S3_EVENT_UPLOAD_REGION=garage
LANGFUSE_S3_EVENT_UPLOAD_ACCESS_KEY_ID=GK3b427f19ad3fd54647e9a1ac
LANGFUSE_S3_EVENT_UPLOAD_SECRET_ACCESS_KEY=6fd34220da97ec87dcc8707e0b930f6d7a431df9742ccf556cc801c87e245435
LANGFUSE_S3_EVENT_UPLOAD_ENDPOINT=http://lakehouse-garage:3900
LANGFUSE_S3_EVENT_UPLOAD_FORCE_PATH_STYLE=true
LANGFUSE_S3_EVENT_UPLOAD_PREFIX=events/
LANGFUSE_S3_MEDIA_UPLOAD_BUCKET=langfuse-media
LANGFUSE_S3_MEDIA_UPLOAD_REGION=garage
LANGFUSE_S3_MEDIA_UPLOAD_ACCESS_KEY_ID=GK3b427f19ad3fd54647e9a1ac
LANGFUSE_S3_MEDIA_UPLOAD_SECRET_ACCESS_KEY=6fd34220da97ec87dcc8707e0b930f6d7a431df9742ccf556cc801c87e245435
LANGFUSE_S3_MEDIA_UPLOAD_ENDPOINT=http://lakehouse-garage:3900
LANGFUSE_S3_MEDIA_UPLOAD_FORCE_PATH_STYLE=true
LANGFUSE_S3_MEDIA_UPLOAD_PREFIX=media/
LANGFUSE_S3_BATCH_EXPORT_ENABLED=false
LANGFUSE_S3_BATCH_EXPORT_BUCKET=langfuse-exports
LANGFUSE_S3_BATCH_EXPORT_PREFIX=exports/
LANGFUSE_S3_BATCH_EXPORT_REGION=garage
LANGFUSE_S3_BATCH_EXPORT_ENDPOINT=http://lakehouse-garage:3900
LANGFUSE_S3_BATCH_EXPORT_EXTERNAL_ENDPOINT=https://langfuse.cianfhoghlaim.ie
LANGFUSE_S3_BATCH_EXPORT_ACCESS_KEY_ID=GK3b427f19ad3fd54647e9a1ac
LANGFUSE_S3_BATCH_EXPORT_SECRET_ACCESS_KEY=6fd34220da97ec87dcc8707e0b930f6d7a431df9742ccf556cc801c87e245435
LANGFUSE_S3_BATCH_EXPORT_FORCE_PATH_STYLE=true

SALT=0b4c81e2bf5dd86d
ENCRYPTION_KEY=faa8a3c1b5e6d7f8c2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3d4e5
TELEMETRY_ENABLED=true
LANGFUSE_ENABLE_EXPERIMENTAL_FEATURES=true

NEXTAUTH_SECRET=dev-nextauth-secret-not-for-prod
LANGFUSE_INIT_PROJECT_NAME=default
LANGFUSE_INIT_USER_EMAIL=admin@local.dev
LANGFUSE_INIT_USER_PASSWORD=devpassword
LANGFUSE_INIT_PROJECT_ID=default
LANGFUSE_INIT_ORG_ID=default
LANGFUSE_INIT_PROJECT_SECRET_KEY=sk-lf-default-dev-secret
NEXT_PUBLIC_LANGFUSE_HOST=http://localhost:3000
EOF

cat > ~/.komodo-stacks/langfuse/compose.local.yaml <<'EOF'
networks:
  langfuse:
    driver: bridge
  lakehouse:
    external: true
    name: lakehouse_lakehouse
EOF

# C2. Bring it up
cd ~/.komodo-stacks/langfuse
set -a; . ./.env; set +a
docker compose -f compose.yaml -f sidecar.yaml -f compose.local.yaml up -d

# C3. Wait + verify
sleep 60
curl -sS -o /dev/null -w "Langfuse /api/public/health: HTTP %{http_code}\n" http://localhost:3001/api/public/health
# Expect: HTTP 200, {"status":"OK","version":"3.224.1"}
```

### Phase D — Fix openclaw (already done via 2026-07-24-deploy-openclaw-hermes-...)

The openclaw sidecar has been updated to:
- Use `user: 1000:1000` (Dockerfile default, NOT 65532)
- Add a chmod init container that fixes the locket file permissions
- Pass `--allow-unconfigured` to the openclaw binary
- Use a shell wrapper command instead of `env_file: /run/secrets/...`

### Phase E — Fix hermes (work in progress)

Hermes is in a crash loop due to s6-overlay + locket passthrough issues.
The fix is one of:
1. Upgrade locket to a version that resolves secrets correctly
2. Apply a workaround that strips `{{ infisical://... }}` placeholders
   from the locket output before sh sources the file

For now, hermes is documented as a known issue. Skip this phase.

### Phase F — Verification (5 min)

```bash
# F1. Container status
docker ps --filter "name=openclaw" --filter "name=hermes" --filter "name=litellm" \
              --filter "name=langfuse" --filter "name=infisical" --filter "name=lakehouse" \
              --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

# F2. API endpoints
curl -sS -o /dev/null -w "LiteLLM:   HTTP %{http_code}\n" http://localhost:4000/health/liveliness
curl -sS -o /dev/null -w "Langfuse:  HTTP %{http_code}\n" http://localhost:3001/api/public/health
curl -sS -o /dev/null -w "OpenClaw:  HTTP %{http_code} (WS port; 52 = WS only)\n" http://localhost:18789/
curl -sS -o /dev/null -w "Infisical: HTTP %{http_code}\n" http://127.0.0.1:8081/api/status

# F3. Locket healthcheck status
for s in openclaw-locket hermes-locket litellm-locket langfuse-locket; do
  echo "  $s: $(docker inspect $s --format '{{.State.Health.Status}}' 2>&1)"
done
```

### Phase G — OpenSpec change (already written)

- `openspec/changes/2026-07-24-full-local-agent-platform-stack-up-v1/`
  - `proposal.md` (this change's background, what, why)
  - `tasks.md` (the 7 phases above)
  - `specs/infrastructure-stacks/spec.md` (2 ADDED Requirements:
    locket bug + hermes s6-overlay)

## Known issues (out of scope)

1. **Locket v0.17.3 + Infisical v0.161+ API mismatch** — all 4 lockets
   silently fall back to passthrough mode. Track under
   `2026-07-XX-locket-v0-18-or-bons-locket-fork-v1`.
2. **Hermes s6-overlay + tmpfs permissions** — hermes container is in
   crash loop. Track under `2026-07-XX-hermes-s6-overlay-init-sidecar-v1`.
3. **Cross-stack DNS** — openclaw + hermes can't reach langfuse because
   they're on different bridge networks. Track under
   `2026-07-XX-unify-agent-platform-network-bridge-v1`.

## Related

- Change: `2026-07-24-deploy-openclaw-hermes-bunchloch-local-infisical-fallback-v1`
  (the prerequisite — the local Infisical vault itself)
- Change: `2026-07-24-iac-sync-sites-pangolin-private-infisical-repair-v1`
  (the OCI repair path; for when you want to switch back to OCI)