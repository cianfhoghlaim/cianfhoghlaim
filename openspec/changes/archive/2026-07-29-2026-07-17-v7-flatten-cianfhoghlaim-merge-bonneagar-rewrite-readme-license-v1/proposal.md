# v7 — flatten cianfhoghlaim/, re-integrate bonneagar/, rewrite README + LICENSE

## Why

The Cianfhoghlaim monorepo carries 5 sources of structural debt that block
forward motion:

1. **`cianfhoghlaim/` nesting is overhead.** The v4 consolidation
   (`2026-06-28-consolidate-sruth-into-cianfhoghlaim-v4`) merged the 6
   `sruth/<quadrant>/` packages into a single Python package at
   `cianfhoghlaim/`, but the package name and the directory name are the
   same — every import carries the redundant `cianfhoghlaim.` prefix
   even though the package IS the repo. The plan to make the package the
   root itself was always the right shape; v7 lands it.

2. **`bonneagar/` split has cost more than it saved.** The IaC was carved
   out as a separate GitHub repo (and an in-tree worktree) to reduce clone
   size + enable GitOps, but introduced (a) 100+ `bonneagar/` path
   references that have to be edited in two places for every IaC change;
   (b) commit mis-routing risk between the two repos; (c) the
   `bun run --cwd bonneagar` shim that pretends bonneagar is integrated
   but isn't. The IaC is at most 8.9 MB — its exclusion isn't worth the
   cognitive overhead. v7 re-merges bonneagar back into the main repo
   **as a subdirectory** (the user clarified mid-run that the `bonneagar/`
   subdir should be preserved, not flattened to root).

