# Repair: Pangolin Private Infisical Resource (arm1-OCI)

## Symptom
`curl -ksS https://infisical.cianfhoghlaim.ie/api/status` returns 502.
Locket sidecars across the platform cannot resolve secrets.

## Root cause
Pangolin private-resource YAML drift on Pangolin Core's Postgres
(since the last Pangolin EE upgrade or since the last
`iac:sync:sites` invocation).

## Fix (one command)

```bash
km run procedure repair-pangolin-private-infisical-arm1-oci-v1
```

The procedure runs `iac:sync:sites` -> polls `/api/status` for 200 ->
runs `iac:rotate-auth` -> smoke-tests locket from bunchloch -> writes
an audit record to `/tmp/infisical-pangolin-private-repair-${TS}.json`.

## Manual fallback (if Komodo is unavailable)

```bash
# Step 1: re-emit the private resource
mise run iac:sync:sites

# Step 2: wait for 200
for i in {1..12}; do
  STATUS=$(curl -ksS -o /dev/null -w '%{http_code}' https://infisical.cianfhoghlaim.ie/api/status)
  [ "$STATUS" = '200' ] && break
  sleep 5
done

# Step 3: rotate bons-iac auth
mise run iac:rotate-auth --target=bons-iac

# Step 4: smoke-test locket
INFISICAL_URL=https://infisical.cianfhoghlaim.ie locket healthcheck
```

## Related
- Change: `2026-07-24-deploy-openclaw-hermes-bunchloch-local-infisical-fallback-v1`
  (the emergency fallback that was running during the repair window)
- Spec: `infrastructure-stacks` §"Pangolin private-resource drift"