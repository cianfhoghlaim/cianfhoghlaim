# Tasks: 2026-07-24-full-local-agent-platform-stack-up-v1

## 1. Verify lakehouse readiness (foundations)

- [x] 1.1 Confirm 12 databases + 7 buckets exist in lakehouse
- [x] 1.2 Create missing DBs: `litellm`, `langfuse` in `lakehouse-postgres`
- [x] 1.3 Verify 3 langfuse buckets exist in `lakehouse-garage`
      (`langfuse-events`, `langfuse-media`, `langfuse-exports`)

## 2. Populate 35 secrets in local Infisical

- [x] 2.1 Authenticate to local Infisical as the bons-iac machine identity
      (CLIENT_ID=`7177c4ef-2688-4afa-982b-cc749d3ea3ad`)
- [x] 2.2 Create 12 new folders in `dev-baile/dev/{litellm,langfuse,mlflow,
      lakehouse,deepseek,gemini,anthropic,openai,zai,opencode-go,
      huggingface,lancedb}` via `/api/v2/folders`
- [x] 2.3 Write 35 secrets via Python+curl (`POST /api/v3/secrets/raw/<KEY>`):
      - 7 litellm (master_key, salt_key, database_url, postgres_*3, litellm_database_url)
      - 5 langfuse (salt, encryption_key, public_key, secret_key, host)
      - 3 mlflow (postgres_user, postgres_password, tracking_uri)
      - 9 lakehouse (REAL values copied from running lakehouse containers)
      - 11 LLM provider placeholders (deepseek, gemini, anthropic, openai, zai, opencode-go × 4, huggingface, lancedb)
- [x] 2.4 Verify with direct reads: 35 ok, 0 failed

## 3. Bons-iac machine identity (canonical)

- [x] 3.1 `~/.locket/infisical_secret` (mode 0600) contains the bons-iac
      client_secret (raw hex, 64 bytes)
- [x] 3.2 Verified the bons-iac identity can read secrets from
      `dev-baile/dev/openclaw/gateway_token` (200 OK)

## 4. Bring up LiteLLM (30 min)

- [x] 4.1 Symlink `~/.komodo-stacks/litellm/` to source files (including
      hidden `.env.dev`, `.env.example`)
- [x] 4.2 Create `~/.komodo-stacks/litellm/.env` with:
      - Local Infisical env (host.docker.internal:8081, d900f50a, dev,
        7177c4ef, ~/.locket/infisical_secret)
      - Lakehouse creds (POSTGRES_USER, POSTGRES_PASSWORD, CLICKHOUSE_*,
        GARAGE_*, REDIS_PASSWORD) — REAL values
      - LITELLM_MASTER_KEY + LITELLM_SALT_KEY (locally generated)
- [x] 4.3 Create `~/.komodo-stacks/litellm/compose.local.yaml`:
      - Force `cianfhoghlaim` as external (avoid collision with openclaw's
        external declaration)
      - Force `lakehouse_lakehouse` as external (already exists)
- [x] 4.4 Fix the locket sidecar (5 bugs — see spec delta for the
      canonical contract):
      - Add `--infisical-url`, `--infisical-default-project-id`,
        `--infisical-default-environment`, `--infisical-default-path` flags
      - Drive URL/project/env via `environment:` block (portable across
        OCI and local-fallback)
      - Healthcheck uses `locket` (binary on PATH) not `/locket`
      - tmpfs mode 700 → 755
      - `infisical_secret.file` default = our `~/.locket/infisical_secret`
- [x] 4.5 Rewrite `bonneagar/stacks/litellm/secrets.env` to use the locket
      v0.17+ format (`?path=/<folder>` for the folder)
- [x] 4.6 Replace `config/config.yaml` with a minimal stub
      (the full 22-key + 24-vision-model config has a `fallback_chain` schema
      mismatch with litellm v1.91.0 — out of scope; can be regenerated later)
