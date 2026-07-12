# Runbook: pangolin

> Written for a future AI agent. Every snippet is shell-
> pasteable. **Do not auto-execute** — the agent must paste
> each snippet deliberately.

## Pre-flight

```bash
# 0.1 — Verify ssh + docker
command -v ssh    || { echo "ERROR: ssh not installed";    exit 1; }
command -v docker || { echo "ERROR: docker not installed"; exit 1; }
ssh -o ConnectTimeout=5 -o BatchMode=yes arm1-oci 'true' \
  || { echo "ERROR: cannot reach arm1-oci"; exit 2; }

# 0.2 — Resolve the newt vs Pangolin server version mismatch
#       (HEALTH_REPORT.md Session 3, blocker #1)
NEW_VERSION=$(ssh arm1-oci 'docker inspect --format="{{.Image}}" pangolin | sed -E "s/.*fosrl\/pangolin:v?(.*)/\1/"')
NEWT_VERSION=$(docker inspect --format='{{index .Config.Labels "org.opencontainers.image.version"}}' newt-bunchloch 2>/dev/null \
  || echo "unknown")
# (Newt labels vary by version; the more reliable path is:)
NEWT_VERSION=$(docker exec newt-bunchloch -- newt --version 2>/dev/null \
  || docker exec newt-bunchloch -- /usr/local/bin/newt --version 2>/dev/null \
  || echo "unknown")

# If the version mismatch is the case (newt 1.12.5 + pangolin 1.18.4),
# fix block 1 first (see Rollback step 3.1 for one possible path).

# 0.3 — Verify the Pangolin API tokens are fresh
#       (HEALTH_REPORT.md Session 3, blocker #3)
[ -n "$PANGOLIN_API_KEY" ] || { echo "ERROR: PANGOLIN_API_KEY not set"; exit 3; }
node -e "
  fetch('https://pangolin.cianfhoghlaim.ie/api/v1/org', {
    headers: { 'Authorization': 'Bearer ' + process.env.PANGOLIN_API_KEY }
  }).then(r => process.exit(r.status === 200 ? 0 : 1))
" || { echo "ERROR: PANGOLIN_API_KEY is invalid or expired; mint a new one in the Pangolin UI"; exit 3; }
```

## First-time deploy

> **Note:** per `infrastructure/pangolin/a2a-resources.blueprint.yaml`,
> Pangolin is *not* a per-service stack — it is the
> infrastructure platform that fronts all `*.cianfhoghlaim.ie`
> domains. "Deploying Pangolin" means: stand up the
> Pangolin+Gerbil+Traefik+Pocket ID+TinyAuth+Middleware
> Manager+CrowdSec compose on `arm1-oci`, plus the newt
> client on `bunchloch`.

```bash
# 1.1 — Decide on the deployment topology
#       Per `infrastructure/PANGOLIN-SETUP.md`:
#         - Pangolin server + Gerbil (WireGuard): arm1-oci
#         - Traefik (public reverse-proxy): arm1-oci
#         - Pocket ID (OIDC): arm1-oci
#         - TinyAuth (SSO): arm1-oci
#         - Middleware Manager: arm1-oci
#         - CrowdSec (WAF): arm1-oci
#         - newt (Pangolin client): bunchloch

# 1.2 — Create the run_directory on arm1-oci
ssh arm1-oci 'mkdir -p /etc/pangolin/storage/{pangolin,gerbil,traefik,pocket-id,tinyauth,middleware-manager,crowdsec}'

# 1.3 — rsync the compose files
for svc in pangolin gerbil traefik pocket-id tinyauth middleware-manager crowdsec; do
  rsync -avz --delete \
    infrastructure/pangolin/$svc/{compose.yaml,sidecar.yaml,secrets.env,blueprint.yaml} \
    arm1-oci:/etc/pangolin/storage/$svc/ 2>/dev/null \
    || echo "WARN: stack $svc has missing GOLD_STANDARD files; create them first"
done

# 1.4 — Add the Pangolin machine identity to the Infisical vault
INFISICAL_PROJECT_ID=$(grep -E '^INFISICAL_PROJECT_ID' .env | cut -d= -f2)
for secret in PANGOLIN_API_KEY PANGOLIN_API_SECRET \
              POCKETID_ADMIN_PASSWORD POCKETID_SESSION_SECRET \
              TINYAUTH_ADMIN_PASSWORD; do
  infisical secrets set "$secret" "$(grep "^$secret=" .env | cut -d= -f2-)" \
    --project-id "$INFISICAL_PROJECT_ID" --env dev-baile \
    --path /pangolin
done

# 1.5 — Bring up Pangolin Core on arm1-oci
ssh arm1-oci 'cd /etc/pangolin/storage/pangolin && docker compose -f compose.yaml -f sidecar.yaml up -d'
ssh arm1-oci 'cd /etc/pangolin/storage/gerbil && docker compose -f compose.yaml -f sidecar.yaml up -d'
ssh arm1-oci 'cd /etc/pangolin/storage/traefik && docker compose -f compose.yaml -f sidecar.yaml up -d'
ssh arm1-oci 'cd /etc/pangolin/storage/pocket-id && docker compose -f compose.yaml -f sidecar.yaml up -d'
ssh arm1-oci 'cd /etc/pangolin/storage/tinyauth && docker compose -f compose.yaml -f sidecar.yaml up -d'
ssh arm1-oci 'cd /etc/pangolin/storage/middleware-manager && docker compose -f compose.yaml -f sidecar.yaml up -d'
ssh arm1-oci 'cd /etc/pangolin/storage/crowdsec && docker compose -f compose.yaml -f sidecar.yaml up -d'

# 1.6 — Bring up the newt client on bunchloch
docker compose -f infrastructure/pangolin/newt.yaml up -d
docker ps | grep newt
```

