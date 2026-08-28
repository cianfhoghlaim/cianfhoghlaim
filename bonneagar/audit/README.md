# bonneagar/audit — Live Container Audit Scripts

> **Provenance (2026-08-28).** This tree was restored from the standalone
> `github.com/cianfhoghlaim/bonneagar` repo, where it was orphaned by the
> 2026-07-17 v7 flatten — it was the only content on that remote with no
> counterpart in the monorepo. Two caveats before you use it:
>
> - **Paths in this document use the legacy `infrastructure/` layout**, which
>   is now `bonneagar/`. Read `infrastructure/x` as `bonneagar/x` throughout.
> - `scripts/stack-doctor.sh` already uses `bonneagar/`-prefixed paths and
>   runs correctly from the monorepo root. The other three scripts still
>   reference `infrastructure/` internally and need their paths updated
>   before they will run. `scripts/stack-doctor.sh` is also distinct from
>   the root `scripts/stack-doctor.sh` (368 lines, GOLD_STANDARD auditor);
>   this one is the 7-gate v5 CI check, and is 6 weeks stale — its Gate 1
>   currently trips on `bonneagar/stacks/unsloth-serve/`, which is
>   intentionally README-only since the unsloth-v5 change.

These scripts are the dynamic counterpart to
`infrastructure/stacks/HEALTH_REPORT.md` (last refreshed
2026-06-12, 3 sessions of fixes documented). The static
report is what an agent *knows* about the 2-host topology; the
4 scripts below are how an agent *verifies* it on demand.

## Scripts

| Script | What it captures | When to run |
|:--|:--|:--|
| `scripts/inventory-bunchloch.sh` | Live `docker ps` + `docker stats` + `docker network ls` + `docker volume ls` to JSON | After any container start/stop, before any audit |
| `scripts/inventory-arm1-oci.sh` | Same shape, over `ssh arm1-oci` | Same as above, but the arm1-oci host |
| `scripts/diff-against-composes.sh` | Compares 2 inventory JSONs against the filesystem `infrastructure/stacks/**/compose.yaml` files. Surfaces orphans, missing services, port conflicts | After both inventory scripts have run |
| `scripts/probe-public-urls.sh` | For each `full-domain` in `infrastructure/pangolin/a2a-resources.blueprint.yaml`, issues `curl -L --max-time 10` and reports status + time | Before any deploy that touches the public Pangolin routable |

## Quick-start

```bash
# 1. Snapshot the local host
bash infrastructure/audit/scripts/inventory-bunchloch.sh

# 2. Snapshot arm1-oci (requires passwordless SSH)
bash infrastructure/audit/scripts/inventory-arm1-oci.sh

# 3. Diff the two snapshots against the filesystem composes
bash infrastructure/audit/scripts/diff-against-composes.sh

# 4. Probe the public URLs
bash infrastructure/audit/scripts/probe-public-urls.sh
```

Each step writes a JSON snapshot to
`infrastructure/audit/inventory/<host>-<UTC>.json`. The
snapshots are committed to git (they're small — ~10–100 KB
each).

## Exit codes

| Script | Code | Meaning |
|:--|:--|:--|
| `inventory-*.sh` | 0 | Snapshot written |
|  | 1 | Required tool missing (docker / ssh / jq) |
|  | 2 | Host unreachable |
|  | 3 | Remote has no docker daemon |
| `diff-against-composes.sh` | 0 | No orphans, no missing, no conflicts |
|  | 1 | At least one orphan |
|  | 2 | At least one missing service |
|  | 3 | At least one port conflict |
|  | 4 | Combination (bitwise OR of 1/2/3) |
| `probe-public-urls.sh` | 0 | All 2xx/3xx/4xx |
|  | 1 | At least one 5xx |
|  | 2 | At least one URL unreachable |
|  | 4 | Blueprint not parseable |

## Security

The inventory JSONs include `labels` (which often contain
Infisical project IDs) and `mounts` (which may leak volume
paths). They do NOT include environment variables or secrets.

If a future agent needs to commit an inventory to a public
repo, run `jq 'del(.containers[].labels, .containers[].mounts)'
inventory-bunchloch-20260615T120000Z.json` first.

## CI gate

The 4-gate `bun run stack-doctor` CI check (file gate + container
gate + secret gate + Pangolin gate) runs on every PR and posts
the diff/probe output as a GitHub PR comment. See
`infrastructure/GOLD_STANDARD.md` for the gate definitions and
`openspec/specs/infrastructure-stacks/spec.md` (added in
`infrastructure-stack-doctor-v1`, archived 2026-06-24) for the
formal Requirement. The 4-gate script also runs on-demand via
`./infrastructure/audit/scripts/inventory-bunchloch.sh` +
`./infrastructure/audit/scripts/diff-against-composes.sh` +
`./infrastructure/audit/scripts/probe-public-urls.sh`.

## Relation to the openspec change

This tree was created by
`openspec/changes/audit-infrastructure-2026-06-15/`. The 4
scripts implement the **Stack Audit Scripts** requirement
added to `infrastructure-stacks` spec.
