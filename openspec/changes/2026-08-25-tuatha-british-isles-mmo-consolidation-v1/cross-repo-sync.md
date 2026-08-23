# Cross-Repo Sync Plan

This change touches **two repos**:

1. **`cianfhoghlaim`** (the parent monorepo at
   `/Users/cianmacandeisigh/dev/kings_college_galway/`) — where
   the prior `agents/tuatha/` lived, where the 2 plan files live,
   where the openspec change lives
2. **`tuatha`** (the new independent sub-repo at
   `/Users/cianmacandeisigh/dev/kings_college_galway/tuatha/`,
   soon to be `github.com/cianmacandeisigh/tuatha.git`) — where
   the new British Isles MMO project is built

## Commit order

Per the concurrent-write-safety protocol (per the AGENTS.md):

```bash
# Per task:
git status -- <path/to/file>
git diff -- <path/to/file>
git add <path/to/file>
git commit -m "tuatha-consolidation-v1: <T1.x> <description>"
```

For multi-repo:

```bash
# 1. cianfhoghlaim parent repo (this change's 8 files in priority order)
git add openspec/changes/2026-08-25-tuatha-british-isles-mmo-consolidation-v1/proposal.md
git add openspec/changes/2026-08-25-tuatha-british-isles-mmo-consolidation-v1/tasks.md
git add openspec/changes/2026-08-25-tuatha-british-isles-mmo-consolidation-v1/design.md
git add openspec/changes/2026-08-25-tuatha-british-isles-mmo-consolidation-v1/PHASING.md
git add openspec/changes/2026-08-25-tuatha-british-isles-mmo-consolidation-v1/cross-repo-sync.md
git add tuatha/old/prior_top_level_tuasha/    # the 12 prior items
git add tuatha/old/scattered_agents_tuasha/   # the 63 scattered items
git add tuatha/old/legacy_theming/babylonjs/  # the hard-archived skill
git add agents/agent_registry.py              # the re-routed media_descriptor_agent
git add agents/meaisinfhoghlaim/media_intel/__init__.py  # the back-compat shim
git commit -m "tuatha-consolidation-v1: Step 1 + 2 + openspec change (the 8 files)"

# 2. Push the cianfhoghlaim parent commit
git push origin token-plan-lc-pipeline-2026-08

# 3. Operator initializes the new tuatha git remote
# (operator runs `gh repo create tuatha --private` or similar)
# (the new tuatha repo is created at github.com/cianmacandeisigh/tuatha.git)

# 4. The new tuatha repo is built across 14-18 turns of v2 build
# (each sub-step is a separate commit per the BUILD_PLAN.md)
```

## Branch

- For the cianfhoghlaim parent: `token-plan-lc-pipeline-2026-08`
  (the current branch)
- For the new tuatha: `main` (default branch per the
  `leabharlann` + `bonneagar` pattern)

## Push target

- cianfhoghlaim parent: `origin` →
  `https://github.com/cianfhoghlaim/cianfhoghlaim.git`
- new tuatha: `origin` → `https://github.com/cianmacandeisigh/tuatha.git`
  (operator's action; I cannot initialize a fresh remote from this
  client)

## PR

A single PR for the cianfhoghlaim parent change
(`2026-08-25-tuatha-british-isles-mmo-consolidation-v1`), opened
at the end of v1 build time. A single initial commit for the
new tuatha repo (the Phase 3.19 commit, opened at the end of
v2 build time).

## Out-of-scope repos

- `leabharlann/` (already a separate repo, not touched by this change)
- `bonneagar/` (already a separate repo, not touched by this change)

## CI gate pre-merge (cianfhoghlaim parent)

```bash
openspec validate 2026-08-25-tuatha-british-isles-mmo-consolidation-v1 --strict
openspec validate --all --strict
mise run lint:registry
ruff check
```

## CI gate pre-merge (new tuatha repo, v2 build time)

```bash
openspec validate 2026-08-25-tuatha-british-isles-mmo-consolidation-v1 --strict
openspec validate --all --strict
mise run lint:registry
ruff check tuatha/
```

## Archive gate (post-deploy, cianfhoghlaim parent)

```bash
# After v2 build time completes + the new tuatha repo is pushed
openspec archive 2026-08-25-tuatha-british-isles-mmo-consolidation-v1 --yes
```

## Cross-repo sync convention compliance

Per `openspec/AGENTS.md` § Cross-repo sync convention:

- Two-repo change → this file is included for clarity
- Topo ordering: cianfhoghlaim parent archives first → new tuatha
  repo is built + pushed
- No new branches in leabharlann / bonneagar (not touched by this change)
