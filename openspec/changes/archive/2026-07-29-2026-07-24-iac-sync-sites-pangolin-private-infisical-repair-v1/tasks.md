# Tasks: 2026-07-24-iac-sync-sites-pangolin-private-infisical-repair-v1

## 1. Verify Change 1 fallback is still green (prerequisite)

- [ ] 1.1 `curl -fsS http://openclaw:18789/api/health` returns 200
- [ ] 1.2 `curl -fsS http://hermes:9119/api/health` returns 200
- [ ] 1.3 `docker ps --filter name=locket --format '{{.Names}}\t{{.Status}}'`
      — confirm openclaw-locket + hermes-locket both Up + Healthy
- [ ] 1.4 DO NOT tear down the bunchloch local Infisical yet

## 2. Re-emit the Pangolin private resource

- [ ] 2.1 `mise run preflight:arm-oci:strict` — confirm Pangolin is
      reachable (we need this working before `iac:sync:sites` can run)
- [ ] 2.2 `mise run iac:sync:sites 2>&1 | tee /tmp/iac-sync-sites-$(date -u +%Y%m%dT%H%M%SZ).log`
      — re-emits the 6 private resources (incl.
      `infisical.cianfhoghlaim.ie`) via the Pangolin Integrations API
- [ ] 2.3 For i in {1..12}; do sleep 5; STATUS=$(curl -ksS -o /dev/null
      -w '%{http_code}' https://infisical.cianfhoghlaim.ie/api/status);
      if [ "$STATUS" = '200' ]; then echo "OK after ${i} attempts"; break; fi;
      done — expect 200 within 60s
- [ ] 2.4 `curl -ksS https://infisical.cianfhoghlaim.ie/api/status | jq`
      — confirm `{ "status": "ok", "version": "v0.161.x" }`

## 3. Refresh the bons-iac Universal Auth credential

- [ ] 3.1 `mise run iac:rotate-auth --target=bons-iac 2>&1 | tee
      /tmp/iac-rotate-auth-$(date -u +%Y%m%dT%H%M%SZ).log` — mints a
      fresh client_secret + writes it to `~/.env` AND to
      `/etc/komodo/secrets/infisical_secret` on arm1-oci AND
      re-pushes the secret into the arm1-oci Infisical vault
- [ ] 3.2 `ssh arm1-oci 'cat /etc/komodo/secrets/infisical_secret | head -3'`
      — confirm the file has the new credential
- [ ] 3.3 `ssh arm1-oci 'curl -ksS -H "X-API-Key: $(grep INFISICAL_UNIVERSAL_AUTH_CLIENT_SECRET /etc/komodo/secrets/infisical_secret | cut -d= -f2 | tr -d \"\")" https://infisical.cianfhoghlaim.ie/api/v3/projects/f3cff583-b74b-4804-b9d3-db8b68885236/identity-machine-identities'`
      — confirm bons-iac can list identities (smoke test the auth)

## 4. Smoke-test from bunchloch (locket against the OCI vault)

- [ ] 4.1 `INFISICAL_URL=https://infisical.cianfhoghlaim.ie locket \
      --provider=infisical \
      --infisical-client-id=$INFISICAL_CLIENT_ID \
      --infisical-client-secret=file:/etc/komodo/secrets/infisical_secret \
      --map=/tmp/locket-test:/tmp/locket-test \
      --mode=oneshot healthcheck`
      — expect >= 16 secrets resolved against the OCI vault
- [ ] 4.2 `docker compose -f compose.yaml -f sidecar.yaml up -d` (in
      `bonneagar/stacks/openclaw/`) — expect the parse-time error to
      NOT occur (locket writes `/run/secrets/locket/secrets.env` before
      openclaw's `depends_on` resolves)

## 5. Tear down Change 1's local fallback

- [ ] 5.1 `cd bonneagar/stacks/infisical && docker compose -f compose.yaml -f sidecar.yaml down -v`
      — stops + removes the local Infisical containers and the named volume
- [ ] 5.2 `docker network rm bunchloch-infra` (idempotent)
- [ ] 5.3 `docker ps --filter name=infisical` — confirm 0 containers
- [ ] 5.4 `curl -fsS https://infisical.cianfhoghlaim.ie/api/status`
      — STILL returns 200 (we have not regressed the OCI path)

## 6. Handover + openspec archive

- [ ] 6.1 Write a JSON audit record to
      `/tmp/infisical-pangolin-private-repair-${TS}.json` capturing:
      { ts, host=arm1-oci, iac:sync:sites log path, iac:rotate-auth
        log path, smoke-test result, before-after /api/status
        timestamps }
- [ ] 6.2 `git add openspec/changes/2026-07-24-iac-sync-sites-pangolin-private-infisical-repair-v1/ \
      bonneagar/komodo/procedures/repair-pangolin-private-infisical-arm1-oci-v1.toml \
      bonneagar/deploy-runbooks/repair-pangolin-private-infisical-2026-07.md \
      openspec/specs/infrastructure-stacks/spec.md`
- [ ] 6.3 `openspec validate 2026-07-24-iac-sync-sites-pangolin-private-infisical-repair-v1 --strict`
      (MUST pass with exit code 0 before commit)
- [ ] 6.4 `git commit -m "fix(iaC): repair Pangolin private Infisical resource via iac:sync:sites + iac:rotate-auth"`
- [ ] 6.5 `git push` (per the "Landing the Plane" workflow)
- [ ] 6.6 After deploy is verified green on arm1-oci:
      `openspec archive 2026-07-24-deploy-openclaw-hermes-bunchloch-local-infisical-fallback-v1 --yes`
      `openspec archive 2026-07-24-iac-sync-sites-pangolin-private-infisical-repair-v1 --yes`