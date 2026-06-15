# Runbook: vikunja

> Written for a future AI agent. Every snippet is shell-
> pasteable. **Do not auto-execute** — the agent must paste
> each snippet deliberately.

Vikunja is the team task management + Gantt + Kanban
platform, deployed on `bunchloch` per
`infrastructure/komodo/stacks/team-workflow.toml` and exposed
at `vikunja.cianfhoghlaim.ie` via Pangolin.

## Pre-flight

```bash
# 0.1 — Verify ssh + docker
command -v ssh    || { echo "ERROR: ssh not installed";    exit 1; }
command -v docker || { echo "ERROR: docker not installed"; exit 1; }

# 0.2 — Verify the vikunja init scripts are present
ls infrastructure/stacks/tools/vikunja/init/ 2>/dev/null \
  || { echo "ERROR: vikunja init/ dir missing; the DB init is required on first boot"; exit 2; }

# 0.3 — Verify the secrets are in the vault
infisical environments list --project-id "$INFISICAL_PROJECT_ID" \
  | grep -q dev-baile \
  || { echo "ERROR: dev-baile env not found"; exit 3; }
for secret in VIKUNJA_DATABASE_PASSWORD VIKUNJA_SERVICE_ROOT_PASSWORD; do
  infisical secrets get "$secret" --project-id "$INFISICAL_PROJECT_ID" --env dev-baile --path /vikunja 2>/dev/null \
    || { echo "WARN: $secret not in /vikunja; provision it"; }
done
```

## First-time deploy

```bash
# 1.1 — Create the run_directory on bunchloch
mkdir -p /etc/komodo/storage/vikunja

# 1.2 — rsync the 6 GOLD_STANDARD files
rsync -avz --delete \
  infrastructure/stacks/tools/vikunja/{compose.yaml,sidecar.yaml,secrets.env,blueprint.yaml,README.md} \
  /etc/komodo/storage/vikunja/

# 1.3 — rsync the init scripts (Vikunja's first-boot DB migration)
rsync -avz --delete infrastructure/stacks/tools/vikunja/init/ \
  /etc/komodo/storage/vikunja/init/

# 1.4 — Bring up the vikunja stack
cd /etc/komodo/storage/vikunja
docker compose -f compose.yaml -f sidecar.yaml up -d
docker compose -f compose.yaml -f sidecar.yaml ps
cd -

# 1.5 — Register the Pangolin private resource (the blueprint
#       is in blueprint.yaml; newt picks it up on the next cycle)
```

## Verify

```bash
# 2.1 — All 2 vikunja services are up
docker ps --format "{{.Names}}\t{{.Status}}" | grep -E "^(vikunja|vikunja-db)"
# Expected: vikunja      Up N minutes (healthy)
#           vikunja-db   Up N minutes

# 2.2 — The /health endpoint responds
docker exec vikunja curl -fsS http://localhost:3456/health -o /dev/null -w "%{http_code}\n"
# Expected: 200

# 2.3 — The init/ scripts ran (Vikunja's first-boot migration)
docker logs vikunja 2>&1 | grep -E "Migrating database|Schema is up to date"
# Expected: "Schema is up to date" or similar

# 2.4 — The Pangolin public URL responds
bash infrastructure/audit/scripts/probe-public-urls.sh | grep vikunja
# Expected: https://vikunja.cianfhoghlaim.ie  <2xx or 3xx>  <time>  (not 5xx)

# 2.5 — The Pocket ID OIDC flow works (manual)
# Open https://vikunja.cianfhoghlaim.ie and sign in via Pocket ID
```

## Rollback

```bash
# 3.1 — Stop the vikunja stack
cd /etc/komodo/storage/vikunja
docker compose -f compose.yaml -f sidecar.yaml down --remove-orphans
cd -

# 3.2 — Optionally drop the vikunja database
docker exec vikunja-db psql -U vikunja -c "DROP DATABASE vikunja"
# (irreversible)

# 3.3 — Optionally remove the vikunja volumes
docker volume rm vikunja-data vikunja-uploads
```

## Last verified

- 2026-06-15: runbook drafted, no end-to-end deploy executed.
  See `openspec/changes/audit-infrastructure-2026-06-15/proposal.md`
  for why deploy is deferred.
- Vikunja is **not in the live container inventory** at
  2026-06-15 (per `infrastructure/stacks/HEALTH_REPORT.md`
  and the historical log). This runbook is the first time
  it's been written down; the deploy brings it online for
  the first time.
- The 4 known blockers from the historical log
  (newt/pangolin version, 3 manual private resources,
  expired `PANGOLIN_API_KEY`, `komodo-locket` production
  credentials) all need fixing before the deploy succeeds.
