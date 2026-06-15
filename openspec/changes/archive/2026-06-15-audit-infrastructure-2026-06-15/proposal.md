# Audit Infrastructure 2026-06-15

## Why

The Cianfhoghlaim monorepo has 4 workspace-member quadrants
(`oideachais/`, `tuatha/`, `croilar/`, `meaisinfhoghlaim/`) and 74
Docker Compose stacks under `infrastructure/stacks/`. As of
2026-06-15, the most recent infrastructure health report
(`infrastructure/stacks/HEALTH_REPORT.md`) is 3 days old and
documents 4 unresolved blockers (newt/pangolin version mismatch,
3 manually-created private resources, 2 expired
`PANGOLIN_API_KEY`s, `komodo-locket` missing production
credentials).

We have:

- 35 running containers on `bunchloch` (MacBook M4, primary
  workloads), 47h uptime
- ~10 containers on `arm1-oci` (Oracle Cloud ARM, control
  plane)
- A Komodo orchestrator with 29 stack TOMLs, 56 procedure
  TOMLs, 2 servers, 2 sites
- 9 specific deploy targets the operator has named for an
  end-to-end test: 4 control-plane (`infisical`, `komodo`,
  `pangolin`, `ansible`) + 5 private-resources (`cal-diy`,
  `vikunja`, `n8n`, `changedetection`, `bytebase`)
- A static `HEALTH_REPORT.md` but no scripts to regenerate it

This change is an **audit + documentation** change, not a
deploy. The actual deploy of the 9 user-named stacks is
deferred to a follow-up change that consumes the runbooks
written here.

## What Changes

### Phase A — Live container audit infrastructure (deferred, but written)

Add 4 shell scripts under `infrastructure/audit/scripts/`:
- `inventory-bunchloch.sh` — captures live `docker ps` + `docker stats` + `docker network ls` to JSON
- `inventory-arm1-oci.sh` — same, but `ssh arm1-oci '...'` wrappers
- `diff-against-composes.sh` — diffs live `docker ps` against the filesystem `infrastructure/stacks/**/compose.yaml` to find orphans, missing services, port conflicts
- `probe-public-urls.sh` — for each `*.cianfhoghlaim.ie` in `infrastructure/pangolin/a2a-resources.blueprint.yaml`, `curl -I -L` and report 200/3xx/4xx/5xx

Plus `infrastructure/audit/inventory/.gitkeep` and
`infrastructure/audit/README.md`.

### Phase B — Quadrant README updates

Add a **Status** section near the top and a **Known issues**
section near the bottom of each quadrant README:
- `oideachais/README.md` (637 lines existing)
- `tuatha/README.md` (794 lines existing)
- `croilar/README.md` (794 lines existing)
- `meaisinfhoghlaim/README.md` (497 lines existing)
- Root `README.md` — Status column added to the Quadrant table

### Phase C — Infrastructure docs

- **NEW** `infrastructure/DEPLOYMENT-STRATEGY.md` (200–300 lines, canonical playbook)
- **UPDATE** `infrastructure/GOLD_STANDARD.md` (add stack-doctor CI gate section)
- **MOVE** `infrastructure/stacks/HEALTH_REPORT.md` historical 3-session log → `infrastructure/archive/HEALTH_REPORT-2026-06-12.md`
- **REWRITE** `infrastructure/stacks/HEALTH_REPORT.md` (Session 4 entry pointing back to the archive)
- **NEW** `infrastructure/QUADRANT-TO-STACK-MAP.md` (1-page table)
- **UPDATE** `docs/06-infrastructure/` pointer

### Phase D — 9 deployment runbooks (for a future AI agent)

Write 9 `infrastructure/deploy-runbooks/<name>.md` files. Each
is shell-snippet copy-pastable, no prose, with diagnostic
checks at every step:

| Runbook | Stack |
|:--|:--|
| `infisical.md` | `infrastructure/infisical/` |
| `komodo.md` | `infrastructure/komodo/` |
| `pangolin.md` | `infrastructure/pangolin/` |
| `ansible.md` | `infrastructure/ansible/` |
| `cal-diy.md` | `infrastructure/stacks/tools/cal-diy/` |
| `vikunja.md` | `infrastructure/stacks/tools/vikunja/` |
| `n8n.md` | `infrastructure/stacks/engineering/n8n/` |
| `changedetection.md` | `infrastructure/stacks/tools/changedetection/` |
| `bytebase.md` | `infrastructure/stacks/engineering/bytebase/` |

### Phase E — OpenSpec archive

After the 4 phases land, this change is archived with
`openspec archive audit-infrastructure-2026-06-15 --yes`,
adding 2 new requirements to `infrastructure-stacks`:

- **Stack Audit Scripts** — every container is reachable via the 4 audit scripts
- **Deployment Runbook** — every user-named deploy target has a runbook under `infrastructure/deploy-runbooks/`

## Impact

- **None of the 4 quadrants change code** (only READMEs)
- **None of the 9 deploy targets get touched** (only runbooks written)
- **No new dependencies** (scripts use `docker`, `ssh`, `jq`, `curl` — all already available)
- **No secrets inlined** (scripts call `infisical export` if a secret is needed)
- **OpenSpec change adds 2 requirements** to `infrastructure-stacks`

## Non-Goals

- No actual deploy of the 9 user-named stacks (runbooks are deferred content)
- No `komodo_client` API calls
- No `ssh arm1-oci` writes
- No Infisical vault writes
- No Pangolin private-resource creation
- No Locket sidecar boots
- No new external scraping
- No new docker compose deploys

## Per-Phase Build Order

| # | Phase | What ships | Files touched |
|--:|:--|:--|:--|
| 1 | A | 4 audit scripts + audit/README.md + inventory/.gitkeep | 6 new files |
| 2 | B | 5 README Status / Known-issues updates | 5 files (4 + root) |
| 3 | C | 1 new strategy doc + 1 archive move + 1 rewrite + 1 new map + 1 update | 5 files (3 new, 2 existing) |
| 4 | D | 9 deployment runbooks | 9 new files |
| 5 | E | OpenSpec archive | 1 archive command |

## Risks

1. **HEALTH_REPORT.md move is irreversible** — once the 3-session log is moved to `infrastructure/archive/HEALTH_REPORT-2026-06-12.md`, future agents reading the live file won't see it. Mitigation: keep a single back-link at the top of the archive file.
2. **README updates may be overwritten** if a later agent edits the same quadrants and discards the Status / Known-issues sections. Mitigation: link the sections to the issue tracker so reverts are noisy.
3. **Runbooks become stale** if Komodo / Pangolin / Infisical release new versions. Mitigation: each runbook ends with a "Last verified" date and a pointer to the relevant upstream release notes.
4. **`openspec validate --strict` may flag the spec deltas** as `MODIFIED` instead of `ADDED` (the issue we hit during `lateralise-british-isles-domains`). Mitigation: write the spec deltas with `## ADDED Requirements` from the start.
