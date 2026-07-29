## Shipped in code

All work proposed here has been delivered to the codebase since this change was opened. The remaining tasks are validation gates + the final `openspec archive` call.

# Production-ise StorageBackend Protocol + `get_default_backend()` factory

## Why

The T4 commit `0bf713c45` ("feat(agents): T4 agent-fleet + baml
0.212 + observability + storage facades") added the
`storage-memory-facade` capability:

- `storage/memf.py` (481 LOC) — the canonical
  `MemoryBackend` Protocol + 3 concrete backends
  (`GraphitiBackend` + `FalkorDBBackend` +
  `InMemoryLanceDBBackend`) + `get_default_backend()` factory with
  a 30-s-cached Graphiti → FalkorDB → InMemoryLanceDB cascade.
- 1 ADDED spec on `agent-memory-systems` (the `MemoryBackend`
  Protocol surface requirement — the one T4 + the
  `2026-07-10-wire-8-subject-agents-cognify-langfuse-v1` change
  added).
- The `agents/tuatha/wiring.py` module (~600 LOC, no graphiti /
  falkordb imports) that the 8 NCCA subject agents consume.

What was **not** done by T4 and what this change closes:

1. The 8 NCCA subject agents
   (`gael_agent`, `math_agent`, `hist_agent`, `geog_agent`,
   `chem_agent`, `comp_agent`, `engl_agent`, `appm_agent`) were
   wired via `wiring.py` but the wiring module was **not**
   verified end-to-end with a real smoke test that:
   - Probes the factory + asserts `MemoryBackend` kind in
     `{graphiti, falkordb, in_memory_lancedb}`
   - Adds an `Episode` via the canonical factory
   - Round-trips a search
2. The factory itself was never smoke-tested from a CI-style
   `pytest` run.
3. The 9 BAML-using notebooks + the 6 per-subject marimo
   notebooks (from the N1 commit `c12c4f4cb`) had never been
   AST-parsed after the storage-facade refactor — silent
   breakage was possible.
4. The 8 NCCA agents' direct-import audit (the Step 4 acceptance
   gate from the wire-8-subject-agents change) was not codified
   in a smoke test that survives across refactors.

This change lands all 4 items as a single 4-hour production-ise
pass with a new ADDED requirement on `agent-memory-systems`.

## What changes

### 1. Smoke test the `MemoryBackend` factory

Add `tests/test_memory_backend_smoke.py` with 3
pytest scenarios that run in the CI hermetic environment (no
Graphiti / no FalkorDB → the factory falls through to
`InMemoryLanceDBBackend` per the cascade):

- `test_get_default_backend_returns_implementation` — asserts
  `isinstance(backend, MemoryBackend)` + `backend.kind` ∈
  `{graphiti, falkordb, in_memory_lancedb}`.
- `test_add_episode_round_trips` — adds an `Episode` and reads
  it back via `backend.search(...)`.
- `test_reset_default_backend_returns_fresh_instance` — calls
  `reset_default_backend()` then `get_default_backend()` again
  and verifies a fresh instance is constructed.

### 2. AST-parse the 9 BAML + 6 per-subject notebooks

Verifies that the 15 notebooks
(`notebooks/03_leaving_cert/*.py` +
`notebooks/04_biep_motherduck/07_subject_full_pipeline.py`
+ `notebooks/legacy/corpora/{subject_full_pipeline_runner.py,
law/01_law_corpus_overview.py}` + the 6 per-subject stubs at
`notebooks/leaving_cert/{chemistry,computer_science,
english,gaeilge,geography,mathematics}.py`) all AST-parse OK
after the storage-facade refactor.

### 3. Audit the 8 NCCA agents

`grep -n "graphiti_client\|falkordb_client\|memgraph_client"
agents/tuatha/<slug>_agent.py` returns 0 matches
for each of the 8 agents. The agents consume the canonical
`wiring.py` module which uses `get_default_backend()` internally
— never direct client imports.

### 4. Codify the production-ise gate as a 1 ADDED spec on
`agent-memory-systems`

1 ADDED requirement + 2 scenarios (smoke test passes + 8 agents
have no direct imports) on the existing
`agent-memory-systems` spec.

## Acceptance gates

- `openspec validate 2026-07-13-storage-memory-facade-v1 --strict`
  passes (1 ADDED spec delta well-formed)
- `uv run pytest tests/test_memory_backend_smoke.py`
  reports 3 tests — all pass
- `grep -n "graphiti_client\|falkordb_client\|memgraph_client"
  agents/tuatha/{gael,math,hist,geog,chem,comp,engl,appm}_agent.py`
  returns 0 matches per agent
- `python3 -c "import ast; ast.parse(open(...))"` succeeds for
  each of the 9 BAML + 6 per-subject notebooks (15 total)
- The factory cascade order (Graphiti → FalkorDB → InMemoryLanceDB)
  works as documented in `storage/memf.py`

## Dependencies

`Blocked by: none` (T4's `0bf713c45` + the
`2026-07-10-wire-8-subject-agents-cognify-langfuse-v1` change are
both already on the branch — T4 added the `MemoryBackend` Protocol
+ factory + the 8-agent wire-up).

`Blocked by (soft): 2026-07-10-wire-8-subject-agents-cognify-langfuse-v1`
(this change production-ises T4's work; it amends
`agent-memory-systems` on the same spec T4 amended).

`Affected repos: cianfhoghlaim` (single-repo change).

## Estimated effort

4 hours of focused work, organised as 6 numbered steps (see
`tasks.md`).

## Cross-repo sync

Not applicable — this is a single-repo change. `bonneagar` +
`leabharlann` are unaffected.

## Files touched

- **Add**: `tests/test_memory_backend_smoke.py` —
  the 3 smoke-test scenarios
- **Add**: `openspec/changes/2026-07-13-storage-memory-facade-v1/`
  (the 4 openspec change files: `proposal.md` + `tasks.md` +
  `specs/agent-memory-systems/spec.md`)
- Total: 2 added files (1 test + 1 openspec change directory) +
  0 modified files

## Risk

**Low**. The factory already exists (T4 commit `0bf713c45`),
already works in production (the BIEP v1 ingestion is wired
through it), and the smoke test only reads the factory — it
never mutates persistent state. The 8 agents are unchanged; the
test file is additive.