# Change: 2026-07-09-v6-drift-remediation-and-repo-boundary-lockdown-v1

## Why

Across 2026-07-06 → 2026-07-09, 7 active openspec changes were
authored in parallel by 5 separate opencode sessions. The drift
that accumulated is now substantial enough that downstream agents
are misrouting writes (data-platform writes that should go to
bonneagar/iac/, frontend-apps writes that should reference
`infrastructure/stacks/` paths but instead reference
`sruth/oideachais/...` which no longer exist post-v4
consolidation, agent-platform deploys that broke the opencode
instance because no pre-flight gate exists).

The drift falls into 4 categories:

1. **Repo boundary drift.** The 3-repo split
   (`cianfhoghlaim/` data+apps, `bonneagar/` IaC+stacks,
   `leabharlann/` corpus) was established by the
   `2026-06-28-consolidate-sruth-into-cianfhoghlaim-v4` change
   but the `infrastructure/stacks/` directory in cianfhoghlaim
   only contains the `motherduck/` sidecar (dives + flights
   metadata). All 88 real Compose stacks live in
   `bonneagar/stacks/`. Multiple agents writing into
   `infrastructure/stacks/<name>/` accidentally created stale
   paths. The `infrastructure-gold-standard-compliance-v1`
   change tried to enforce the boundary but its tasks were
   committed (30/30 ticked) without the actual work being
   applied — 5 placeholder dirs
   (`backend/`, `platform-service/`, `runner/`, `workers/`,
   `x2text-service/`) still exist, the stack counts drift
   between root AGENTS.md (94), bonneagar AGENTS.md (88/86), and
   actual (97 dirs), and `iac:bootstrap` is not exposed at the
   repo root.

2. **Path drift in root AGENTS.md.** Lines 275 and 280 still
   reference `sruth/oideachais/data_platform` and
   `sruth/oideachais/notebooks` — paths that no longer exist
   post-v4 consolidation (should be `cianfhoghlaim/dlt/` and
   `cianfhoghlaim/notebooks/`). Line 280 also references
   `infrastructure/stacks/{engineering/n8n,tools/vikunja,...}/`
   but the engineering/tools subdirs live in bonneagar.

3. **Stack count drift.** Three different counts in three
   different files (94 / 88 / 86 / 97) confuse every agent.

4. **Missing safety gates.** Repeatedly deploying arm-oci core
   stacks (`openchamber`, `backrest`, `olm-arm1-oci`) from
   opencode sessions that may share a process namespace with
   the deployed container has broken the opencode instance
   itself. There is no pre-flight check that:
   (a) verifies the opencode PID is isolated from the target
       container's namespace,
   (b) verifies Pangolin + Komodo + Infisical are healthy
       before the deploy begins,
   (c) shows a dry-run diff before committing the change.

This remediation change lands 4 things:

1. **The 2-repo boundary convention** (cianfhoghlaim + bonneagar)
   with explicit ownership lists and the new
   `cross-repo-sync.md` file convention for openspec changes
   that touch both.
2. **Root AGENTS.md + bonneagar AGENTS.md** rewrite to fix all
   3 stack-count drifts, the `sruth/oideachais/...` paths, the
   1Password/SOPS reference, and to add 3 new top-level sections
   (Repo Boundary / OpenSpec Change Management / OpenCode Safety).
3. **The `preflight:arm-oci` script** at the repo root that
   enforces the deploy pre-conditions (Pangolin + Komodo +
   Infisical health + process namespace isolation + dry-run).
4. **Drift remediation** that finishes the work the
   `infrastructure-gold-standard-compliance-v1` change claimed
   to have done but did not actually do (5-deletion in
   bonneagar, count-references everywhere, iac:bootstrap
   exposure, generator scripts).