- [x] 4.7 `docker compose -f compose.yaml -f sidecar.yaml -f compose.local.yaml up -d`
- [x] 4.8 Wait for locket + litellm migrations to complete (~60s)
- [x] 4.9 `curl /health/liveliness` → 200, "I'm alive!"
- [x] 4.10 `curl /health/readiness` → 200
- [x] 4.11 `curl /v1/models` → 200, `{"data":[],"object":"list"}` (empty because
      the minimal config has no models — gateway itself works)

## 5. Bring up Langfuse (30 min)

- [x] 5.1 Create `~/.komodo-stacks/langfuse/` directory + symlinks
- [x] 5.2 Create `~/.komodo-stacks/langfuse/.env` with the local Infisical
      fallback + REAL lakehouse creds (NOT the dev-password placeholders
      that ship in `.env.dev`)
- [x] 5.3 Fix the langfuse sidecar (same 5 bugs as litellm)
- [x] 5.4 Rewrite `bonneagar/stacks/langfuse/secrets.env` (v0.17+ format)
- [x] 5.5 Force `compose.local.yaml`:
      - `lakehouse_lakehouse` as external
      - `langfuse` as a local bridge (langfuse-web ↔ langfuse-worker)
- [x] 5.6 First up attempt failed (locket crashed with 502 Bad Gateway) —
      root cause: the locket container was on the `langfuse_default` network
      (compose's auto-generated default), NOT on `langfuse_langfuse` where
      `host.docker.internal` mapping is set up
- [x] 5.7 Fix the sidecar: change `networks: default:` to `networks:
      langfuse: external: true, name: langfuse_langfuse` + add `lakehouse`
      to the locket's networks
- [x] 5.8 Second up attempt: locket resolved 5 secrets, but redis
      auth failed (`WRONGPASS`). The `.env.dev` had `REDIS_PASSWORD=devpassword`
      but the actual `redis-server --requirepass` is `c9f2e6ea1204a94234d7fba213dc7a7b`
- [x] 5.9 Fix `.env` with the REAL redis password (also the correct ClickHouse
      user `clickhouse` not `oideachais`, and the correct internal port 6379
      not the host-mapped 6381)
- [x] 5.10 `docker compose -f compose.yaml -f sidecar.yaml -f compose.local.yaml up -d`
      with `set -a && . .env && set +a` to source the env
- [x] 5.11 Langfuse up, `/api/public/health` → 200, `{"status":"OK","version":"3.224.1"}`
- [x] 5.12 Langfuse-web on port 3001 (NOT 3000 — the docker compose remaps)

## 6. Fix openclaw `gateway.mode=local` (5 min)

- [x] 6.1 Add `"mode": "local"` to `gateway` block in
      `bonneagar/stacks/openclaw/config/openclaw.json`
- [x] 6.2 Update `openclaw/sidecar.yaml` openclaw service:
      - Remove `env_file: /run/secrets/locket/secrets.env` (parse-time error)
      - Add a `command:` shell wrapper that sources the file at runtime
      - Add `--allow-unconfigured` flag to the openclaw binary
- [x] 6.3 Add a chmod init container (alpine, user 0:0) that runs once
      after the locket sidecar is healthy, chmods the secrets.env to 644
      (locket writes mode 600 by default; the openclaw consumer user 1000
      can't read 600 files)
- [x] 6.4 Fix the tmpfs mode 1777 Docker daemon rejection: removing the
      `read_only: true` was rejected (`invalid tmpfs option ["mode:1777"]`).
      Fix: keep `read_only: true` but add a tmpfs for /home/node/.openclaw
      (the WORKDIR) without the mode 1777 (default 755 works for the
      openclaw binary's /tmp needs)
- [x] 6.5 Restart openclaw, chmod init exits 0, openclaw starts
- [x] 6.6 Openclaw WebSocket gateway listening on `ws://127.0.0.1:18789`
      (HTTP /api/health returns 52 "Empty reply" because the gateway is
      WebSocket-only, not HTTP)

## 7. Fix hermes (s6-overlay permissions, 30 min)

- [x] 7.1 Add chmod init container to hermes (same pattern as openclaw)
- [x] 7.2 Multiple attempts at the user: + tmpfs: + read_only:
      combination to satisfy s6-overlay's `/run belongs to uid X` check:
      - `user: 1000:1000` + `read_only: true` + `tmpfs: /run:8m,mode:1777`:
        Docker daemon rejects mode 1777 under no-new-privileges
      - `user: 0:0` + `read_only: true` + `tmpfs: /run:8m`: s6-overlay gets
        `/run` owned by 0, but image's s6-overlay init files are at
        `/run/s6/basedir/bin/init` which is now missing → `Permission denied`
      - `user: 10000:10000` (the internal `hermes` user from /etc/passwd):
        s6-overlay gets `/run` owned by 10000, but `cd /opt/data` fails
        because /opt/data is mode 700 owned by 10000
      - `user: 0:0` + `cap_add: [SETUID, SETGID]`: s6-overlay runs
        s6-overlay-suexec which fails with `unable to setgid to root`
- [x] 7.3 Settled on: `user: 0:0` + no `read_only` + no
      `no-new-privileges` + cap_drop ALL (upstream s6-overlay pattern)
- [x] 7.4 Removed explicit `/opt/data` volume mount (was breaking
      /opt/data ownership which is `hermes:hermes` mode 700)
- [x] 7.5 Hermes s6-overlay boots all services:
      - `s6-rc: service main-hermes successfully started`
      - `s6-rc: service dashboard successfully started`
      - `s6-rc: service legacy-cont-init successfully started`
- [x] 7.6 DISCOVERED: hermes main service failed with
      `cd: can't cd to /opt/data` — because the locket sidecar wrote
      the un-resolved template (passthrough mode) which sh interpreted
      as a script with bad infisical:// references
- [x] 7.7 (Still in restart loop at session end) — need to either:
      - Fix the locket v0.17.3 + Infisical v0.161+ API bug
      - Or write a wrapper that pre-processes the secrets.env to remove
        the `{{ infisical://... }}` placeholders before sh sees them

## 8. Cross-stack verification (Phase F)

- [x] 8.1 All 21 expected containers running
- [x] 8.2 DNS resolution: openclaw → litellm ✅; openclaw → langfuse ❌
      (different networks); hermes → anything ❌ (different network)
- [x] 8.3 4 locket sidecars all "healthy" but in passthrough mode
- [x] 8.4 API endpoints:
      - LiteLLM `/health/liveliness` → 200
      - Langfuse `/api/public/health` → 200
      - OpenClaw WebSocket `:18789` → 52 (expected, WS only)
      - Hermes `:9119/api/health` → 000 (in crash loop)

## 9. OpenSpec change (Phase G — this file + spec + scripts + runbook)

- [x] 9.1 `proposal.md` (this change's proposal)
- [x] 9.2 `tasks.md` (this file)
- [x] 9.3 `specs/infrastructure-stacks/spec.md` (2 ADDED Requirements)
- [x] 9.4 `bonneagar/scripts/seed-bunchloch-litellm-langfuse-fallback.sh`
- [x] 9.5 `bonneagar/deploy-runbooks/full-local-agent-platform-stack-2026-07.md`
- [x] 9.6 `bonneagar/komodo/procedures/deploy-litellm-bunchloch-local-v1.toml`
- [x] 9.7 Canonical file modifications: litellm + langfuse sidecar.yaml +
      secrets.env (5 + 5 = 10 file changes)
- [x] 9.8 `openspec validate <id> --strict` (MUST pass)
- [x] 9.9 `git commit -m "feat(iaC): full local agent platform stack (litellm + langfuse + hermes)"`
- [x] 9.10 `git push`
- [x] 9.11 (DO NOT archive — leave change open until the locket bug
      and hermes s6-overlay are fixed in follow-up changes)