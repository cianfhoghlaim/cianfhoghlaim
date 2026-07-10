# Cross-repo Sync Plan: 2026-07-13-arm-oci-deploy-preflight-hard-gate-v1

This change touches both repos. The commit order is **bonneagar first**,
then **cianfhoghlaim** (the IaC tests in bonneagar are a prerequisite for
the cianfhoghlaim openspec archive).

## Commit 1 — bonneagar repo

- **Branch:** `pick-5b-bonneagar-v5-continuation`
- **Remote:** `bonneagar` (https://github.com/cianfhoghlaim/bonneagar.git)
- **Push target:** `origin pick-5b-bonneagar-v5-continuation`
- **File:** `komodo/procedures/deploy-agent-platform-cluster-arm1-oci.toml`
- **Change:** Stage 0 preflight RunShellCommand now has
  `require_success = true` + the report is captured to a versioned
  `/tmp/preflight-reports/arm-oci/<utc-ts>.md` path.

```
git -C kings_college_galway/bonneagar add komodo/procedures/deploy-agent-platform-cluster-arm1-oci.toml
git -C kings_college_galway/bonneagar commit -m "fix(komodo): hard-gate preflight:arm-oci with require_success=true + versioned report path"
git -C kings_college_galway/bonneagar push origin pick-5b-bonneagar-v5-continuation
```

## Commit 2 — cianfhoghlaim repo

- **Branch:** `pick-4-biep-v1`
- **Remote:** `origin` (https://github.com/cianfhoghlaim/cianfhoghlaim.git)
- **Push target:** `origin pick-4-biep-v1`
- **Files:**
  - `openspec/changes/2026-07-13-arm-oci-deploy-preflight-hard-gate-v1/proposal.md` (NEW)
  - `openspec/changes/2026-07-13-arm-oci-deploy-preflight-hard-gate-v1/tasks.md` (NEW)
  - `openspec/changes/2026-07-13-arm-oci-deploy-preflight-hard-gate-v1/cross-repo-sync.md` (NEW, this file)
  - `openspec/changes/2026-07-13-arm-oci-deploy-preflight-hard-gate-v1/specs/infrastructure-stacks/spec.md` (NEW, 1 ADDED Requirement)

```
git add openspec/changes/2026-07-13-arm-oci-deploy-preflight-hard-gate-v1/
git commit -m "feat(openspec): arm-oci deploy preflight hard-gate v1 (Improvement 3)"
git push origin pick-4-biep-v1
```

## Post-push: archive

After both pushes succeed:

```
openspec archive 2026-07-13-arm-oci-deploy-preflight-hard-gate-v1 --yes
```