The 4 archive-now changes (#2, #4, #5, #7) are validated and
archived in Wave 1 before this change is implemented, so the
remaining work is sequenced cleanly. Changes #3 and #1 are
finished via the tasks.md of this change (they share the same
dependency: Brown Ajah component cleanup is part of #3 which
is a prerequisite for #1 finishing the `*web surfaces for the
6 subjects` acceptance criterion).

## Dependencies

`Blocked by: none` (this is the consolidation change — the
archive-now changes in Wave 1 happen first, then this change
implements, then #3 and #1 are finished).

`Blocked by (soft): 2026-07-09-infrastructure-gold-standard-compliance-v1`
— this change EXTENDS the gold-standard change's spec delta
rather than forking it; the gold-standard change should be
archived simultaneously (the tasks.md Phase 1-3 work is
re-stated here for clarity).

`Affected repos: cianfhoghlaim, bonneagar` (see `cross-repo-sync.md`).

## What changes

### A. New conventions

| File | Status | Purpose |
|:--|:--|:--|
| `openspec/changes/<id>/cross-repo-sync.md` | NEW (per-change) | Lists the commits needed in cianfhoghlaim + bonneagar + leabharlann for changes that touch >1 repo |
| `openspec/changes/<id>/proposal.md` `## Dependencies` section | NEW (per-change) | Lists `Blocked by: <change-id>` edges for topo ordering |
| `openspec/AGENTS.md` | MODIFIED | Add a "Cross-repo sync" + "Dependencies" section |
| `openspec/specs/infrastructure-stacks-documentation/spec.md` | MODIFIED | Add 3 ADDED Requirements: Repo Boundary, OpenSpec Change Management, OpenCode Safety |

### B. New safety script

| File | Status | Purpose |
|:--|:--|:--|
| `scripts/preflight-arm-oci.ts` | NEW | Bun script that runs the 4 pre-flight checks + emits a dry-run diff |
| `package.json` `preflight:arm-oci` script | NEW | `bun run scripts/preflight-arm-oci.ts` |
| `package.json` `iac:bootstrap` script | NEW | `bun run --cwd bonneagar iac:bootstrap` (exposes IaC at root) |

### C. Drift remediation (the work #6 claimed to do)

| File | Edit | Reason |
|:--|:--|:--|
| `bonneagar/stacks/{backend,platform-service,runner,workers,x2text-service}/` | DELETE | 5 placeholder dirs (1-line `compose.yaml` stubs) |
| `AGENTS.md` (root) | EDIT 3 lines | "94 stacks" → "87 stacks" (3 hits) |
| `AGENTS.md` (root) | EDIT lines 275, 280 | `sruth/oideachais/...` → `cianfhoghlaim/...` |
| `AGENTS.md` (root) | EDIT line 280 | Remove `engineering/n8n,tools/vikunja,tools/cal-diy/` reference (lives in bonneagar) |
| `AGENTS.md` (root) | NEW sections | Add `## Repo Boundary` + `## OpenSpec Change Management` + `## OpenCode Safety` |
| `bonneagar/AGENTS.md` | EDIT 8 lines | "88 / 86 stacks" → "87 stacks" (8 hits) |
| `bonneagar/AGENTS.md` | NEW section | Add `## IaC Repo Boundary` |
| `bonneagar/GOLD_STANDARD.md` | EDIT 3 hits | "94 stacks" → "87 stacks" |
| `bonneagar/package.json` | EDIT | "88-stack" → "87-stack" |
| `bonneagar/stacks/README.md` | EDIT | "93/94 stacks" → "87 stacks" |
| `bonneagar/deploy-runbooks/bunchloch-bootstrap.md` | EDIT | "86-stack" → "87-stack" |
| `docs/stacks/README.md` | EDIT | "88 stacks" → "87 stacks" |
| `openspec/specs/{dlthub-platform-integration,documentation,agent-platform-cluster,bonneagar-iac-merge,bonneagar-komodo-gitops,infrastructure-stacks-documentation,infrastructure-stacks}/spec.md` | EDIT | "91/88/86 stacks" → "87 stacks" |

### D. Spec deltas (5 MODIFIED + 0 ADDED — see `specs/`)

- `specs/infrastructure-stacks/spec.md` — MODIFIED Requirement
  "Selfhosted stack inventory" + ADDED Requirement "Drift-remediation pass"
- `specs/bonneagar-iac-merge/spec.md` — ADDED Requirement
  "Cross-repo sync convention" + ADDED Requirement "iac:bootstrap at root"
- `specs/bonneagar-komodo-gitops/spec.md` — ADDED Requirement
  "Pre-flight gate before resource-sync apply"
- `specs/infrastructure-stacks-documentation/spec.md` — ADDED
  Requirement "Repo boundary documented in root AGENTS.md"
- `specs/indexing-and-cognition/spec.md` — MODIFIED Requirement
  "CCC search excludes archived openspec" (clarify `openspec/changes/archive/` exclusion)

### E. Cross-repo sync

The drift remediation touches 2 repos:
- **cianfhoghlaim** — openspec change files, root `AGENTS.md`,
  `scripts/preflight-arm-oci.ts`, `package.json` scripts,
  4 spec files (the cianfhoghlaim-side ones)
- **bonneagar** — `AGENTS.md`, `GOLD_STANDARD.md`,
  `package.json`, `stacks/README.md`, `deploy-runbooks/bunchloch-bootstrap.md`,
  5 placeholder dir deletions, 3 spec files (the bonneagar-side ones)

The full cross-repo commit plan is in
`openspec/changes/2026-07-09-v6-drift-remediation-and-repo-boundary-lockdown-v1/cross-repo-sync.md`.

## What does NOT change

- The 5 active openspec changes still being worked on
  (this remediation change is *parallel* to them — they
  continue in Waves 1-3)
- `infrastructure/stacks/motherduck/` (correctly stays in
  cianfhoghlaim — it's the MotherDuck Dives/Flights metadata
  sidecar, not a Compose stack)
- The 3 separate git remotes (`origin` = cianfhoghlaim,
  `bonneagar` = bonneagar, `leabharlann` = leabharlann)
- The shared `.git/` directory between worktrees (intentional —
  it's how the 3 repos coexist as worktrees of one git dir)
- `docs/PHASE_0.3_DEPLOY_RUNBOOK.md` (out of scope — owned by
  the `infrastructure` subagent engagement)

## Files (N created + M edited)

See `tasks.md` for the full file-by-file list.

## Acceptance

- `openspec validate 2026-07-09-v6-drift-remediation-and-repo-boundary-lockdown-v1 --strict` passes
- `ccc search "94 stacks" | grep AGENTS.md` returns 0 hits (in both repos)
- `ccc search "88 stacks" | grep bonneagar/AGENTS.md` returns 0 hits
- `ccc search "86 stacks" | grep bonneagar/AGENTS.md` returns 0 hits
- `ls -d bonneagar/stacks/*/` returns exactly 87 (5 pruned)
- `bun run preflight:arm-oci` exits 0 from a clean opencode session
- `bun run preflight:arm-oci` exits 1 with clear error when Pangolin is unreachable
- `bun run preflight:arm-oci` exits 1 with clear error when the opencode PID is in the same namespace as a running openchamber container
- `bun run iac:bootstrap --dry-run` exits 0 and prints the diff
- `mise run lint:skills` still passes (53/53)
- The 4 archive-now changes are validated + archived before this change lands
- The cross-repo-sync.md file lists every commit hash + branch needed in bonneagar

## Cross-references

- Related archive: `openspec/changes/archive/2026-06-28-consolidate-sruth-into-cianfhoghlaim-v4/`
- Related active: `2026-07-09-infrastructure-gold-standard-compliance-v1` (extended by this change)
- Related active: `2026-07-09-biep-6-subject-web-surfaces-v1` (Brown Ajah component cleanup)
- Related active: `2026-07-06-british-isles-education-pipeline-v1` (Wave 3 finish)
- Related skills: `infrastructure-stacks`, `openspec`, `komodo`, `pangolin`, `infisical`, `secrets-management`