# Cross-repo Sync Plan: 2026-07-14-tightly-knit-auth-stack-v1

## Commit 1 — bonneagar repo

- **Branch:** `pick-5b-bonneagar-v5-continuation`
- **Files (16 NEW + 8 EDIT):**
  - `iac/auth-pocketid-admin.ts` (NEW, ~250 LOC)
  - `iac/commands/bootstrap-pocketid-admin.ts` (NEW, ~230 LOC)
  - `stacks/tinyauth/{compose,sidecar,secrets,pangolin,blueprint}.yaml + .env.example + README.md` (NEW, 7 files)
  - `komodo/procedures/deploy-pocket-id-bunchloch.toml` (NEW, ~120 LOC)
  - `komodo/procedures/deploy-tinyauth-bunchloch.toml` (NEW, ~110 LOC)
  - `komodo/procedures/deploy-pocket-id-arm1-oci.toml` (NEW, ~120 LOC)
  - `komodo/stacks/pocket-id-bunchloch.toml` (NEW, hand-curated)
  - `komodo/stacks/tinyauth-bunchloch.toml` (NEW, hand-curated)
  - `iac/commands/bootstrap.ts` (EDIT — restructured into 9 phases)
  - `iac/commands/health.ts` (EDIT — extended from 4-way to 6-way check)
  - `iac/commands/rotate-auth.ts` (EDIT — wired ensureBonsIacClient)
  - `iac/cli.ts` (EDIT — added bootstrap-pocketid-admin case)
  - `package.json` (EDIT — added iac:bootstrap-pocketid-admin script)
  - `komodo/resource-syncs/cross-cutting.toml` (EDIT — added 3 new procedures)
  - `komodo/procedures/server_id_legend.md` (EDIT — added 3 new procedures)

```
git -C kings_college_galway/bonneagar add iac/auth-pocketid-admin.ts iac/commands/bootstrap-pocketid-admin.ts \
  stacks/tinyauth/ komodo/procedures/deploy-pocket-id-bunchloch.toml \
  komodo/procedures/deploy-tinyauth-bunchloch.toml komodo/procedures/deploy-pocket-id-arm1-oci.toml \
  komodo/stacks/pocket-id-bunchloch.toml komodo/stacks/tinyauth-bunchloch.toml \
  iac/commands/bootstrap.ts iac/commands/health.ts iac/commands/rotate-auth.ts \
  iac/cli.ts package.json komodo/resource-syncs/cross-cutting.toml \
  komodo/procedures/server_id_legend.md
git -C kings_college_galway/bonneagar commit -m "feat(iaC): tightly-knit-auth-stack (Pocket ID + Tinyauth integrated)

Implements the 2026-07-14-tightly-knit-auth-stack-v1 openspec change.

WHAT THIS FIXES:
- User's Pocket ID passkeys don't work (DB was empty; this is the
  immediate fix via iac:bootstrap-pocketid-admin which creates a signup
  token + prints a URL the operator opens in a browser)
- Tinyauth crash loop (was missing Locket sidecar; now has the proper
  6-file GOLD_STANDARD stack with Locket)
- The deeper pattern: Pocket ID + Tinyauth drifted outside the IaC
  for months. This change brings them in as first-class systems.

NEW IaC COMMANDS:
- iac:bootstrap-pocketid-admin: creates the first user + bons-iac OIDC
  client via the admin API (only manual step: open the URL in a browser)
- iac:health now does 6-way check (was 4-way): adds pocket-id + tinyauth

NEW 3 KOMODO PROCEDURES:
- deploy-pocket-id-bunchloch (5 stages: preflight → stackup → health →
  probe → finalize)
- deploy-tinyauth-bunchloch (5 stages; fixes the crash loop)
- deploy-pocket-id-arm1-oci (mirrors bunchloch; for the arm1-oci
  migration target per the bons AGENTS.md architecture)

NEW 1 STACK:
- stacks/tinyauth/ (6-file GOLD_STANDARD: compose + sidecar + secrets +
  pangolin + blueprint + .env.example + README; with Locket sidecar
  pattern that prevents the crash loop)

WIRED INTO:
- iac:bootstrap: 9 phases (Pulumi → Infisical → Pocket ID → Auth wiring →
  Pangolin → Komodo → Tinyauth → Newt → all syncs)
- iac:rotate-auth: calls ensureBonsIacClient before the Pangolin
  rotation (ensures the OIDC client exists)
- komodo/resource-syncs/cross-cutting.toml: added 3 new procedures to
  the cross-cutting prereq order

Companion openspec change: 2026-07-14-tightly-knit-auth-stack-v1" 2>&1 | tail -5
git -C kings_college_galway/bonneagar push origin pick-5b-bonneagar-v5-continuation 2>&1 | tail -5
```

## Commit 2 — cianfhoghlaim repo

- **Branch:** `pick-4-biep-v1`
- **Files (4):**
  - `openspec/changes/2026-07-14-tightly-knit-auth-stack-v1/proposal.md` (NEW)
  - `openspec/changes/2026-07-14-tightly-knit-auth-stack-v1/tasks.md` (NEW)
  - `openspec/changes/2026-07-14-tightly-knit-auth-stack-v1/cross-repo-sync.md` (NEW, this file)
  - `openspec/changes/2026-07-14-tightly-knit-auth-stack-v1/specs/agent-platform-cluster/spec.md` (NEW, 1 ADDED Requirement)
  - `openspec/changes/2026-07-14-tightly-knit-auth-stack-v1/specs/infrastructure-stacks/spec.md` (NEW, 1 ADDED Requirement)

```
git add openspec/changes/2026-07-14-tightly-knit-auth-stack-v1/
git commit -m "feat(openspec): tightly-knit-auth-stack v1 (Pocket ID + Tinyauth IaC integration)"
git push origin pick-4-biep-v1
```

## Post-push: archive

```
openspec archive 2026-07-14-tightly-knit-auth-stack-v1 --yes
```
