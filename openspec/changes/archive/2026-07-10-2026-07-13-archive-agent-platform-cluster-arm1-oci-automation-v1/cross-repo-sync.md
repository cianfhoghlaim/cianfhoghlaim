# Cross-repo Sync Plan: 2026-07-13-archive-agent-platform-cluster-arm1-oci-automation-v1

## Commit 1 — bonneagar repo

- **Branch:** `pick-5b-bonneagar-v5-continuation`
- **File:** `komodo/procedures/archive-agent-platform-cluster-arm1-oci.toml` (NEW, ~85 lines)

```
git -C kings_college_galway/bonneagar add komodo/procedures/archive-agent-platform-cluster-arm1-oci.toml
git -C kings_college_galway/bonneagar commit -m "feat(komodo): auto-archive procedure for agent-platform-cluster-arm1-oci"
git -C kings_college_galway/bonneagar push origin pick-5b-bonneagar-v5-continuation
```

## Commit 2 — cianfhoghlaim repo

- **Branch:** `pick-4-biep-v1`
- **Files:** `openspec/changes/2026-07-13-archive-agent-platform-cluster-arm1-oci-automation-v1/` (NEW, 4 files)

```
git add openspec/changes/2026-07-13-archive-agent-platform-cluster-arm1-oci-automation-v1/
git commit -m "feat(openspec): archive automation procedure v1 (Improvement 5)"
git push origin pick-4-biep-v1
```

## Post-push: archive

```
openspec archive 2026-07-13-archive-agent-platform-cluster-arm1-oci-automation-v1 --yes
```