# Cross-repo Sync Plan: 2026-07-14-deploy-newt-bunchloch-v2-with-iac-sync-v1

## Commit 1 — bonneagar repo

- **Branch:** `pick-5b-bonneagar-v5-continuation`
- **Files (2):**
  - `komodo/procedures/deploy-newt-bunchloch-v2.toml` (NEW, ~150 LOC)
  - `komodo/procedures/server_id_legend.md` (EDIT — add v2 entry, mark v1 as legacy)

```
git -C kings_college_galway/bonneagar add komodo/procedures/deploy-newt-bunchloch-v2.toml komodo/procedures/server_id_legend.md
git -C kings_college_galway/bonneagar commit -m "feat(komodo): deploy-newt-bunchloch-v2 — iac-integrated + v1.14.0 assertion"
git -C kings_college_galway/bonneagar push origin pick-5b-bonneagar-v5-continuation
```

## Commit 2 — cianfhoghlaim repo

- **Branch:** `pick-4-biep-v1`
- **Files (4):**
  - `openspec/changes/2026-07-14-deploy-newt-bunchloch-v2-with-iac-sync-v1/proposal.md` (NEW)
  - `openspec/changes/2026-07-14-deploy-newt-bunchloch-v2-with-iac-sync-v1/tasks.md` (NEW)
  - `openspec/changes/2026-07-14-deploy-newt-bunchloch-v2-with-iac-sync-v1/cross-repo-sync.md` (NEW, this file)
  - `openspec/changes/2026-07-14-deploy-newt-bunchloch-v2-with-iac-sync-v1/specs/agent-platform-cluster/spec.md` (NEW, 1 ADDED Requirement)

```
git add openspec/changes/2026-07-14-deploy-newt-bunchloch-v2-with-iac-sync-v1/
git commit -m "feat(openspec): deploy-newt-bunchloch-v2 with iac sync v1 (Improvement: bunchloch newt procedure)"
git push origin pick-4-biep-v1
```

## Post-push: archive

```
openspec archive 2026-07-14-deploy-newt-bunchloch-v2-with-iac-sync-v1 --yes
```
