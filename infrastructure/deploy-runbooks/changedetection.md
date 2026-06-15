# Runbook: changedetection

> Written for a future AI agent. Every snippet is shell-
> pasteable. **Do not auto-execute** — the agent must paste
> each snippet deliberately.

changedetection.io is the change-detection / website
watcher. It periodically diffs target pages and notifies on
change. Integrated with the new
`firecrawl_monitor_create` MCP tool (per
`oideachais/notebooks/dashboards/medicine/all_nations.py`'s
intake pattern).

## Pre-flight

```bash
# 0.1 — Verify docker
command -v docker || { echo "ERROR: docker not installed"; exit 1; }

# 0.2 — Verify the secrets are in the vault
infisical environments list --project-id "$INFISICAL_PROJECT_ID" \
  | grep -q dev-baile \
  || { echo "ERROR: dev-baile env not found"; exit 2; }
for secret in CHANGEDETECTION_DB_PASSWORD CHANGEDETECTION_ADMIN_PASSWORD; do
  infisical secrets get "$secret" --project-id "$INFISICAL_PROJECT_ID" --env dev-baile --path /changedetection 2>/dev/null \
    || { echo "WARN: $secret not in /changedetection; provision it"; }
done
```

## First-time deploy

```bash
# 1.1 — Create the run_directory on bunchloch (the intended host)
mkdir -p /etc/komodo/storage/changedetection

# 1.2 — rsync the 5 GOLD_STANDARD files (missing .env.example — see Phase C)
rsync -avz --delete \
  infrastructure/stacks/tools/changedetection/{compose.yaml,sidecar.yaml,secrets.env,blueprint.yaml,README.md} \
  /etc/komodo/storage/changedetection/

# 1.3 — Create the .env.example (Phase C left this as a known gap)
cat > /etc/komodo/storage/changedetection/.env.example <<'ENV_EOF'
# CHANGEDETECTION_DB_PASSWORD=replace-me
# CHANGEDETECTION_ADMIN_PASSWORD=replace-me
# CHANGEDETECTION_BASE_URL=https://changedetection.cianfhoghlaim.ie
ENV_EOF

# 1.4 — Bring up the changedetection stack
cd /etc/komodo/storage/changedetection
docker compose -f compose.yaml -f sidecar.yaml up -d
docker compose -f compose.yaml -f sidecar.yaml ps
cd -

# 1.5 — Register the Pangolin private resource
```

## Verify

```bash
# 2.1 — The 2 changedetection services are up
docker ps --format "{{.Names}}\t{{.Status}}" | grep -E "^(changedetection|changedetection-db)"
# Expected: changedetection     Up N minutes (healthy)
#           changedetection-db  Up N minutes

# 2.2 — The /health endpoint responds
docker exec changedetection curl -fsS http://localhost:5000/health -o /dev/null -w "%{http_code}\n"
# Expected: 200

# 2.3 — A watch can be added (manual)
# Open https://changedetection.cianfhoghlaim.ie and add a watch
# pointing at https://www.examinations.ie — verify a change
# diff is produced

# 2.4 — The Pangolin public URL responds
bash infrastructure/audit/scripts/probe-public-urls.sh | grep changedetection
# Expected: https://changedetection.cianfhoghlaim.ie  <2xx or 3xx>  <time>  (not 5xx)
```

## Rollback

```bash
# 3.1 — Stop the changedetection stack
cd /etc/komodo/storage/changedetection
docker compose -f compose.yaml -f sidecar.yaml down --remove-orphans
cd -

# 3.2 — Optionally drop the changedetection database
docker exec changedetection-db psql -U changedetection -c "DROP DATABASE changedetection"
# (irreversible)

# 3.3 — Remove the Pangolin private resource
#   → Open https://pangolin.cianfhoghlaim.ie → Sites → changedetection → Resources → delete
```

## Last verified

- 2026-06-15: runbook drafted, no end-to-end deploy executed.
  See `openspec/changes/audit-infrastructure-2026-06-15/proposal.md`
  for why deploy is deferred.
- changedetection is **not in the live container inventory**
  at 2026-06-15. This runbook is the first time it's been
  written down; the deploy brings it online for the first
  time.
- The 4 known blockers from the historical log
  (newt/pangolin version, 3 manual private resources,
  expired `PANGOLIN_API_KEY`, `komodo-locket` production
  credentials) all need fixing before the deploy succeeds.
