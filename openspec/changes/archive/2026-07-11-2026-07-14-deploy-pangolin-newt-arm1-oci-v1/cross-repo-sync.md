# Cross-repo Sync Plan: 2026-07-14-deploy-pangolin-newt-arm1-oci-v1

## Commit 1 — bonneagar repo

- **Branch:** `pick-5b-bonneagar-v5-continuation`
- **Files (2):**
  - `komodo/procedures/deploy-pangolin-newt-arm1-oci.toml` (NEW, ~130 LOC)
  - `komodo/procedures/server_id_legend.md` (EDIT — add the new procedure to the arm1-oci section)

```
git -C kings_college_galway/bonneagar add komodo/procedures/deploy-pangolin-newt-arm1-oci.toml komodo/procedures/server_id_legend.md
git -C kings_college_galway/bonneagar commit -m "feat(komodo): deploy-pangolin-newt-arm1-oci procedure (secondary newt client)"
git -C kings_college_galway/bonneagar push origin pick-5b-bonneagar-v5-continuation
```

## Commit 2 — cianfhoghlaim repo

- **Branch:** `pick-4-biep-v1`
- **Files (4):**
  - `openspec/changes/2026-07-14-deploy-pangolin-newt-arm1-oci-v1/proposal.md` (NEW)
  - `openspec/changes/2026-07-14-deploy-pangolin-newt-arm1-oci-v1/tasks.md` (NEW)
  - `openspec/changes/2026-07-14-deploy-pangolin-newt-arm1-oci-v1/cross-repo-sync.md` (NEW, this file)
  - `openspec/changes/2026-07-14-deploy-pangolin-newt-arm1-oci-v1/specs/agent-platform-cluster/spec.md` (NEW, 1 ADDED Requirement)

```
git add openspec/changes/2026-07-14-deploy-pangolin-newt-arm1-oci-v1/
git commit -m "feat(openspec): deploy-pangolin-newt-arm1-oci v1 (Improvement: arm1-oci newt procedure)"
git push origin pick-4-biep-v1
```

## Post-push: archive

```
openspec archive 2026-07-14-deploy-pangolin-newt-arm1-oci-v1 --yes
```
