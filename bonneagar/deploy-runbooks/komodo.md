# Runbook: komodo

> Written for a future AI agent. Every snippet is shell-
> pasteable. **Do not auto-execute** — the agent must paste
> each snippet deliberately.

## Pre-flight

```bash
# 0.1 — Verify docker + the infisical vault
command -v docker || { echo "ERROR: docker not installed"; exit 1; }
docker info >/dev/null 2>&1 || { echo "ERROR: docker daemon not reachable"; exit 2; }
infisical environments list --project-id "$INFISICAL_PROJECT_ID" \
  | grep -q dev-baile \
  || { echo "ERROR: dev-baile env not found"; exit 3; }

# 0.2 — Verify the komodo client lib is installed
node -e "require('komodo_client')" 2>/dev/null \
  || { echo "ERROR: komodo_client npm package not installed; run: bun add komodo_client"; exit 4; }

# 0.3 — Verify the komodo API key + secret are fresh
#       (see HEALTH_REPORT.md Session 3, blocker #3)
[ -n "$KOMODO_API_KEY" ] || { echo "ERROR: KOMODO_API_KEY not set"; exit 5; }
[ -n "$KOMODO_API_SECRET" ] || { echo "ERROR: KOMODO_API_SECRET not set"; exit 5; }
```

## First-time deploy

```bash
# 1.1 — Decide where Komodo Core lives
#       Per `infrastructure/AGENTS.md`, the MacBook (`bunchloch`)
#       is the Core. The Oracle box (`arm1-oci`) is a Periphery.
#       This runbook deploys the Core on `bunchloch` + the
#       OCI Periphery on `arm1-oci`.

# 1.2 — Snapshot the existing state on the target hosts
bash infrastructure/audit/scripts/inventory-bunchloch.sh
bash infrastructure/audit/scripts/inventory-arm1-oci.sh

# 1.3 — Create the run_directory on both hosts
ssh arm1-oci 'mkdir -p /etc/komodo/storage/komodo /etc/komodo/storage/komodo-periphery'
mkdir -p /etc/komodo/storage/komodo /etc/komodo/storage/komodo-periphery

# 1.4 — rsync the compose + sidecar files
#       (Komodo Core on bunchloch uses the local compose)
rsync -avz \
  infrastructure/komodo/compose.yaml \
  infrastructure/komodo/sidecar.yaml \
  arm1-oci:/etc/komodo/storage/komodo/

# 1.5 — Add the Infisical machine identity for /komodo
INFISICAL_PROJECT_ID=$(grep -E '^INFISICAL_PROJECT_ID' .env | cut -d= -f2)
infisical machine-identities create "komodo" \
  --project-id "$INFISICAL_PROJECT_ID" --env dev-baile \
  --role "/komodo" 2>/dev/null \
  || echo "WARN: machine identity 'komodo' may already exist"
infisical machine-identities token "komodo" \
  --project-id "$INFISICAL_PROJECT_ID" --env dev-baile \
  --path /komodo --ttl-seconds 0 2>/dev/null \
  > /tmp/komodo-infisical-token \
  || { echo "ERROR: could not get komodo machine identity token"; exit 6; }
KOMODO_INFISICAL_TOKEN=$(cat /tmp/komodo-infisical-token)
# Save to .env as INFISICAL_CLIENT_ID=... and INFISICAL_CLIENT_SECRET=...

# 1.6 — Write the komodo Core compose on bunchloch
#       (uses the existing infrastructure/komodo/stacks/komodo.toml;
#        this is multi-stack, so we just verify it's registered)
grep -q '\[\[stack\]\]' infrastructure/komodo/stacks/komodo.toml \
  || { echo "ERROR: infrastructure/komodo/stacks/komodo.toml missing"; exit 7; }

# 1.7 — Add the Periphery agent for arm1-oci
cat >> infrastructure/komodo/stacks/komodo.toml <<'KOMODO_EOF'

[[stack]]
name = "komodo-periphery-oci"
description = "Komodo Periphery agent for OCI workloads"
tags = ["host:arm1-oci", "tier:control-plane", "type:agent"]
[stack.config]
server_id = "arm1-oci"
run_directory = "/etc/komodo/storage/komodo-periphery"
file_paths = ["compose.yaml", "sidecar.yaml"]
KOMODO_EOF

# 1.8 — Commit + push + trigger Komodo resource sync
git add infrastructure/komodo/stacks/komodo.toml
git -c user.email=agent@cianfhoghlaim.ie \
    -c user.name="opencode agent" \
    commit -m "feat(komodo): register OCI periphery"
git push

# 1.9 — Deploy the Core (local on bunchloch)
cd /etc/komodo/storage/komodo
docker compose -f compose.yaml -f sidecar.yaml up -d
docker compose -f compose.yaml -f sidecar.yaml ps
cd -
```

## Verify

```bash
# 2.1 — Core is up on bunchloch
docker ps | grep komodo-core
# Expected: komodo-core   Up N minutes (healthy)
#           komodo-postgres   Up N minutes
#           komodo-ferretdb   Up N minutes
#           komodo-locket     Up N minutes

# 2.2 — Core's web UI responds
curl -I http://localhost:9120/
# Expected: HTTP 200

# 2.3 — Periphery is registered to the Core
node -e "
  import('komodo_client').then(async ({ KomodoClient }) => {
    const c = new KomodoClient({
      url: 'https://komodo.cianfhoghlaim.ie',
      key: process.env.KOMODO_API_KEY,
      secret: process.env.KOMODO_API_SECRET,
    });
    const servers = await c.listServers();
    console.log(servers);
  });
"
# Expected: includes 'arm1-oci' and 'bunchloch'

# 2.4 — The Locket sidecar is healthy
docker ps | grep komodo-locket
docker inspect --format='{{.State.Health.Status}}' komodo-locket
# Expected: healthy
```

## Rollback

```bash
# 3.1 — Stop the Periphery on arm1-oci
ssh arm1-oci 'cd /etc/komodo/storage/komodo-periphery && docker compose -f compose.yaml -f sidecar.yaml down --remove-orphans'

# 3.2 — Stop the Core on bunchloch
cd /etc/komodo/storage/komodo
docker compose -f compose.yaml -f sidecar.yaml down --remove-orphans
cd -

# 3.3 — Optionally remove the Periphery entry
node -e "
  import('komodo_client').then(async ({ KomodoClient }) => {
    const c = new KomodoClient({
      url: 'https://komodo.cianfhoghlaim.ie',
      key: process.env.KOMODO_API_KEY,
      secret: process.env.KOMODO_API_SECRET,
    });
    await c.removeStack({ stack: 'komodo-periphery-oci' });
  });
"

# 3.4 — Optionally delete the Infisical machine identity
#        (this is irreversible — the next deploy will need a new one)
infisical machine-identities delete "komodo" \
  --project-id "$INFISICAL_PROJECT_ID" --env dev-baile
```

## Last verified

- 2026-06-15: runbook drafted, no end-to-end deploy executed.
  See `openspec/changes/audit-infrastructure-2026-06-15/proposal.md`
  for why deploy is deferred.
- The Komodo Core has been running on `bunchloch` since
  Session 1 (Komodo FerretDB swap, HEALTH_REPORT.md Session 1).
  The Periphery on `arm1-oci` is the new piece; it exists
  per `infrastructure/komodo/stacks/komodo.toml` but the
  production wiring of the agent's outbound tunnel to the
  Core was the Session 1 fix.