3. **Branch + remote sprawl is unmanageable.** 40+ local branches and
   ~25 remote branches across `origin` and `bonneagar` remotes, mostly
   `pick-*`, `feat/*`, `backup/*`, `q3-2026-*` that have either shipped,
   been abandoned, or live on as dead refs. The user requested **remote
   only** cleanup (local branches stay — don't lose local work).

4. **Leabharlann stays independent.** The 3.4 GB `leabharlann/` corpus is
   the only remaining separately-managed repo. Its README still references
   cianfhoghlaim paths — those need updating in a follow-up change that
   does NOT touch this repo (per the leabharlann independence rule).

5. **README + LICENSE are stale.** The 1464-line README still describes
   the 3-repo constellation (cianfhoghlaim + bonneagar + leabharlann).
   The 57-line LICENSE still calls bonneagar a "companion repository".
   Both need updating for the post-v7 single-repo reality, while
   preserving the family history / credential references verbatim.

## What changes

### 1. Flatten `cianfhoghlaim/` to repo root

```
cianfhoghlaim/{agents,baml,baml_client,baml_src,cocoindex,dlt,
  dlthub-ai-workbench,leabharlann,leaving_certificate,meaisinfhoghlaim,
  motherduck,notebooks,observability,orchestration,storage,tests,tuatha,
  web,__init__.py,__main__.py,__deployment__.py}  →  root
```

`cianfhoghlaim/cli.py` → `clio.py` (collision with the IaC's
`bonneagar/cli.py`).
`cianfhoghlaim/README.md` → `docs/legacy/cianfhoghlaim-pkg-readme.md`
(the package README is preserved as a legacy artifact).
`cianfhoghlaim/pyproject.toml` → `bonneagar/pyproject.toml` (the IaC's
own pyproject).

`scripts/*` merge into root `scripts/`, with
`scripts/legacy/*.pkg` for the few that already exist at root.

### 2. Re-integrate `bonneagar/` into the main repo (as a subdirectory)

The 88 Docker Compose stacks, the unified IaC, the Komodo resource-syncs,
the Pangolin config, the 4 audit scripts — all of it lives in
`bonneagar/` at the repo root. The IaC's package.json scripts run via
`bun run --cwd bonneagar ...` from the root `package.json`.

### 3. Update manifests

- `package.json`: iac:* scripts use `--cwd bonneagar`; workspaces
  simplified to `web/apps/*`, `web/packages/*`, `web/hono-api`.
- `pyproject.toml`: dropped "Companion to cianfhoghlaim/bonneagar" wording;
  kept leabharlann companion.
- `mise.toml`: ruff/mypy/pytest targets run on `.` not `cianfhoghlaim/`;
  `CIANFHOGHLAIM_PYPROJECT_GENERATED_AT` bumped to `2026-07-17`.
- `dg.toml`: code-location path is `.`; module_name is `assets.definitions`.
- `opencode.json`: subagent prompts describe the flat root layout.
- `turbo.json`: wasm output path updated.
- `.gitignore`: IaC patterns scoped to `bonneagar/{stacks,komodo,pangolin,...}/*`.

### 4. Update 5 spec deltas (this change's `specs/<spec>/spec.md` files)

- `bonneagar-iac-merge`: paths change from `bonneagar/iac/` → `iac/` →
  `bonneagar/iac/` (re-clarified: IaC stays in bonneagar/)
- `bonneagar-komodo-gitops`: paths `bonneagar/komodo/` → `bonneagar/komodo/`
  (unchanged — IaC stays in bonneagar/)
- `infrastructure-stacks`: 88 stacks at `bonneagar/stacks/` (unchanged)
- `agent-memory-systems`: stack paths unchanged (always `bonneagar/stacks/...`)
- `data-engineering-pipeline-documentation`: "4 canonical ops dirs" line
  collapses from `(bonneagar/, cianfhoghlaim/assets/, ...)` to
  `(bonneagar/, assets/, docs/stacks/, bonneagar/komodo/)`.

### 5. Update path references across docs + skills + openspec changes

53 `.agents/skills/*/SKILL.md` files + `AGENTS.md` +
`openspec/AGENTS.md` + `openspec/project.md` + `README.md` + ~45 pending
openspec changes get a scripted rewrite to reflect the flat layout.

### 6. Remote branch cleanup (per user: "remote only")

Delete from `origin`:
- `origin/feat/*` (12 branches — all shipped)
- `origin/pick-{1,2,3,6,7,8,9,10}-*` (8 branches — shipped)
- `origin/q3-2026-cianfhoghlaim-consolidation` (rolled into main)

Keep on `origin`:
- `origin/main`, `origin/pick-4-biep-v1`, `origin/pick-5b-bonneagar-v5-continuation`

The `bonneagar` GitHub remote is renamed to `archive-bonneagar` so future
commits cannot be mis-pushed to the standalone repo.

### 7. LICENSE.md edit

Drop the "companion repository cianfhoghlaim/bonneagar" sentence. Keep:
- The BUSL 1.1 grant terms
- The Additional Use Grant
- The Change Date + Change License
- The Governing Law & Jurisdiction
- The "companion repository cianfhoghlaim/leabharlann" sentence (still
  separate)

### 8. README.md rewrite

Preserve verbatim the entire `### On the family — Mac an Déisigh Uí Liatháin
(Deacy-Lyons)` section (lines 637-1230 of the pre-v7 README — the full
genealogical essay, the 3-stream synthesis, the mythological warrant, the
dual-monarchy framework).

Rewrite everything else: TL;DR, the 5-stage pipeline, the 11 NCCA LC
subject asset groups, the PDF processing pipeline, the marimo notebook
catalogue, the OpenSpec catalogue, the 3-host topology, the deployed
stacks summary, the repository constellation (now 2 repos not 3).

## Dependencies

`Blocked by: none`
`Blocked by (soft): 2026-06-28-consolidate-sruth-into-cianfhoghlaim-v4`
(informational — the v4 consolidation created the nested shape that v7
undoes)
`Affected repos: cianfhoghlaim`

The standalone `bonneagar` GitHub repo is affected in name only — it
becomes the `archive-bonneagar` remote after this change.

## Cross-repo sync

See `cross-repo-sync.md`.

## Stats

- 11,701 files renamed/moved in the primary flatten commit
- 4 manifests updated (mise.toml, dg.toml, opencode.json, turbo.json,
  package.json, pyproject.toml, .gitignore)
- 5 spec deltas modified
- 53 skills path-rewritten (scripted)
- 1 LICENSE.md sentence removed
- 1 README.md fully rewritten (with the family section preserved verbatim)

## Out of scope (handled by follow-up changes)

- **leabharlann/ README updates** — references to cianfhoghlaim paths
  need updating in a separate change IN the leabharlann repo (per the
  leabharlann-independence rule).
- **CI workflow files** at `.github/workflows/*` and `.forgejo/workflows/*`
  may reference old paths; these get updated in a follow-up "ci-paths-v7"
  change.
- **opencode.json subagent prompt polish** — the agent prompts are
  functionally correct but the prose is rough; a follow-up change
  rewords them.
