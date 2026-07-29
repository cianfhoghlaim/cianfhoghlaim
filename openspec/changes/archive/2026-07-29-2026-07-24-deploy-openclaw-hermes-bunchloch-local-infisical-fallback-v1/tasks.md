# Tasks: 2026-07-24-deploy-openclaw-hermes-bunchloch-local-infisical-fallback-v1

## 1. Verify bunchloch prerequisites

- [ ] 1.1 `docker ps --format '{{.Names}}' | grep -E '^(infisical|locket|openclaw|hermes|pangolin)-' | wc -l` returns 0
- [ ] 1.2 `docker network ls | grep -E '^(cianfhoghlaim|bunchloch-infra)$'` returns 0 (neither exists; OK)
- [ ] 1.3 `cat /Users/cianmacandeisigh/dev/kings_college_galway/infisical_secret | head -1` — confirm the symlink target
      `bonneagar/stacks/infisical/infisical_secret` exists and is readable
- [ ] 1.4 `mise run preflight:arm-oci --skip-namespace --emit-md | tail -10` — confirm
      "Pangolin reachable" + "Infisical reachable" both show FAIL
      (this is the explicit signal that the OCI private resource is the
      bottleneck we are routing around)
- [ ] 1.5 `mkdir -p /etc/komodo/secrets` — create the Periphery mount dir
      for the infisical_secret file

## 2. Bring up the local Infisical vault

- [ ] 2.1 `docker network create bunchloch-infra` (idempotent — `|| true`)
- [ ] 2.2 `cd bonneagar/stacks/infisical`
- [ ] 2.3 `docker compose -f compose.yaml -f sidecar.yaml up -d db redis backend`
- [ ] 2.4 `for i in {1..24}; do sleep 5; STATUS=$(curl -ksS -o /dev/null -w '%{http_code}' http://localhost:8081/api/status); if [ "$STATUS" = '200' ]; then break; fi; done`
- [ ] 2.5 `curl -ksS http://localhost:8081/api/status | jq` — confirm
      `{ "status": "ok", "version": "v0.161.x" }`

## 3. Bootstrap the dev-baile project + 9 openclaw/hermes secrets

- [ ] 3.1 Open `http://127.0.0.1:8081` in browser, sign up first user
      (becomes org admin)
- [ ] 3.2 Create a new project named `dev-baile` (the canonical project
      name — same as on arm1-oci; secrets.env files reference it by name)
- [ ] 3.3 Project Settings → Machine Identities → Create identity
      `bons-iac`; grant `Member` on `dev-baile/dev`; **capture**
      Client ID + Client Secret
- [ ] 3.4 Run `INFISICAL_URL=http://127.0.0.1:8081 mise run iac:bootstrap-infisical`
      (it will read the captured client_id/secret from stdin / .env)
- [ ] 3.5 Run the new seed script: `bun run scripts/seed-bunchloch-fallback-vault.sh`
      — writes the 9 openclaw/hermes secret paths + the 7 infisical
      meta-secrets (encryption_key, auth_secret, postgres_password, etc.)
- [ ] 3.6 `infisical secrets list --project-id=<UUID> --env=dev | jq '.[] | .path'`
      — confirm >= 16 paths present (7 infisical + 9 openclaw/hermes)
- [ ] 3.7 `cp ~/.env /etc/komodo/secrets/infisical_secret && chmod 0600 /etc/komodo/secrets/infisical_secret`

## 4. Install the locket binary + verify it resolves secrets

- [ ] 4.1 `mise run iac:bootstrap-locket-binary` (installs
      `/usr/local/bin/locket` from the bons IaC)
- [ ] 4.2 `locket --provider=infisical --infisical-client-id=$INFISICAL_CLIENT_ID \
      --infisical-client-secret=file:/etc/komodo/secrets/infisical_secret \
      --map=/dev/null:/tmp/locket-test --mode=oneshot healthcheck`
      — confirm locket resolves >= 16 secrets

## 5. Bring up openclaw + hermes

- [ ] 5.1 `docker volume create openclaw_stack-secrets --driver local \
      --driver-opt type=tmpfs --driver-opt device=tmpfs \
      --driver-opt o=uid=65532,gid=65532,mode=700`
- [ ] 5.2 `docker volume create hermes_stack-secrets --driver local \
      --driver-opt type=tmpfs --driver-opt device=tmpfs \
      --driver-opt o=uid=65532,gid=65532,mode=700`
- [ ] 5.3 `cd bonneagar/stacks/openclaw && docker compose -f compose.yaml -f sidecar.yaml up -d`
      — the parse-time env_file error is resolved by `depends_on:
      service_healthy` since docker compose 2.20+ only validates
      env_file paths when the service starts, after locket has
      written them (verify this with `docker inspect openclaw-locket`
      showing `/run/secrets/locket/secrets.env` populated)
- [ ] 5.4 `cd ../hermes && docker compose -f compose.yaml -f sidecar.yaml up -d`
- [ ] 5.5 `docker ps --filter name=openclaw --filter name=hermes --format 'table {{.Names}}\t{{.Status}}'`
      — confirm 4 containers Up + Healthy (openclaw, openclaw-locket,
      hermes, hermes-locket)

## 6. Health checks (4-point verification)

- [ ] 6.1 `docker exec openclaw-locket -- /locket healthcheck` returns OK
- [ ] 6.2 `docker exec hermes-locket -- /locket healthcheck` returns OK
- [ ] 6.3 `curl -fsS http://openclaw:18789/api/health` returns 200
- [ ] 6.4 `curl -fsS http://hermes:9119/api/health` returns 200
- [ ] 6.5 `docker logs openclaw --tail 50 2>&1 | grep -E 'channel (enabled|disabled)' | wc -l`
      returns >= 1 (the gateway initialised its channel-fanout layer)

## 7. Handover + openspec archive

- [ ] 7.1 Update `bonneagar/stacks/openclaw/README.md` with a new
      "Bunchloch fallback deploy" subsection referencing this change
- [ ] 7.2 Update `.agents/skills/secrets-management/SKILL.md` with a
      note: "When the OCI Pangolin private resource returns 502, use
      the local fallback path documented in
      openspec/changes/2026-07-24-deploy-openclaw-hermes-bunchloch-local-infisical-fallback-v1/"
- [ ] 7.3 `git add openspec/changes/<id>/ bonneagar/scripts/seed-bunchloch-fallback-vault.sh \
      bonneagar/komodo/procedures/deploy-bunchloch-infisical-fallback-v1.toml \
      bonneagar/deploy-runbooks/openclaw-hermes-bunchloch-local-2026-07.md \
      openspec/specs/infrastructure-stacks/spec.md`
- [ ] 7.4 `openspec validate 2026-07-24-deploy-openclaw-hermes-bunchloch-local-infisical-fallback-v1 --strict`
      (MUST pass with exit code 0 before commit)
- [ ] 7.5 `git commit -m "feat(iaC): local Infisical fallback for openclaw + hermes on bunchloch"`
- [ ] 7.6 `git push` (per the "Landing the Plane" workflow)
- [ ] 7.7 After deploy is verified green on bunchloch:
      `openspec archive 2026-07-24-deploy-openclaw-hermes-bunchloch-local-infisical-fallback-v1 --yes`