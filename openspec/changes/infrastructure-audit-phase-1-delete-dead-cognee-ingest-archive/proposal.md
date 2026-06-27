# Proposal: Delete dead `infrastructure/scripts/cognee-ingest-archive.py` (round 11 infrastructure phase 1)

## Context

The Cianfhoghlaim platform has 2 Cognee ingestion scripts under
`infrastructure/scripts/`:

| Script | Lines | Status |
|---|--:|---|
| `cognee-ingest-docs.py` | 184 | **ACTIVE** — wired into `mise.toml` (3 task aliases), `.forgejo/workflows/cognee-ingest.yaml`, `.github/workflows/cognee-ingest.yaml`, the `agent-observability` skill, and the `centralize-agent-context-and-automate` openspec change. 7 typed clusters via `cognee-graph-models/`. |
| `cognee-ingest-archive.py` | 434 | **DEAD** — targets 5 input paths that were deleted by the `docs-restructuring` openspec change (round 1 of docs consolidation). Zero production callers (only self-referenced in its own docstring). |

**Why `cognee-ingest-archive.py` is dead**:

The script (lines 11-26 of its docstring) lists its 4 ingestion targets:

```python
1. docs/archive/2026-06-06-*   (date-stamped reference archives)
2. docs/*.pdf at root          (5 loose reference PDFs)
3. docs/auto-deploy-stacks.toml (a single loose config file)
4. docs/INDEX.md, docs/00_index.md (master index files)
```

All 4 target groups were deleted or restructured by the `docs-restructuring` +
`docs-skills-consolidation-pipeline` + `centralize-agent-context-and-automate`
openspec changes (rounds 1-9 of docs consolidation):

- `docs/archive/2026-06-06-*` — the 7 date-stamped archives were deleted by
  `docs-restructuring` and replaced with the canonical 7-domain taxonomy at
  `.agents/skills/`.
- `docs/*.pdf` (5 loose PDFs at root) — deleted by `docs-restructuring`
  (PDFs moved into the `sruth/oideachais/leabharlann/` corpus).
- `docs/auto-deploy-stacks.toml` — deleted by `docs-restructuring`
  (the file no longer exists at the project root).
- `docs/INDEX.md` + `docs/00_index.md` — replaced by `.agents/skills/INDEXING_AND_COGNITION.md`
  as the canonical index.

The script's primary value was ingesting the 7 date-stamped archives
(`docs/archive/2026-06-06-{data-engineering, education, ai-ml, ...}`) which
contained 1,038 docs pre-consolidation. After the docs-restructuring
change, those archives don't exist anymore. The script's ingestion
targets now resolve to zero files, so the script does nothing useful.

**Zero production callers** (verified via grep):

- `mise.toml` — does NOT reference `cognee-ingest-archive.py` (only
  `cognee-ingest-docs.py`).
- `.forgejo/workflows/cognee-ingest.yaml` — does NOT reference.
- `.github/workflows/cognee-ingest.yaml` — does NOT reference.
- `.agents/skills/` — does NOT reference.
- The script's only references are:
  - itself (`infrastructure/scripts/cognee-ingest-archive.py` line 22-28,
    inside its own docstring)
  - the `cognee-ingest-docs.py` script header comment line 9 (mentions it
    as a sibling: "cognee-ingest-archive.py — legacy archive ingestion")

The sibling reference in `cognee-ingest-docs.py` is harmless (just a
descriptive comment); removing the script does not require touching
`cognee-ingest-docs.py`.

## Proposal

Delete the 1 dead script:

1. **Delete** `infrastructure/scripts/cognee-ingest-archive.py` (434 lines).

After this change, `infrastructure/scripts/` contains only:

- `cognee-ingest-docs.py` (184 lines, ACTIVE)
- `cognee-graph-models/` (7 files, ACTIVE — the 7 typed cluster
  graph models wired into `cognee-ingest-docs.py`)
- `create-olm-clients.sh` (126 lines, OPERATIONAL — wraps the
  canonical `createOLMClients` Dagger function at
  `infrastructure/dagger/ts_submodules/bonneagar/src/pangolin.ts:940`)
- `deploy-cf.sh` (95 lines, ACTIVE — wired into 4 `mise.toml` tasks)
- `dev.sh` (136 lines, ACTIVE — wired into 4 `mise.toml` tasks)
- `setup-pangolin-komodo.sh` (241 lines, OPERATIONAL — referenced
  by `infrastructure/docs/pangolin-komodo/` + `infrastructure/iac/komodo/README.md`)
- `stack.sh` (171 lines, ACTIVE — wired into 3 `mise.toml` tasks)
- `sync-blueprints.sh` (177 lines, ACTIVE — wired into 2 Komodo procedures)

The pre-existing user-in-flight work on `infrastructure/scripts/cognee-ingest-docs.py`
(modification) is unchanged — out of scope.

## Affected surfaces

- 1 file deleted (434 lines)
- 0 files added
- 1 spec delta added to `indexing-and-cognition`

## No backwards compatibility

Per round 11 conventions, no `try/except ImportError` fallback shims, no
deprecation warnings. Delete outright. If the script's original purpose
(ingesting legacy archives) is ever needed again, the operator can
re-create it from git history (the file is preserved at
`openspec/changes/archive/2026-06-27-infrastructure-audit-phase-1-delete-dead-cognee-ingest-archive/`).