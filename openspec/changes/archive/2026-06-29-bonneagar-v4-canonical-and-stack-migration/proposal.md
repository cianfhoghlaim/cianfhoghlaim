# Change: 2026-06-29-bonneagar-v4-canonical-and-stack-migration

## Why

The Cianfhoghlaim monorepo has three coexisting stack locations
that are drifting apart:

1. `bonneagar/stacks/` — **88 stacks** (the v0 → v4 canonical
   location, the GitOps home)
2. `infrastructure/stacks/ci/hf-watchdog/` — **1 stack** (a new
   v4 attempt from the parallel
   `2026-06-29-fix-ocr-vlm-registry-with-unsloth-priority` change)
3. `cianfhoghlaim/stacks/` — **41 entries** (35 duplicate stacks
   + 2 cianfhoghlaim-only stacks + 4 non-stacks)

This drift is dangerous because:

- The IaC TypeScript client at `bonneagar/iac/komodo/` is
  configured to look at `bonneagar/stacks/` only. The
  `infrastructure/` and `cianfhoghlaim/stacks/` locations are
  invisible to the IaC and will never be deployed.
- The `infrastructure/AGENTS.md` (created today by a parallel
  sub-agent) duplicates the canonical stack inventory that's
  already in `bonneagar/AGENTS.md`.
- The Python watchdog code at
  `infrastructure/stacks/ci/hf-watchdog/watchdog.py` is bundled
  inside a stack dir, violating the design principle that
  **`cianfhoghlaim/` = code, `bonneagar/` = ops**.
