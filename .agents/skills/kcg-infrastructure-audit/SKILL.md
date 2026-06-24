---
name: kcg-infrastructure-audit
description: Run the Cianfhoghlaim live container audit (4 shell scripts under `infrastructure/audit/scripts/`) and diagnose the bitwise-OR exit codes. Covers the 4 scripts (inventory-bunchloch.sh, inventory-arm1-oci.sh, diff-against-composes.sh, probe-public-urls.sh), the JSON snapshot schema (`containers[]` + `networks[]` + `volumes[]` + `host_info`), the 7 exit codes (0=clean, 1=orphan, 2=missing, 3=conflict, 4=combo, 1=missing-tool, 2=unreachable, 3=no-docker), the `infrastructure/audit/inventory/<host>-<UTC>.json` filename convention, the cross-link to `infrastructure/stacks/HEALTH_REPORT.md` and `infrastructure/stacks/README.md`, and the 4-gate `stack-doctor` CI check. Use when answering "is the cluster healthy?", debugging a missing container, or running the weekly audit cron.
---

# KCG Infrastructure Audit

## Purpose

The KCG platform is a fleet of 86+ Docker Compose stacks across 3
hosts (`bunchloch`, `arm1-oci`, `cax41-hetzner`). The audit surface
consists of 4 shell scripts that:

1. **Inventory** each host's containers, networks, and volumes
2. **Diff** the live inventory against the per-stack `compose.yaml`
3. **Probe** the public `*.cianfhoghlaim.ie` URLs
4. **Stack-doctor** validate the 6-file GOLD_STANDARD for every stack

This skill captures the script anatomy, the exit code contract,
the JSON snapshot schema, and the diagnostic workflow.

## When to use this skill

Use when you need to:

- "Is the cluster healthy?"
- "Why is `*.cianfhoghlaim.ie` returning 502?"
- "Run the weekly audit cron"
- "Diff the live containers against the compose files"
- "Find orphan containers (running, but no compose file)"
- "Find missing containers (in compose, but not running)"
- "Probe the public URLs"

## The 4 scripts (the audit surface)

### 1. `inventory-bunchloch.sh` (the M4 MacBook host)

```bash
#!/usr/bin/env bash
# infrastructure/audit/scripts/inventory-bunchloch.sh
set -euo pipefail
HOST=bunchloch
UTC=$(date -u +%Y%m%dT%H%M%SZ)
OUT_DIR="$(dirname "$0")/../inventory"
mkdir -p "$OUT_DIR"

docker ps --format json > "$OUT_DIR/$HOST-containers.jsonl"
docker network ls --format json > "$OUT_DIR/$HOST-networks.jsonl"
docker volume ls --format json > "$OUT_DIR/$HOST-volumes.jsonl"

# Bundle into a single snapshot
jq -s '{
  host: "bunchloch",
  utc: "'$UTC'",
  host_info: {hostname: "'$(hostname)'", kernel: "'$(uname -r)'", docker: "'$(docker --version)'"},
  containers: .[0],
  networks: .[1],
  volumes: .[2]
}' "$OUT_DIR/$HOST-containers.jsonl" "$OUT_DIR/$HOST-networks.jsonl" "$OUT_DIR/$HOST-volumes.jsonl" \
  > "$OUT_DIR/$HOST-$UTC.json"
```

The script writes:
- `infrastructure/audit/inventory/bunchloch-20260624T120000Z.json` (the
  canonical snapshot)
- `infrastructure/audit/inventory/bunchloch-containers.jsonl` (the
  raw line-delimited JSON for `jq` piping)

### 2. `inventory-arm1-oci.sh` (the OCI arm control plane)

Same shape as `inventory-bunchloch.sh` but with `HOST=arm1-oci` and
the script runs over SSH:

```bash
ssh arm1-oci "docker ps --format json" > "$OUT_DIR/arm1-oci-containers.jsonl"
```

### 3. `diff-against-composes.sh` (the bitwise-OR exit code contract)

```bash
#!/usr/bin/env bash
# infrastructure/audit/scripts/diff-against-composes.sh
set -uo pipefail   # NOTE: not -e (we use the exit code as the diff signal)
EXIT=0

for compose in infrastructure/stacks/*/compose.yaml; do
  STACK=$(basename "$(dirname "$compose")")
  CONTAINERS=$(yq '.services | keys | .[]' "$compose" 2>/dev/null)
  for container in $CONTAINERS; do
    if ! docker ps --format '{{.Names}}' | grep -q "^${container}$"; then
      echo "MISSING: $STACK/$container" >&2
      EXIT=$((EXIT | 2))   # bit 1 = missing
    fi
  done
done

LIVE=$(docker ps --format '{{.Names}}')
for container in $LIVE; do
  if ! grep -rq "container_name: $container" infrastructure/stacks/*/compose.yaml; then
    echo "ORPHAN: $container" >&2
    EXIT=$((EXIT | 1))   # bit 0 = orphan
  fi
done

# bit 2 = conflict (same container_name in 2 compose files)
# bit 4 = combo (missing + orphan in same stack)

exit $EXIT
```

### 4. `probe-public-urls.sh` (the URL probe)

```bash
#!/usr/bin/env bash
# infrastructure/audit/scripts/probe-public-urls.sh
set -uo pipefail
EXIT=0

for url in $(yq '.pangolin.private-resources | to_entries | .[] | .value.full-domain' infrastructure/stacks/*/pangolin.yaml 2>/dev/null); do
  STATUS=$(curl -sk -o /dev/null -w '%{http_code}' "https://$url/health" || echo "unreachable")
  if [[ "$STATUS" != "200" ]]; then
    echo "PROBE FAIL: $url -> $STATUS" >&2
    EXIT=$((EXIT | 2))   # bit 1 = unreachable
  fi
done

exit $EXIT
```

