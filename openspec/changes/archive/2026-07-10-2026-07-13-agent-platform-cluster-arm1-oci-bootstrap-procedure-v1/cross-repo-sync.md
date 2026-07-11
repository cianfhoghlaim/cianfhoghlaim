# Cross-repo Sync Plan: 2026-07-13-agent-platform-cluster-arm1-oci-bootstrap-procedure-v1

## Commit 1 — bonneagar repo

- **Branch:** `pick-5b-bonneagar-v5-continuation`
- **Remote:** `bonneagar`
- **File:** `komodo/procedures/agent-platform-cluster-arm1-oci-bootstrap.toml` (NEW, ~140 lines)

```
git -C kings_college_galway/bonneagar add komodo/procedures/agent-platform-cluster-arm1-oci-bootstrap.toml
git -C kings_college_galway/bonneagar commit -m "feat(komodo): one-shot bootstrap procedure for agent-platform-cluster-arm1-oci"
git -C kings_college_galway/bonneagar push origin pick-5b-bonneagar-v5-continuation
```

## Commit 2 — cianfhoghlaim repo

- **Branch:** `pick-4-biep-v1`
- **Remote:** `origin`
- **Files:** `openspec/changes/2026-07-13-agent-platform-cluster-arm1-oci-bootstrap-procedure-v1/` (NEW, 4 files)

```
git add openspec/changes/2026-07-13-agent-platform-cluster-arm1-oci-bootstrap-procedure-v1/
git commit -m "feat(openspec): agent-platform-cluster-arm1-oci bootstrap procedure v1 (Improvement 4)"
git push origin pick-4-biep-v1
```

## Post-push: archive

```
openspec archive 2026-07-13-agent-platform-cluster-arm1-oci-bootstrap-procedure-v1 --yes
```