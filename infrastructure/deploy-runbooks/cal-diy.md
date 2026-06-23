# Runbook: cal-diy

> Written for a future AI agent. Every snippet is shell-
> pasteable. **Do not auto-execute** — the agent must paste
> each snippet deliberately.

cal-diy is the cal.com community self-hosted build,
deployed on `arm1-oci` per `infrastructure/komodo/stacks/team-workflow.toml`
and exposed at `calcom.cianfhoghlaim.ie` via Pangolin.

## Pre-flight

```bash
# 0.1 — Verify ssh + docker
command -v ssh    || { echo "ERROR: ssh not installed";    exit 1; }
command -v docker || { echo "ERROR: docker not installed"; exit 1; }
ssh -o ConnectTimeout=5 -o BatchMode=yes arm1-oci 'true' \
  || { echo "ERROR: cannot reach arm1-oci"; exit 2; }

# 0.2 — Verify the cal.diy source is cloned into stedding
[ -d infrastructure/stedding/repos/cal.diy ] \
  || { echo "ERROR: cal.diy source not cloned; run: git clone https://github.com/calcom/cal.diy infrastructure/stedding/repos/cal.diy"; exit 3; }

# 0.3 — Verify the secrets are in the vault
infisical environments list --project-id "$INFISICAL_PROJECT_ID" \
  | grep -q dev-baile \
  || { echo "ERROR: dev-baile env not found"; exit 4; }
for secret in CALCOM_DB_PASSWORD CALCOM_NEXTAUTH_SECRET \
              CALCOM_ENCRYPTION_KEY CALCOM_WEBHOOK_SECRET \
              POCKETID_TEAM_WORKFLOW_CLIENT_SECRET; do
  infisical secrets get "$secret" --project-id "$INFISICAL_PROJECT_ID" --env dev-baile --path /calcom 2>/dev/null \
    || { echo "WARN: $secret not in /calcom; provision it"; }
done
```

## First-time deploy

```bash
# 1.1 — Create the run_directory on arm1-oci
ssh arm1-oci 'mkdir -p /etc/komodo/storage/cal-diy'

# 1.2 — rsync the 6 GOLD_STANDARD files (and clone the cal.diy source)
rsync -avz --delete \
  infrastructure/stacks/cal-diy/{compose.yaml,sidecar.yaml,secrets.env,blueprint.yaml,README.md} \
  arm1-oci:/etc/komodo/storage/cal-diy/

# 1.3 — rsync the cal.diy source so the build context is local
rsync -avz --delete infrastructure/stedding/repos/cal.diy/ \
  arm1-oci:/etc/komodo/storage/cal-diy/stedding/repos/cal.diy/

# 1.4 — Add the Pangolin private resource (manual via UI; the
#       blueprint cannot overwrite the manually-created entry
#       from HEALTH_REPORT.md Session 3)
#   → Open https://pangolin.cianfhoghlaim.ie
#   → Sites → cal-diy → Resources → delete the manual entry
#   → The blueprint reapplies on the next newt cycle
#   OR: edit the existing resource: change target to
#   `calcom-web:3000` and scheme to `http`

# 1.5 — Bring up the cal-diy stack
ssh arm1-oci 'cd /etc/komodo/storage/cal-diy && docker compose -f compose.yaml -f sidecar.yaml up -d'
```

## Verify

```bash
# 2.1 — All 3 cal-diy services are up
ssh arm1-oci 'docker ps --format "{{.Names}}\t{{.Status}}" | grep -E "^(calcom-web|calcom-db|calcom-redis)"'
# Expected: calcom-web     Up N minutes (healthy)
#           calcom-db      Up N minutes
#           calcom-redis   Up N minutes

# 2.2 — The /auth/setup endpoint responds (per Session 1 healthcheck fix)
ssh arm1-oci 'docker exec calcom-web curl -fsS http://localhost:3000/auth/setup -o /dev/null -w "%{http_code}\n"'
# Expected: 200

# 2.3 — The Pangolin public URL responds
bash infrastructure/audit/scripts/probe-public-urls.sh | grep calcom
# Expected: https://calcom.cianfhoghlaim.ie  <2xx or 3xx>  <time>  (not 5xx)

# 2.4 — Pocket ID OIDC login flow works (manual)
# Open https://calcom.cianfhoghlaim.ie → /auth/setup → sign in via Pocket ID
```

## Rollback

```bash
# 3.1 — Stop the cal-diy stack
ssh arm1-oci 'cd /etc/komodo/storage/cal-diy && docker compose -f compose.yaml -f sidecar.yaml down --remove-orphans'

# 3.2 — Delete the Pangolin private resource (if needed)
#   → Open https://pangolin.cianfhoghlaim.ie
#   → Sites → cal-diy → Resources → delete the cal-diy entry

# 3.3 — Optionally drop the calcom Postgres database
ssh arm1-oci 'docker exec calcom-db psql -U calcom -c "DROP DATABASE calcom"'
# (irreversible; the next deploy will need a fresh `prisma
#  migrate deploy` to recreate the schema)
```

## Last verified

- 2026-06-15: runbook drafted, no end-to-end deploy executed.
  See `openspec/changes/audit-infrastructure-2026-06-15/proposal.md`
  for why deploy is deferred.
- The 4 known blockers from `infrastructure/stacks/HEALTH_REPORT.md`
  Session 3 (newt/pangolin version, 3 manual private resources,
  expired `PANGOLIN_API_KEY`, `komodo-locket` production
  credentials) all need fixing before the deploy succeeds.
- The cal-diy `healthcheck` is `/auth/setup` (Session 1 fix
  — cal-diy does not expose `/api/v2/ping`).
