# Cross-repo Sync Plan: 2026-07-14-bump-newt-v1.14.0-cross-cluster-v1

## Commit 1 — bonneagar repo

- **Branch:** `pick-5b-bonneagar-v5-continuation`
- **Files (3):**
  - `stacks/newt/IMAGE` (NEW)
  - `stacks/newt/docker-compose.yaml` (EDIT — image line)
  - `stacks/pangolin/newt.yaml` (EDIT — image line)

```
git -C kings_college_galway/bonneagar add stacks/newt/IMAGE stacks/newt/docker-compose.yaml stacks/pangolin/newt.yaml
git -C kings_college_galway/bonneagar commit -m "fix(komodo): bump newt 1.13.0 → 1.14.0 + SHA digest across clusters"
git -C kings_college_galway/bonneagar push origin pick-5b-bonneagar-v5-continuation
```

## Commit 2 — cianfhoghlaim repo

- **Branch:** `pick-4-biep-v1`
- **Files (4):**
  - `openspec/changes/2026-07-14-bump-newt-v1.14.0-cross-cluster-v1/proposal.md` (NEW)
  - `openspec/changes/2026-07-14-bump-newt-v1.14.0-cross-cluster-v1/tasks.md` (NEW)
  - `openspec/changes/2026-07-14-bump-newt-v1.14.0-cross-cluster-v1/cross-repo-sync.md` (NEW, this file)
  - `openspec/changes/2026-07-14-bump-newt-v1.14.0-cross-cluster-v1/specs/infrastructure-stacks/spec.md` (NEW, 1 ADDED Requirement)

```
git add openspec/changes/2026-07-14-bump-newt-v1.14.0-cross-cluster-v1/
git commit -m "feat(openspec): bump newt v1.14.0 cross-cluster v1 (Improvement: cross-cluster image pin)"
git push origin pick-4-biep-v1
```

## Post-push: archive

```
openspec archive 2026-07-14-bump-newt-v1.14.0-cross-cluster-v1 --yes
```