## The 7 exit codes (the bitwise-OR contract)

| Code | Bit | Meaning | When |
|:-:|--:|:--|:--|
| 0 | — | Clean | No orphan, no missing, no conflict, all URLs return 200 |
| 1 | 0 | Orphan | A container is running but no `compose.yaml` declares it |
| 2 | 1 | Missing | A `compose.yaml` declares a container but it's not running |
| 3 | 0+1 | Orphan + Missing | Both above (most common "drift" state) |
| 4 | 2 | Conflict | Two `compose.yaml` files declare the same `container_name:` |
| 8 | 3 | Unreachable | A public URL returns non-200 |
| 16 | 4 | Combo | Missing + orphan + conflict in the same stack (the worst state) |
| 1 (different) | — | Missing tool | `docker`, `jq`, `yq`, or `ssh` not on PATH |
| 2 (different) | — | Unreachable host | SSH to `arm1-oci` or `cax41-hetzner` times out |
| 3 (different) | — | No docker | The host doesn't have a Docker daemon |

The script exits with the bitwise-OR of all the bits that fired; the
caller (cron or `bun run stack-doctor`) reads the exit code and
generates the per-week `HEALTH_REPORT.md` delta.

## The JSON snapshot schema

```json
{
  "host": "bunchloch",
  "utc": "2026-06-24T12:00:00Z",
  "host_info": {
    "hostname": "bunchloch.local",
    "kernel": "24.4.0",
    "docker": "Docker version 27.0.3, build 7d4bcd8"
  },
  "containers": [
    {"Names": "locket", "Image": "ghcr.io/cianfhoghlaim/locket:1.0.0", "State": "running", ...}
  ],
  "networks": [
    {"Name": "cianchoghlaim_locket_secrets", "Driver": "local"}
  ],
  "volumes": [
    {"Name": "cianchoghlaim_locket_secrets", "Driver": "local"}
  ]
}
```

The snapshots are stored in `infrastructure/audit/inventory/` with
the filename convention `<host>-<UTC>.json` (e.g.
`bunchloch-20260624T120000Z.json`).

## The 4-gate `stack-doctor` (the CI check)

`bun run stack-doctor` (from `infrastructure/GOLD_STANDARD.md`)
runs 4 gates on every stack:

1. **File gate** — every `infrastructure/stacks/<name>/compose.yaml` has the other 5 GOLD_STANDARD files
2. **Container gate** — every `container_name:` is in the live inventory OR explicitly documented as stacked-only
3. **Secret gate** — every `secrets.env` URI resolves in the Infisical vault
4. **Pangolin gate** — every `pangolin.yaml` parses against the official schema

The script's exit code is the bitwise-OR of the 4 gate failures (1, 2, 4, 8).

## Worked example: weekly audit cron

```bash
#!/usr/bin/env bash
# /etc/cron.weekly/kcg-audit
set -uo pipefail
REPO=/Users/cianmacandeisigh/dev/kings_college_galway
cd "$REPO"

# 1. Inventory each host
./infrastructure/audit/scripts/inventory-bunchloch.sh
./infrastructure/audit/scripts/inventory-arm1-oci.sh
./infrastructure/audit/scripts/inventory-cax41-hetzner.sh

# 2. Diff against the compose files
./infrastructure/audit/scripts/diff-against-composes.sh
DIFF_EXIT=$?

# 3. Probe the public URLs
./infrastructure/audit/scripts/probe-public-urls.sh
PROBE_EXIT=$?

# 4. Stack-doctor
bun run stack-doctor
DOCTOR_EXIT=$?

# 5. Generate the report
if [[ $((DIFF_EXIT | PROBE_EXIT | DOCTOR_EXIT)) -ne 0 ]]; then
  mise run locket:exec -- \
    python -c "
      from oideachais.cognee_integration.cross_stage_cognify import emit_alert
      emit_alert('infra-audit', $((DIFF_EXIT | PROBE_EXIT | DOCTOR_EXIT)))
    "
fi
```

## Common failure modes

| Symptom | Cause | Fix |
|:--|:--|:--|
| `diff-against-composes.sh: exit 3 (orphan + missing)` | A container was added to a compose file but never deployed, OR a container was manually started but never declared | `docker compose up -d <service>` OR `docker compose stop <orphan>` |
| `diff-against-composes.sh: exit 4 (conflict)` | Two compose files use the same `container_name:` | Rename one of them |
| `probe-public-urls.sh: exit 8` | A Pangolin route is misconfigured OR the container is down | Check the per-stack `pangolin.yaml` + the Komodo stack status |
| `inventory-bunchloch.sh: "Cannot connect to Docker daemon"` | The Docker Desktop app is not running | Start Docker Desktop |
| `inventory-arm1-oci.sh: "ssh: connect to host arm1-oci port 22: Connection refused"` | The OCI instance is down OR the SSH key is missing | Check the OCI console + `ssh-add ~/.ssh/oci` |

## Cross-references

- `.agents/skills/stack-ops/SKILL.md` — the 6-file GOLD_STANDARD + `stack-doctor` rules
- `.agents/skills/kcg-bunchloch/SKILL.md` — the 3-host topology (where the audit runs)
- `.agents/skills/kcg-convergence/SKILL.md` — the 94-stack layout
- `.agents/skills/secrets-management/SKILL.md` — the vault URI contract (used by gate 3)
- `infrastructure/audit/README.md` — the 78-line audit README
- `infrastructure/GOLD_STANDARD.md` — the 320-line 6-file pattern + 4-gate `stack-doctor` rules
- `infrastructure/stacks/HEALTH_REPORT.md` — the live cluster health report
