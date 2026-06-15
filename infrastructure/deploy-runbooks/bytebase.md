# Runbook: bytebase

> Written for a future AI agent. Every snippet is shell-
> pasteable. **Do not auto-execute** — the agent must paste
> each snippet deliberately.

Bytebase is the SQL-review + migration platform. The
intentional deployment target is `arm1-oci` (per the user's
deploy plan), with potential to also run a second instance
on `bunchloch` for the dev workflow.

## Pre-flight

```bash
# 0.1 — Verify ssh + docker
command -v ssh    || { echo "ERROR: ssh not installed";    exit 1; }
command -v docker || { echo "ERROR: docker not installed"; exit 1; }
ssh -o ConnectTimeout=5 -o BatchMode=yes arm1-oci 'true' \
  || { echo "ERROR: cannot reach arm1-oci"; exit 2; }

# 0.2 — Verify the bytebase-config is present
[ -f infrastructure/stacks/engineering/bytebase/bytebase-config.yaml ] \
  || { echo "ERROR: bytebase-config.yaml missing; this file holds the workspace policies + approval rules"; exit 3; }

# 0.3 — Verify the secrets are in the vault
infisical environments list --project-id "$INFISICAL_PROJECT_ID" \
  | grep -q dev-baile \
  || { echo "ERROR: dev-baile env not found"; exit 4; }
for secret in BYTEBASE_EXTERNAL_URL BYTEBASE_PG_PASSWORD; do
  infisical secrets get "$secret" --project-id "$INFISICAL_PROJECT_ID" --env dev-baile --path /bytebase 2>/dev/null \
    || { echo "WARN: $secret not in /bytebase; provision it"; }
done
```

## First-time deploy (on arm1-oci)

```bash
# 1.1 — Create the run_directory on arm1-oci
ssh arm1-oci 'mkdir -p /etc/komodo/storage/bytebase'

# 1.2 — rsync the 5 GOLD_STANDARD files (missing .env.example — see Phase C)
rsync -avz --delete \
  infrastructure/stacks/engineering/bytebase/{compose.yaml,sidecar.yaml,secrets.env,blueprint.yaml,bytebase-config.yaml,README.md} \
  arm1-oci:/etc/komodo/storage/bytebase/

# 1.3 — Create the .env.example (Phase C left this as a known gap)
ssh arm1-oci 'cat > /etc/komodo/storage/bytebase/.env.example <<ENV_EOF
# BYTEBASE_EXTERNAL_URL=https://bytebase.cianfhoghlaim.ie
# BYTEBASE_PG_PASSWORD=replace-me
ENV_EOF'

# 1.4 — Bring up the bytebase stack
ssh arm1-oci 'cd /etc/komodo/storage/bytebase && docker compose -f compose.yaml -f sidecar.yaml up -d'

# 1.5 — Register the Pangolin private resource
```

## Verify

```bash
# 2.1 — The bytebase service is up
ssh arm1-oci 'docker ps --format "{{.Names}}\t{{.Status}}" | grep bytebase'
# Expected: bytebase   Up N minutes (healthy)

# 2.2 — The /healthz endpoint responds
ssh arm1-oci 'docker exec bytebase curl -fsS http://localhost:8080/healthz -o /dev/null -w "%{http_code}\n"'
# Expected: 200

# 2.3 — The bytebase-config is loaded (manual)
# Open https://bytebase.cianfhoghlaim.ie → Settings → Workspace →
# verify the policies from bytebase-config.yaml are present

# 2.4 — A migration can be applied (manual)
# Connect bytebase to one of the Postgres services (e.g.
# oideachais-postgres) and apply a no-op migration; verify
# the SQL-review + approval flow works

# 2.5 — The Pangolin public URL responds
bash infrastructure/audit/scripts/probe-public-urls.sh | grep bytebase
# Expected: https://bytebase.cianfhoghlaim.ie  <2xx or 3xx>  <time>  (not 5xx)
```

## Rollback

```bash
# 3.1 — Stop the bytebase stack
ssh arm1-oci 'cd /etc/komodo/storage/bytebase && docker compose -f compose.yaml -f sidecar.yaml down --remove-orphans'

# 3.2 — Optionally drop the bytebase metadata database
# (Bytebase's own Postgres is part of the compose; dropping
#  it loses the workspace config + audit trail)
ssh arm1-oci 'docker exec bytebase-pg psql -U bytebase -c "DROP DATABASE bytebase"'
# (irreversible)

# 3.3 — Remove the Pangolin private resource
#   → Open https://pangolin.cianfhoghlaim.ie → Sites → bytebase → Resources → delete
```

## Last verified

- 2026-06-15: runbook drafted, no end-to-end deploy executed.
  See `openspec/changes/audit-infrastructure-2026-06-15/proposal.md`
  for why deploy is deferred.
- bytebase is **not in the live container inventory** at
  2026-06-15. This runbook is the first time it's been
  written down; the deploy brings it online for the first
  time.
- The 4 known blockers from the historical log
  (newt/pangolin version, 3 manual private resources,
  expired `PANGOLIN_API_KEY`, `komodo-locket` production
  credentials) all need fixing before the deploy succeeds.
