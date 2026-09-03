# Cross-repo sync — `2026-08-15-bonneagar-infra-remediation-v2`

> This change touches **2 repos in this monorepo**:
> `bonneagar` (the IaC subdirectory) + `cianfhoghlaim` (the root + the
> specs). The third repo `leabharlann/` is NOT touched (read-only
> consumer).
>
> Per the `2026-07-09-v6-drift-remediation-and-repo-boundary-lockdown-v1`
> openspec change, the IaC tests in `bonneagar/iac/` are a prerequisite
> for the openspec archive. **bonneagar MUST be committed first.**

## Commit order

### Step 1: bonneagar (the IaC subdirectory)

Branch: `2026-08-15-bonneagar-infra-remediation-v2`
Push target: `cliste/kings_college_galway` (the Forgejo origin)

```bash
# From the repo root
git checkout -b 2026-08-15-bonneagar-infra-remediation-v2

# IaC TypeScript (new + modified)
git add bonneagar/iac/load-env.ts                                            # NEW
git add bonneagar/iac/cli.ts                                                  # MODIFIED
git add bonneagar/iac/models/pangolin.ts                                     # MODIFIED
git add bonneagar/iac/clients/pangolin-client.ts                              # MODIFIED
git add bonneagar/iac/commands/bootstrap-pangolin-client.ts                   # NEW
git add bonneagar/iac/commands/sync-clients.ts                                # NEW
git add bonneagar/iac/commands/rotate-auth.ts                                # MODIFIED
git add bonneagar/iac/commands/bootstrap.ts                                   # MODIFIED
git add bonneagar/iac/package.json                                           # MODIFIED

# Stack files (new)
git add bonneagar/stacks/newt-arm1-oci/

# Komodo procedures + resource-sync (new + modified)
git add bonneagar/komodo/procedures/deploy-pangolin-client-arm1-oci.toml
git add bonneagar/komodo/procedures/deploy-pangolin-client-bunchloch.toml
git add bonneagar/komodo/resource-syncs/cross-cutting.toml

# Scripts (modified)
git add scripts/deploy-full.ts
git add scripts/deploy-full.sh

# IaC package.json scripts
git add bonneagar/package.json

git commit -m "feat(iac): pangolin client-mgmt API + 4 new IaC commands + newt-arm1-oci stack + 10-phase deploy:full v2"
git push origin 2026-08-15-bonneagar-infra-remediation-v2
```

### Step 2: cianfhoghlaim (the root + the specs)

Branch: `2026-08-15-bonneagar-infra-remediation-v2` (same)
Push target: `cliste/kings_college_galway` (same — the monorepo)

```bash
# After Step 1 is merged into main
git pull --rebase

# OpenSpec change artifacts
git add openspec/changes/2026-08-15-bonneagar-infra-remediation-v2/

# Drift-doc updates
git add AGENTS.md

git commit -m "docs(specs): 5 ADDED Requirements across 2 specs + drift-doc updates"
git push origin 2026-08-15-bonneagar-infra-remediation-v2
```

## Branch + push targets

| Repo | Branch | Push target | Status |
|:--|:--|:--|:--|
| cianfhoghlaim | `2026-08-15-bonneagar-infra-remediation-v2` | `cliste/kings_college_galway` (Forgejo) | first |
| bonneagar | (subdirectory of cianfhoghlaim; no separate repo) | (same) | first (Step 1) |
| leabharlann | (read-only consumer; not touched) | n/a | n/a |

## Order of operations

1. **bonneagar first** — the IaC tests in `bonneagar/iac/` are a
   prerequisite for the openspec archive per the
   `2026-07-09-v6-drift-remediation-and-repo-boundary-lockdown-v1`
   convention.
2. **cianfhoghlaim second** — the spec deltas + drift-doc updates
   depend on the IaC code being correct.

## Single-repo changes (no cross-repo sync needed)

This change touches BOTH sub-trees of the cianfhoghlaim monorepo
(bonneagar/ + the specs/ root), so the cross-repo-sync.md file is
required per the `## Cross-repo sync convention` rule in
`openspec/AGENTS.md`.
