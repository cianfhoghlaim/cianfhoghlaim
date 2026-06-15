# Runbook: n8n

> Written for a future AI agent. Every snippet is shell-
> pasteable. **Do not auto-execute** — the agent must paste
> each snippet deliberately.

n8n is the workflow-automation platform, deployed on
`bunchloch` per `infrastructure/komodo/stacks/team-workflow.toml`
and exposed at `n8n.cianfhoghlaim.ie` via Pangolin. The 6
seeded `workflows/team-*.json` workflows use the
`OPENCODE_GO_API` LLM backbone.

## Pre-flight

```bash
# 0.1 — Verify ssh + docker
command -v ssh    || { echo "ERROR: ssh not installed";    exit 1; }
command -v docker || { echo "ERROR: docker not installed"; exit 1; }

# 0.2 — Verify the 6 seeded workflows are present
ls infrastructure/stacks/engineering/n8n/workflows/ 2>/dev/null \
  | grep -c "team-" \
  | { read count; [ "$count" -ge 6 ] || { echo "ERROR: only $count team-*.json workflows found (need >= 6)"; exit 2; }; }

# 0.3 — Verify the secrets are in the vault
infisical environments list --project-id "$INFISICAL_PROJECT_ID" \
  | grep -q dev-baile \
  || { echo "ERROR: dev-baile env not found"; exit 3; }
for secret in N8N_ENCRYPTION_KEY N8N_USER_MANAGEMENT_JWT_SECRET \
              N8N_DB_POSTGRESDB_PASSWORD OPENCODE_GO_API_KEY; do
  infisical secrets get "$secret" --project-id "$INFISICAL_PROJECT_ID" --env dev-baile --path /n8n 2>/dev/null \
    || { echo "WARN: $secret not in /n8n; provision it"; }
done

# 0.4 — Verify the init/ scripts (the n8n-init one-shot container)
ls infrastructure/stacks/engineering/n8n/init/ 2>/dev/null \
  || { echo "ERROR: n8n init/ dir missing"; exit 4; }
```

## First-time deploy

```bash
# 1.1 — Create the run_directory on bunchloch
mkdir -p /etc/komodo/storage/n8n

# 1.2 — rsync the 6 GOLD_STANDARD files + the 6 seeded workflows
rsync -avz --delete \
  infrastructure/stacks/engineering/n8n/{compose.yaml,sidecar.yaml,secrets.env,blueprint.yaml,README.md} \
  /etc/komodo/storage/n8n/
rsync -avz --delete infrastructure/stacks/engineering/n8n/workflows/ \
  /etc/komodo/storage/n8n/workflows/
rsync -avz --delete infrastructure/stacks/engineering/n8n/init/ \
  /etc/komodo/storage/n8n/init/

# 1.3 — Bring up the n8n stack
cd /etc/komodo/storage/n8n
docker compose -f compose.yaml -f sidecar.yaml up -d
docker compose -f compose.yaml -f sidecar.yaml ps
cd -

# 1.4 — Run the n8n-init one-shot container (imports the 6 workflows)
docker compose -f /etc/komodo/storage/n8n/compose.yaml \
  run --rm n8n-init

# 1.5 — Register the Pangolin private resource
```

## Verify

```bash
# 2.1 — The 2 n8n services are up
docker ps --format "{{.Names}}\t{{.Status}}" | grep -E "^(n8n|n8n-db)"
# Expected: n8n      Up N minutes (healthy)
#           n8n-db   Up N minutes

# 2.2 — The /healthz endpoint responds
docker exec n8n curl -fsS http://localhost:5678/healthz -o /dev/null -w "%{http_code}\n"
# Expected: 200

# 2.3 — The 6 workflows imported
docker exec n8n n8n list:workflow 2>/dev/null | grep -c "team-" \
  | { read count; [ "$count" -ge 6 ] || { echo "WARN: only $count team-* workflows visible"; }; }
# Expected: 6+

# 2.4 — A workflow using the OpenCode Go LLM works (manual)
# Open https://n8n.cianfhoghlaim.ie → open one of the team-*
# workflows → click "Execute Workflow" → check the LLM step
# returns a non-empty response

# 2.5 — The Pangolin public URL responds
bash infrastructure/audit/scripts/probe-public-urls.sh | grep n8n
# Expected: https://n8n.cianfhoghlaim.ie  <2xx or 3xx>  <time>  (not 5xx)
```

## Rollback

```bash
# 3.1 — Stop the n8n stack
cd /etc/komodo/storage/n8n
docker compose -f compose.yaml -f sidecar.yaml down --remove-orphans
cd -

# 3.2 — Optionally drop the n8n database
docker exec n8n-db psql -U n8n -c "DROP DATABASE n8n"
# (irreversible — the next deploy will need a fresh import of the
#  6 team-*.json workflows via the n8n-init one-shot container)

# 3.3 — Remove the Pangolin private resource
#   → Open https://pangolin.cianfhoghlaim.ie → Sites → n8n → Resources → delete
```

## Last verified

- 2026-06-15: runbook drafted, no end-to-end deploy executed.
  See `openspec/changes/audit-infrastructure-2026-06-15/proposal.md`
  for why deploy is deferred.
- n8n is **not in the live container inventory** at
  2026-06-15. This runbook is the first time it's been
  written down; the deploy brings it online for the first
  time.
- The 4 known blockers from the historical log
  (newt/pangolin version, 3 manual private resources,
  expired `PANGOLIN_API_KEY`, `komodo-locket` production
  credentials) all need fixing before the deploy succeeds.