- The 35 duplicate stacks in `cianfhoghlaim/stacks/` will drift
  out of sync with their canonical twins in `bonneagar/stacks/`
  (one will be updated, the other won't).
- The IaC `package.json` is nested at
  `bonneagar/iac/komodo/package.json` — awkward to discover
  when `bonneagar/` is its own repository.

This change brings the v4 reality into a single canonical
location:

- **All stacks** live at `bonneagar/stacks/<name>/` (the
  6-file GOLD_STANDARD).
- **All code** (e.g. `watchdog.py`) lives at
  `cianfhoghlaim/ci/hf_watchdog.py` (or wherever the Python
  module belongs).
- **All ops** (Dockerfile, compose, blueprint, sidecar,
  secrets.env, pangolin.yaml, .env.example) lives at
  `bonneagar/stacks/<name>/`.
- **The IaC `package.json`** is hoisted to the root of
  `bonneagar/`, ready for the future split into its own GitHub
  repo (`github.com/cianfhoghlaim/bonneagar`).
- **Per-stack docs** live at
  `cianfhoghlaim/docs/stacks/<name>.md` with a 4-section
  template: (1) purpose for the project, (2) why it stays in
  the komodo/pangolin/infisical GitOps, (3) cross-reference to
  the ops dir, (4) cross-reference to any code.

Dagger image-building is **explicitly out of scope** for this
change (per the user's direction). A future change will
introduce a shared `kcg/base:latest` base image that bundles
the cianfhoghlaim package.

## What Changes

### 1. Migrate `infrastructure/stacks/ci/hf-watchdog/` → `bonneagar/stacks/ci/hf-watchdog/`

The 1 stack from the `2026-06-29-fix-ocr-vlm-registry-with-unsloth-priority`
change moves to the canonical location:

- 3 ops files (`blueprint.yaml`, `compose.yaml`, `Dockerfile`)
  → `bonneagar/stacks/ci/hf-watchdog/`
- 1 code file (`watchdog.py`) → `cianfhoghlaim/ci/hf_watchdog.py`
- The Dockerfile is rewritten as a multi-stage build that
  `COPY --from=ghcr.io/cianfhoghlaim/cianfhoghlaim:dev /app/ci/hf_watchdog.py /app/`
- 4 missing GOLD_STANDARD files are added (`sidecar.yaml`,
  `secrets.env`, `pangolin.yaml`, `.env.example`)
- 1 new vault ref to `.infisical.env`
  (`infisical://dev-baile/ci/hf-watchdog/slack_webhook_url`)
- 1 new doc at `cianfhoghlaim/docs/stacks/ci/hf-watchdog.md`
- The stack is registered in
  `bonneagar/iac/komodo/deploy-stacks.ts` with tag
  `host:bunchloch` + `tier:ci` + `project:cianfhoghlaim`

### 2. Migrate the 2 cianfhoghlaim-only stacks → `bonneagar/stacks/`

`browser` and `llama-swap` exist only in `cianfhoghlaim/stacks/`.
Both are full 6-file GOLD_STANDARD. Both move to
`bonneagar/stacks/<name>/` and are registered in the IaC.

### 3. Move the 4 non-stack files → `cianfhoghlaim/assets/_oideachais_dagster_defs/`

The 4 files `oideachais_dagster.yaml`, `oideachais_Dockerfile`,
`oideachais_Dockerfile.adk`, `oideachais_Dockerfile.dagster`
are dockerfiles + a dagster code-location yaml, not stacks.
They move to `cianfhoghlaim/assets/_oideachais_dagster_defs/`
(where the dagster build pipeline already lives).

### 4. Delete the 35 duplicate stacks from `cianfhoghlaim/stacks/`

The 35 stacks that exist in BOTH `cianfhoghlaim/stacks/` and
`bonneagar/stacks/` are deleted from the cianfhoghlaim copy.
The canonical twins in `bonneagar/stacks/` are unchanged.
The 3 cloud-managed duplicates (`planetscale`, `r2`,
`motherduck`) are flagged for a future change to delete the
bonneagar copies (the user said these don't need to be
self-hosted).

### 5. Delete the v4-canonical `infrastructure/` dir

The `infrastructure/` dir at the repo root was created today by
a parallel sub-agent. It duplicates the canonical stack
inventory. After this change:

- The `infrastructure/AGENTS.md` content moves to
  `bonneagar/AGENTS.md` (the 5-group model + the 94-stack
  inventory + the IaC pointers)
- The `infrastructure/stacks/ci/hf-watchdog/` moves to
  `bonneagar/stacks/ci/hf-watchdog/` (per §1)
- The `infrastructure/` dir is deleted
- The 7 docs in `bonneagar/` are updated to remove all
  references to `infrastructure/`
- The `scripts/stack-doctor.sh` is updated to point at
  `bonneagar/stacks/` only

### 6. Hoist the IaC `package.json` to the root of `bonneagar/`

The IaC TypeScript client at `bonneagar/iac/komodo/` has its
own `package.json`, `tsconfig.json`, and `bun.lock`. These
are hoisted to the root of `bonneagar/`:

- `bonneagar/package.json` (NEW at the root) — the IaC's
  manifest + 4 alias scripts (`iac:deploy-stacks`,
  `iac:create-resources`, `iac:read-state`, `iac:bootstrap`)
- `bonneagar/tsconfig.json` (NEW at the root)
- `bonneagar/bun.lock` (moved from `iac/komodo/`)
- The 5 IaC scripts (`config.ts`, `komodo-rpc.ts`,
  `deploy-stacks.ts`, `create-resources.ts`, `read-state.ts`)
  stay at `iac/komodo/` but reference the root
  `package.json` via relative imports

This prepares `bonneagar/` for the future split into its own
GitHub repo (per the user's "bonneagar is its own repository"
direction).

### 7. Document all 88 stacks in `cianfhoghlaim/docs/stacks/`

A new `infrastructure-stacks-documentation` capability is
introduced. The contract: every stack in `bonneagar/stacks/`
MUST have a corresponding `cianfhoghlaim/docs/stacks/<name>.md`
doc with a 4-section template:

1. **Purpose for the Cianfhoghlaim project** — what this stack
   does for us (2-3 sentences)
2. **Why it stays in komodo/pangolin/infisical GitOps** — the
   operational requirement (2-3 sentences)
3. **Cross-references** — to the ops dir at
   `bonneagar/stacks/<name>/`, to the code (if any), to the
   IaC entry, to the Pangolin domain
4. **Tags** — `host:bunchloch` / `host:arm1-oci` /
   `tier:infrastructure` / `tier:data-plane` / etc.

The CI gate (`stack-doctor --json`) is updated to fail if any
stack in `bonneagar/stacks/` is missing its doc.

### 8. Update openspec

- `infrastructure-stacks` (MODIFIED) — new canonical home
  (`bonneagar/stacks/`), the 5-group model, the per-stack doc
  requirement, the `infrastructure/` removal
- `data-engineering-pipeline-documentation` (MODIFIED) — the 4
  canonical ops dirs after the migration
- `indexing-and-cognition` (MODIFIED) — cross-reference the
  IaC at `bonneagar/iac/komodo/`
- `author-archive-pipeline` (MODIFIED) — cross-reference
  `bonneagar/stacks/ci/hf-watchdog/` +
  `cianfhoghlaim/ci/hf_watchdog.py`
- NEW `infrastructure-stacks-documentation` — the contract
  for the per-stack docs

## Impact

### Affected specs (5 total)

- MODIFIED `infrastructure-stacks` — new canonical home +
  5-group model + per-stack doc requirement
- MODIFIED `data-engineering-pipeline-documentation` — 4
  canonical ops dirs
- MODIFIED `indexing-and-cognition` — cross-reference the
  IaC
- MODIFIED `author-archive-pipeline` — cross-reference the
  hf-watchdog migration
- NEW `infrastructure-stacks-documentation` — per-stack doc
  contract

### New files

- `bonneagar/package.json` (NEW at the root — hoisted from
  `iac/komodo/`)
- `bonneagar/tsconfig.json` (NEW at the root)
- `bonneagar/bun.lock` (NEW at the root — moved from
  `iac/komodo/`)
- `bonneagar/stacks/ci/hf-watchdog/` (NEW — 6 files + README)
- `cianfhoghlaim/ci/__init__.py` (NEW)
- `cianfhoghlaim/ci/hf_watchdog.py` (NEW — the Python watchdog)
- `cianfhoghlaim/ci/README.md` (NEW)
- `cianfhoghlaim/docs/stacks/` (NEW dir + 88 docs + README)
- `openspec/specs/infrastructure-stacks-documentation/spec.md`
  (NEW canonical home)
- `openspec/changes/2026-06-29-bonneagar-v4-canonical-and-stack-migration/{proposal.md, tasks.md, specs/<5>/spec.md}`
  (15 files)

### Modified files

- `bonneagar/AGENTS.md` — add the IaC table + the 5-group
  model + the 88-stack inventory
- `bonneagar/README.md` — remove the `infrastructure/stacks/`
  reference
- `bonneagar/DEPLOYMENT-STRATEGY.md` — remove the
  `infrastructure/stacks/` reference
- `bonneagar/GOLD_STANDARD.md` — point at `bonneagar/stacks/`
- `bonneagar/PANGOLIN-SETUP.md` — same
- `bonneagar/SECRETS-MANAGEMENT.md` — same
- `bonneagar/QUADRANT-TO-STACK-MAP.md` — same
- `bonneagar/iac/komodo/deploy-stacks.ts` — register the 3
  new stacks (hf-watchdog, browser, llama-swap)
- `scripts/stack-doctor.sh` — point at `bonneagar/stacks/`
  only + check for the per-stack doc
- `.infisical.env` — +1 vault ref (hf-watchdog Slack
  webhook)
- `openspec/project.md` — +1 capability row
  (`infrastructure-stacks-documentation`)

### Deleted files

- `infrastructure/` (entire dir — 5 files)
- `infrastructure/AGENTS.md` (content moves to
  `bonneagar/AGENTS.md`)
- `infrastructure/stacks/ci/hf-watchdog/{blueprint,compose,Dockerfile}`
  (moved to `bonneagar/stacks/ci/hf-watchdog/`)
- `infrastructure/stacks/ci/hf-watchdog/watchdog.py` (moved to
  `cianfhoghlaim/ci/hf_watchdog.py`)
- 35 duplicate stack dirs in `cianfhoghlaim/stacks/`
  (backrest, cognee, croilar, dagster, docling-serve,
  dots-ocr, dragonfly, falkordb, garage, graphiti, infisical,
  invokeai, komodo, lakehouse, lancedb, langfuse, litellm,
  logfire, mailcow-dockerized, marimo, memgraph, mlflow,
  mlx-omni, motherduck, nimtable, olake, olmocr,
  openchamber, openclaw, paddleocr, pangolin, planetscale,
  r2, risingwave, tuatha)
- 4 non-stack files in `cianfhoghlaim/stacks/`
  (`oideachais_dagster.yaml`, `oideachais_Dockerfile*` × 3)
  — moved to `cianfhoghlaim/assets/_oideachais_dagster_defs/`
- 2 cianfhoghlaim-only stack dirs in `cianfhoghlaim/stacks/`
  (`browser`, `llama-swap`) — moved to `bonneagar/stacks/`
- `bonneagar/iac/komodo/bun.lock` — moved to
  `bonneagar/bun.lock`

### Affected agent skills

- `.agents/skills/infrastructure-stacks/SKILL.md` — update
  the canonical location to `bonneagar/stacks/`
- `.agents/skills/indexing-and-cognition/SKILL.md` — cross-ref
  the IaC at `bonneagar/iac/komodo/`
- `.agents/skills/agent-fleet-orchestration/SKILL.md` — same
- `.agents/skills/agent-observability/SKILL.md` — same
- NEW `.agents/skills/infrastructure-stacks-documentation/SKILL.md`
  — the per-stack doc template

### Affected CI

- `bun run validate-stacks` (stack-doctor) — the gate now
  points at `bonneagar/stacks/` and checks for the per-stack
  doc
- `mise run lint:skills` — the new
  `infrastructure-stacks-documentation` SKILL.md must pass
  the 4 metadata rules
- `openspec validate 2026-06-29-bonneagar-v4-canonical-and-stack-migration --strict` — every `### Requirement:`
  has at least one `#### Scenario:`

## Non-Goals

- This change does **NOT** introduce a shared `kcg/base:latest`
  base image that bundles the cianfhoghlaim package. The
  Dockerfiles keep their existing build approach
  (`python:3.12 + pip install ...`). A future change will
  introduce the base image.
- This change does **NOT** introduce Dagger. The
  `bonneagar/dagger/` TS submodule stays as-is. A future
  change will wire Dagger for image building + testing.
- This change does **NOT** split `bonneagar/` out of the
  monorepo. It only prepares the structure (root
  `package.json`, self-contained paths) for the future
  split. A future change will move `bonneagar/` to its own
  GitHub repo.
- This change does **NOT** delete the 3 cloud-managed stacks
  (`planetscale`, `r2`, `motherduck`) from `bonneagar/stacks/`.
  Only the cianfhoghlaim duplicates are deleted. A future
  change will remove the bonneagar copies.
- This change does **NOT** re-validate the 4 open change
  proposals in `openspec/changes/` that reference the old
  `infrastructure/stacks/` paths
  (`add-openclaw-stack-and-channel-fanout`,
  `add-openchamber-stack-and-opencode-ui`,
  `2026-06-28-split-leabharlann-bonneagar`,
  `2026-06-29-leabharlann-email-inbox-pipeline`). The
  re-validation will happen after this change lands.
- This change does **NOT** introduce the Backrest + Olake
  backup strategy for the komodo-postgres data. That's a
  separate change already drafted in the previous
  plan.
- This change does **NOT** introduce the combined
  "infrastructure stack" / "data engineering stack" group
  abstractions. Those are a separate change.

## Risk Assessment

- **Risk: 35 stack deletions could orphan references.** The
  4 open change proposals in `openspec/changes/` reference
  `cianfhoghlaim/stacks/<name>/` paths. After this change,
  these refs need to be re-validated. **Mitigation:** the
  change is scoped to cianfhoghlaim/stacks → bonneagar/stacks;
  the 4 open changes will be re-validated as a separate
  follow-up.
- **Risk: the hf-watchdog Dockerfile rewrite could break the
  build.** The new multi-stage build depends on the
  cianfhoghlaim image being published to
  `ghcr.io/cianfhoghlaim/cianfhoghlaim:dev`. **Mitigation:**
  the new Dockerfile uses `COPY --from=...` which is a
  standard Docker pattern; if the cianfhoghlaim image is not
  yet published, the fallback is to use
  `pip install cianfhoghlaim` from a private index.
- **Risk: 88 docs is a lot of content.** The per-stack docs
  could become a maintenance burden if they get out of sync
  with the actual stacks. **Mitigation:** the
  `stack-doctor` CI gate fails if a stack is missing its
  doc; a future change can add a doc-drift check that
  compares the doc against the live `compose.yaml` + `pangolin.yaml`.
- **Risk: deleting `infrastructure/` breaks the parallel
  `2026-06-29-fix-ocr-vlm-registry-with-unsloth-priority`
  change.** That change created the `infrastructure/` dir.
  **Mitigation:** the migration moves the only stack
  (hf-watchdog) to `bonneagar/stacks/ci/hf-watchdog/`; the
  other artifacts in `2026-06-29-fix-ocr-vlm-registry-with-unsloth-priority`
  (the BAML schema, the oideachais-pdf-review space) are
  unaffected.

## Validation

1. `docker compose -f bonneagar/stacks/ci/hf-watchdog/compose.yaml config`
   parses successfully
2. `openspec validate 2026-06-29-bonneagar-v4-canonical-and-stack-migration --strict` passes
3. `bun run validate-stacks` passes (no missing 6-file
   stacks, no missing per-stack docs)
4. `ls bonneagar/stacks/ | wc -l` returns 91 (88 original + 3
   migrated from cianfhoghlaim: browser + llama-swap +
   hf-watchdog)
5. `ls cianfhoghlaim/stacks/` returns 0 (or only a
   `.gitkeep`-style file)
6. `ls infrastructure/` returns "No such file or directory"
7. `ls bonneagar/package.json` returns the file (exists at
   the root)
8. `ls cianfhoghlaim/ci/hf_watchdog.py` returns the file
9. `ls cianfhoghlaim/docs/stacks/ | wc -l` returns 91 (88 docs
   + 1 README + 1 ci subdir + 1 hf-watchdog doc)
10. (post-deploy) `bun run iac:read-state` shows the
    komodo-postgres state consistent with the IaC
