# Change: infrastructure-stack-doctor-v1

## Why

Round 7 of the multi-quadrant refactor plan. Per the
`infrastructure/` subagent's deep-dive report (2026-06-24):

- **93 stacks** in `infrastructure/stacks/` (per
  `infrastructure/AGENTS.md`; the README says 94)
- **88 compose.yaml + 86 sidecar.yaml + 88 blueprint.yaml + 91 secrets.env**
  present, but **23/93 stacks are missing `.env.example`** and
  **6/93 stacks are missing `pangolin.yaml`**
- The `infrastructure/legacy/` directory has 5 `.ts` files
  (~88KB) that are already replaced by `infrastructure/iac/komodo/*.ts`
- The 4 quadrants (meaisinfhoghlaim, tuatha, croilar, plus the
  in-flight oideachais-agent-services) keep deploy files
  (`compose.yaml`, `sidecar.yaml`, `pangolin.yaml`) inside the
  quadrant directory — these are anti-patterns; the canonical
  home is `infrastructure/stacks/<quadrant>/`
- The `infrastructure/GOLD_STANDARD.md` describes a 4-gate
  `stack-doctor` CI check, but the gates aren't formally codified
  in any spec Requirement
- 3 new skills are landing in this round: `kcg-pangolin-stack`,
  `kcg-locket-sidecar`, `kcg-infrastructure-audit` (598 lines
  combined)

The change formalises the 4-gate `stack-doctor` and the 3 host
tags + the image-pinning policy + the Locket 3-mode contract as
canonical Requirements on `infrastructure-stacks`.

## What Changes

### 1. `infrastructure-stacks` spec (MODIFIED + ADDED)

1 MODIFIED Requirement ("Stack Standardization") + 1 ADDED
Requirement ("Stack-Doctor CI Gate") that codify the 4-gate
`bun run stack-doctor` + the 3 host tags + the image-pinning
policy.

### 2. 5 supporting MODIFIED Requirements (batched into the same
openspec change)

- **Image Pinning Policy** — every `image:` line in
  `infrastructure/stacks/<name>/compose.yaml` SHALL be pinned to
  `<major>.<minor>.<patch>` (no `:latest`); local-build images with
  `pull_policy: never` are exempt and MUST include an inline
  comment
- **Locket Sidecar Contract** — every `sidecar.yaml` SHALL use the
  `user: "65532:65532"` + `no-new-privileges:true` + `cap_drop: [ALL]`
  + `read_only: true` + `tmpfs: [/run/secrets/locket:size=1m,mode=0700]`
  security baseline; the `cianfhoghlaim_locket_secrets` external
  tmpfs volume SHALL be shared across all 86+ stacks
- **Locket 3-Mode Contract** — every `sidecar.yaml` SHALL declare
  `LOCKET_MODE` as one of `watch` / `exec` / `oneshot`; the
  `watch` mode is the default for long-running services
- **Host Tag Mandatory** — every `infrastructure/komodo/stacks/<name>.toml`
  SHALL declare exactly one `host:*` tag from
  `{host:bunchloch, host:arm1-oci, host:cax41-hetzner}` (or be a
  reference stack with no tag)
- **Pangolin 6-Label Pattern** — every `pangolin.yaml` SHALL follow
  the 6-label shape (`name`, `mode`, `full-domain`,
  `destination-port`, `protocol`, `roles[0]`); the 4 common
  Traefik middlewares are `tinyauth@file`, `secure-headers@file`,
  `rate-limit-api@file`, `rate-limit-auth@file`

### 3. Refactor: 4 quadrant deploy quartets → `infrastructure/stacks/<quadrant>/`

- Move `sruth/meaisinfhoghlaim/{compose.yaml, sidecar.yaml, blueprint.yaml, secrets.env}` → `infrastructure/stacks/meaisinfoghlaim/` (4 files, ~120 LOC)
- Move `sruth/tuatha/{pangolin.yaml, docker-compose.yaml, compose.dev.yaml}` → `infrastructure/stacks/sruth/tuatha/` (3 files, ~250 LOC)
- Move `sruth/croilar/{compose.yaml, compose.dev.yaml, sidecar.yaml, secrets.env, Dockerfile.dagster}` → `infrastructure/stacks/sruth/croilar/` (5 files, ~250 LOC)
- All moves preserve the originals as thin re-export shims (per the established 6-phase refactor pattern)

### 4. Refactor: delete 5 legacy `.ts` files

The `infrastructure/legacy/` directory has 5 `.ts` files
(`ansible.ts`, `cloudflare-dns.ts`, `pangolin-setup.ts`,
`servers.ts`, `taisce-deploy.ts`) totalling ~88KB. These are
already replaced by `infrastructure/iac/komodo/*.ts` (per the
`legacy/README.md` itself). Delete them and keep only
`LOCKET-MODES.md` + `ANALYSIS.md` (the documentation).

### 5. Refactor: delete 5 deferred deploy runbooks

`infrastructure/deploy-runbooks/{cal-diy,vikunja,n8n,changedetection,bytebase}.md`
are deferred (not in the live container inventory at 2026-06-15).
Delete them; keep the 4 active runbooks (`infisical`, `komodo`,
`pangolin`, `ansible`).

### 6. 3 new skills land

- `.agents/skills/kcg-pangolin-stack/SKILL.md` (155 lines)
- `.agents/skills/kcg-locket-sidecar/SKILL.md` (201 lines)
- `.agents/skills/kcg-infrastructure-audit/SKILL.md` (242 lines)

### 7. 7 doc updates (1-line diffs each)

- `infrastructure/AGENTS.md` — add the 7th bullet (image pinning) to the Standard Stack Structure
- `infrastructure/README.md` — update stack count to 93
- `infrastructure/GOLD_STANDARD.md` — add the forbidden `:latest` rule
- `infrastructure/audit/README.md` — add the 5th quick-start step (`stack-doctor`)
- `infrastructure/komodo/README.md` — mark the 5 legacy `.ts` files as `STATUS: scheduled-for-deletion-2026-07`
- `infrastructure/stacks/README.md` — update count
- `openspec/specs/infrastructure-stacks/spec.md` — append the new "Image Pinning Policy" Requirement

## Impact

- Affected specs: `infrastructure-stacks` (1 MODIFIED + 1 ADDED + 5 supporting MODIFIED Requirements)
- Affected skills: 3 new (kcg-pangolin-stack, kcg-locket-sidecar, kcg-infrastructure-audit)
- Affected code:
  - 3 quadrant deploy quartets → 3 new `infrastructure/stacks/<quadrant>/` dirs (12 files moved, 3 thin shims)
  - 5 legacy `.ts` files deleted (88KB)
  - 5 deferred deploy runbooks deleted
- Net change: +598 lines of skill content, -88KB of legacy, ~620 lines of deploy-quartet consolidation, ~3,000 lines of stale runbook removal
- 1 commit + 1 archive commit per the established pattern

## Success criteria

- `openspec validate infrastructure-stack-doctor-v1 --strict` passes
- 3 new skills exist with valid frontmatter
- 4 quadrant deploy quartets consolidated to `infrastructure/stacks/`
- 5 legacy `.ts` files deleted (or marked as deleted with a git history note)
- 5 deferred runbooks removed (or marked `STATUS: deferred` with a `README.md` pointer)
- `bun run stack-doctor` runs and reports clean for the 4 stacks that were moved
- 1 commit + 1 archive commit land on `q3-2026-oideachais-consolidation`
