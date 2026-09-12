# Change: KCG Legacy Folder Retirement

## Why

`/Users/cianmacandeisigh/dev/kings_college_galway/` was the working name of
this repository before the 2026-07-29
`2026-07-28-reconcile-stack-contract-and-rename-bons-kcg-to-cianfhoghlaim-v1`
archive. The directory has been retained as a stale working tree since then.

A 2026-09-12 audit (the one that motivates this change) shows the folder
now holds only:

| Item | Size class | Action |
|------|-----------:|--------|
| `bonneagar/stacks/{cognee,hermes,lakehouse,litellm,mlflow,openclaw}/` | 6 stacks | Stale duplicates — every file already lives (newer) under `cianfhoghlaim/bonneagar/stacks/<name>/` |
| `bonneagar/stedding/huggingface/` + `stedding/huggingface/` | ~2 GB | HuggingFace model cache (`Snowflake/snowflake-arctic-embed-xs`, `BAAI/bge-large-en-v1.5`, `BAAI/bge-m3`, `Qwen/Qwen3-VL-8B-Instruct-GGUF`) — not source, just downloaded artifacts |
| `notebooks/` | empty dir | Nothing to port |
| `.DS_Store` | macOS metadata | Nothing to port |

**No substantive source content is unique to KCG.** Every config file,
stack definition, openspec change, scripts/, agents/, baml_src/, dlt_sources/,
orchestration/, cocoindex_flows/, motherduck/, web/, and packages/ directory
that once lived in KCG is already merged into `cianfhoghlaim/` (and in many
cases is already a strict superset — the litellm `config.yaml` in KCG is
missing the 2026-08-era `glm-4.6v-flash` + `deepseek-ocr-2` entries that
the canonical copy carries).

The KCG directory therefore exists as pure dead weight: a non-git
working tree that risks being mistaken for the canonical source, while
the actual canonical source lives in a separate git repo (this one) and
is regularly receiving updates that never propagate back.

## What changes

- **Delete** `/Users/cianmacandeisigh/dev/kings_college_galway/` (the
  legacy directory). This is the single concrete action; the rest of this
  change updates the docs that referenced the path so they don't lie
  about a directory that no longer exists.

- **MODIFIED capability** `infrastructure-stacks` (host-path reference at
  §"Identical absolute repository mount"): swap the two literal
  `/Users/cianmacandeisigh/dev/kings_college_galway` path references for
  `/Users/cianmacandeisigh/dev/cianfhoghlaim`, which is the canonical
  post-v7 repository location that the OpenChamber dev container will
  mount after this change.

- **MODIFIED capability** `agent-platform-cluster` (Scenario: "Existing
  sessions are visible through OpenChamber"): same swap.

- **No MODIFIED for `bonneagar-komodo-gitops`**: that spec references
  `kings_college_galway` because that is the **canonical forgejo repo
  name** at `forgejo.cianfhoghlaim.ie/cliste/kings_college_galway` —
  external infrastructure we do not own. `iac/config.ts` line 43 still
  defaults `CONFIG.gitRepo` to `"kings_college_galway"`. That relationship
  is the historical name of the git remote, not a reference to the local
  directory being retired by this change. Out of scope.

- **No MODIFIED for `openspec/research/2026-06-28-browserbase-program-2/`**:
  per `openspec/AGENTS.md` ("Historical research lives in `docs/openspec/` -
  never modify the 3 research files there; they're point-in-time
  artifacts"), the research files are point-in-time and remain unchanged.

- **No MODIFIED for `openspec/project.md` line 121**: it documents the
  external forgejo URL, which is unchanged.

## Why now

- The user has explicitly asked for the merge: *"kings_college_galway was
  the old name for cianfhoghlaim, they should be merged into cianfhoghlaim"*
  (2026-08-26).
- 17 days of post-session work (Aug 26 → Sep 12) have already executed
  the bulk of the merge — the only remaining artefacts are the dead-weight
  items in the audit table above.
- The audit confirms nothing substantive would be lost.

## Risk

- **Low**: the KCG directory is not under git, is not the canonical
  source, and every substantive file it contained is already in
  `cianfhoghlaim/`. Deletion is reversible only via filesystem recovery
  (`.DS_Store` snapshots, etc.) — but nothing in KCG is load-bearing.
- The HuggingFace model cache will need to be re-downloaded if any agent
  tries to load these models from the KCG-side cache after deletion.
  Mitigation: every model referenced by the cache is also cached under
  `cianfhoghlaim/bonneagar/stedding/huggingface/hub/models--<org>--<name>/`
  (the canonical HF cache home for this repo); agents that load models
  resolve to `HF_HOME` env var, which the mise/Locket flow points at
  the canonical path.
- The forgejo git remote at `forgejo.cianfhoghlaim.ie/cliste/kings_college_galway`
  is unchanged. If the local `iac/config.ts` `GIT_REPO` override is ever
  unset (defaulting to `"kings_college_galway"`), Komodo resource-syncs
  will still work because they target the external forgejo URL, not the
  local directory being retired by this change.

## Dependencies

`Blocked by: none`
`Blocked by (soft): none`
`Affected repos: cianfhoghlaim` (single-repo change; forgejo remote name
and `iac/config.ts` are unchanged)

## Out of scope

- Renaming the forgejo git remote (`kings_college_galway` →
  `cianfhoghlaim`) — that requires forgejo admin action and is the
  topic of a separate, larger openspec change.
- Migrating the historical `openspec/research/` files — they're
  point-in-time artifacts by design.
- Fixing any of the 5 inert-layer defects catalogued in MEMORY 1
  (`kcg-runtime-inert-layers`): those defects now live in `cianfhoghlaim/`
  (e.g. `meaisinfhoghlaim/ocr/ensemble/ensembled_extractor.py:639` still
  hardcodes `0.9`; `dlt_sources/api_sources/*.py` still uses `import dlt_sources`
  instead of `import dlt`). The retirement of KCG does not fix or
  preserve those defects — they belong to separate openspec changes
  (e.g. `2026-12-XX-mega-3d-baml-quality-v1`).