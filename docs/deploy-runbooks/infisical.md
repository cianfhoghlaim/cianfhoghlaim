# Runbook: infisical

> Written for a future AI agent. Every snippet is shell-
> pasteable. **Do not auto-execute** — the agent must paste
> each snippet deliberately.

## Pre-flight

```bash
# 0.1 — Verify ssh + docker + infisical CLI
command -v ssh      || { echo "ERROR: ssh not installed";      exit 1; }
command -v docker   || { echo "ERROR: docker not installed";   exit 1; }
command -v infisical >/dev/null 2>&1 || {
  echo "ERROR: infisical CLI not installed; install with: brew install infisical"
  exit 1
}

# 0.2 — Verify passwordless SSH to arm1-oci
ssh -o ConnectTimeout=5 -o BatchMode=yes arm1-oci 'true' \
  || { echo "ERROR: cannot reach arm1-oci"; exit 2; }

# 0.3 — Verify the vault env exists
infisical environments list --project-id <INFISICAL_PROJECT_ID> \
  | grep -q dev-baile \
  || { echo "ERROR: dev-baile env not found"; exit 3; }
```

## First-time deploy

```bash
# 1.1 — Snapshot the existing arm1-oci state
bash infrastructure/audit/scripts/inventory-arm1-oci.sh

# 1.2 — Create the run_directory on arm1-oci
ssh arm1-oci 'mkdir -p /etc/komodo/storage/infisical'

# 1.3 — rsync the 6 GOLD_STANDARD files
rsync -avz --delete \
  infrastructure/infisical/{compose.yaml,sidecar.yaml,secrets.env,blueprint.yaml,README.md} \
  arm1-oci:/etc/komodo/storage/infisical/

# 1.4 — rsync the .env.example (committed, no real secrets)
ssh arm1-oci '[[ -f /etc/komodo/storage/infisical/.env.example ]] || exit 4'
# NOTE: .env.example is currently missing from this stack — Phase C
# left it as a known gap; create it before deploy:
#   touch infrastructure/infisical/.env.example
#   echo "# INFISICAL_CLIENT_ID=replace-me" >> infrastructure/infisical/.env.example

# 1.5 — Add the Infisical secrets to the vault (the Locket sidecar
#       will read them at container start)
INFISICAL_PROJECT_ID=$(grep -E '^INFISICAL_PROJECT_ID' .env | cut -d= -f2)
for secret in INFISICAL_CLIENT_ID INFISICAL_CLIENT_SECRET \
              INFISICAL_DB_URL INFISICAL_REDIS_URL \
              INFISICAL_OIDC_CLIENT_ID INFISICAL_OIDC_CLIENT_SECRET \
              INFISICAL_ENCRYPTION_KEY INFISICAL_INVITE_ONLY_SIGNUP \
              INFISICAL_DISABLE_SIGNUP; do
  infisical secrets set "$secret" "$(grep "^$secret=" .env | cut -d= -f2-)" \
    --project-id "$INFISICAL_PROJECT_ID" --env dev-baile \
    --path /infisical
done

# 1.6 — Wire Infisical as a Komodo stack. Append to
#       infrastructure/komodo/stacks/infisical-arm1-oci.toml (or
#       create it if it doesn't exist):
cat >> infrastructure/komodo/stacks/infisical-arm1-oci.toml <<'KOMODO_EOF'

[[stack]]
name = "infisical"
description = "Infisical — self-hosted secret vault"
tags = ["host:arm1-oci", "tier:control-plane", "type:secrets", "domain:infisical.cianfhoghlaim.ie"]
[stack.config]
server_id = "arm1-oci"
run_directory = "/etc/komodo/storage/infisical"
file_paths = ["compose.yaml", "sidecar.yaml", "secrets.env", "blueprint.yaml"]
KOMODO_EOF

# 1.7 — Trigger Komodo to pull the new stack
node -e "
  import('komodo_client').then(async ({ KomodoClient }) => {
    const c = new KomodoClient({
      url: 'https://komodo.cianfhoghlaim.ie',
      key: process.env.KOMODO_API_KEY,
      secret: process.env.KOMODO_API_SECRET,
    });
    await c.deployStack({ stack: 'infisical', server: 'arm1-oci' });
  });
"
```

## Verify

```bash
# 2.1 — Container is up on arm1-oci
ssh arm1-oci 'docker ps --format "{{.Names}}\t{{.Status}}" | grep infisical'
# Expected: infisical-backend   Up N minutes (healthy)
#           infisical-postgres  Up N minutes (healthy)
#           infisical-locket    Up N minutes (healthy)

# 2.2 — The /api/v1/status endpoint responds
ssh arm1-oci 'curl -fsS http://localhost:8080/api/v1/status | jq .'

# 2.3 — The Locket sidecar is injecting secrets
ssh arm1-oci 'docker exec infisical-locket /locket healthcheck'
# Expected: OK

# 2.4 — The Pangolin private resource is registered
bash infrastructure/audit/scripts/probe-public-urls.sh | grep infisical
# Expected: https://infisical.cianfhoghlaim.ie  <2xx or 3xx>  <time>  (not 5xx)

# 2.5 — OIDC login flow works (manual — requires a browser)
# Open https://infisical.cianfhoghlaim.ie and sign in via Pocket ID
```

## Rollback

```bash
# 3.1 — Stop the Infisical stack via Komodo
node -e "
  import('komodo_client').then(async ({ KomodoClient }) => {
    const c = new KomodoClient({
      url: 'https://komodo.cianfhoghlaim.ie',
      key: process.env.KOMODO_API_KEY,
      secret: process.env.KOMODO_API_SECRET,
    });
    await c.stopStack({ stack: 'infisical', server: 'arm1-oci' });
  });
"

# 3.2 — Optional: remove the Pangolin private resource
#        (so a future re-deploy can recreate it from the blueprint)
node -e "
  import('komodo_client').then(async ({ KomodoClient }) => {
    const c = new KomodoClient({
      url: 'https://komodo.cianfhoghlaim.ie',
      key: process.env.KOMODO_API_KEY,
      secret: process.env.KOMODO_API_SECRET,
    });
    await c.deleteResource({ resourceId: 'infisical' });
  });
"
# NOTE: if a manually-created private resource exists (per
# HEALTH_REPORT.md Session 3), delete it via the Pangolin UI
# instead — the API cannot overwrite a manual entry.

# 3.3 — Optionally: remove the dev-baile /infisical/* secrets
for secret in $(infisical secrets list --project-id "$INFISICAL_PROJECT_ID" --env dev-baile --path /infisical | awk '{print $1}'); do
  infisical secrets delete "$secret" --project-id "$INFISICAL_PROJECT_ID" --env dev-baile --path /infisical
done
```

## Last verified

- 2026-06-15: runbook drafted, no end-to-end deploy executed.
  See `openspec/changes/audit-infrastructure-2026-06-15/proposal.md`
  for why deploy is deferred.
- The 4 known blockers from `infrastructure/stacks/HEALTH_REPORT.md`
  Session 3 (newt/pangolin version, 3 manual private resources,
  expired `PANGOLIN_API_KEY`, `komodo-locket` production
  credentials) may need fixing before the deploy succeeds.