## Verify

```bash
# 2.1 — All 7 Pangolin services are up
ssh arm1-oci 'docker ps --format "{{.Names}}\t{{.Status}}" | grep -E "^(pangolin|gerbil|traefik|pocket-id|tinyauth|middleware-manager|crowdsec)"'

# 2.2 — The Pangolin UI responds
curl -I https://pangolin.cianfhoghlaim.ie/
# Expected: HTTP 200 (or 302 → Pocket ID SSO)

# 2.3 — The newt client has connected
docker logs newt-bunchloch 2>&1 | tail -20
# Expected: "Connected to Pangolin server", "Site resources sync"

# 2.4 — The private resources are registered
#        (the audit script reads the blueprint and probes each)
bash infrastructure/audit/scripts/probe-public-urls.sh | head -20
# Expected: at least 5 of the *.cianfhoghlaim.ie URLs return 2xx/3xx/4xx

# 2.5 — Pocket ID OIDC works (manual)
# Open https://pangolin.cianfhoghlaim.ie and sign in via Pocket ID
```

## Rollback

```bash
# 3.1 — Fix the newt/pangolin version mismatch (HEALTH_REPORT.md Session 3 blocker #1)
#       Option A: upgrade Pangolin to 1.13.0+
ssh arm1-oci 'cd /etc/pangolin/storage/pangolin && docker compose pull && docker compose -f compose.yaml -f sidecar.yaml up -d'
#       Option B: downgrade newt to 1.11.x
docker compose -f infrastructure/pangolin/newt.yaml down
docker pull fosrl/newt:1.11.0
# edit the newt.yaml to use fosrl/newt:1.11.0
docker compose -f infrastructure/pangolin/newt.yaml up -d

# 3.2 — Stop all 7 Pangolin services
for svc in pangolin gerbil traefik pocket-id tinyauth middleware-manager crowdsec; do
  ssh arm1-oci "cd /etc/pangolin/storage/$svc && docker compose -f compose.yaml -f sidecar.yaml down --remove-orphans"
done
docker compose -f infrastructure/pangolin/newt.yaml down

# 3.3 — Delete the 3 manually-created private resources via the Pangolin UI
#       (the API cannot overwrite a manual entry)
# Open https://pangolin.cianfhoghlaim.ie → Sites → each resource →
# Resource → delete the manual entry. Blueprint reapplies on next newt cycle.
```

## Last verified

- 2026-06-15: runbook drafted, no end-to-end deploy executed.
  See `openspec/changes/audit-infrastructure-2026-06-15/proposal.md`
  for why deploy is deferred.
- The 4 known blockers from `infrastructure/stacks/HEALTH_REPORT.md`
  Session 3 (newt/pangolin version, 3 manual private resources,
  expired `PANGOLIN_API_KEY`, `komodo-locket` production
  credentials) all need fixing before this deploy succeeds.
