# Tasks — 2026-07-13-storage-memory-facade-v1

## Step 1 — Verify the `storage/memf.py` factory works end-to-end (15 min)

1. [x] `ls cianfhoghlaim/storage/memf.py` → confirm 481-LOC file
   exists at the canonical location.
2. [x] `uv run python -c "import asyncio; from
   cianfhoghlaim.storage.memf import get_default_backend,
   MemoryBackend; async def main(): b = await get_default_backend();
   print(b.kind); asyncio.run(main())"` — confirm factory
   resolves to one of the 3 backend kinds.

## Step 2 — Audit the 8 NCCA agents for direct graphiti / falkordb / memgraph imports (30 min)

3. [x] `grep -n "graphiti_client\|falkordb_client\|memgraph_client"
   cianfhoghlaim/agents/tuatha/<slug>_agent.py` for each of the
   8 agents (`gael_agent`, `math_agent`, `hist_agent`,
   `geog_agent`, `chem_agent`, `comp_agent`, `engl_agent`,
   `appm_agent`) → 0 matches per agent.
4. [x] Verify each agent imports from `.wiring` (T4's wire-up
   module) which uses `get_default_backend()` internally — no
   direct client imports.

## Step 3 — Wire the StorageBackend Protocol into the 15 notebooks (1 h)

5. [x] `python3 -c "import ast; ast.parse(open('<notebook>').read())"`
   succeeds for each of:
   - `cianfhoghlaim/notebooks/03_leaving_cert/01_chemistry_analysis.py`
   - `cianfhoghlaim/notebooks/03_leaving_cert/05_mathematics_analysis.py`
   - `cianfhoghlaim/notebooks/03_leaving_cert/03_gaeilge_analysis.py`
   - `cianfhoghlaim/notebooks/03_leaving_cert/02_computer_science_analysis.py`
   - `cianfhoghlaim/notebooks/03_leaving_cert/04_geography_analysis.py`
   - `cianfhoghlaim/notebooks/03_leaving_cert/06_en_vs_ga_comparison.py`
   - `cianfhoghlaim/notebooks/04_biep_motherduck/07_subject_full_pipeline.py`
   - `cianfhoghlaim/notebooks/legacy/corpora/subject_full_pipeline_runner.py`
   - `cianfhoghlaim/notebooks/legacy/corpora/law/01_law_corpus_overview.py`
   - `cianfhoghlaim/notebooks/leaving_cert/chemistry.py`
   - `cianfhoghlaim/notebooks/leaving_cert/computer_science.py`
   - `cianfhoghlaim/notebooks/leaving_cert/english.py`
   - `cianfhoghlaim/notebooks/leaving_cert/gaeilge.py`
   - `cianfhoghlaim/notebooks/leaving_cert/geography.py`
   - `cianfhoghlaim/notebooks/leaving_cert/mathematics.py`

## Step 4 — Add the 3-scenario smoke test (30 min)

6. [x] Create `cianfhoghlaim/tests/test_memory_backend_smoke.py`
   with 3 scenarios:
   - `test_get_default_backend_returns_implementation` —
     asserts `isinstance(backend, MemoryBackend)` + kind ∈
     `{graphiti, falkordb, in_memory_lancedb}`
   - `test_add_episode_round_trips` — adds an `Episode` via the
     canonical factory and searches it back
   - `test_reset_default_backend_returns_fresh_instance` —
     calls `reset_default_backend()` and verifies a fresh
     instance is constructed on the next call

## Step 5 — OpenSpec change (this file's parent directory) (30 min)

7. [x] Write `proposal.md` (this change)
8. [x] Write this `tasks.md`
9. [x] Write `specs/agent-memory-systems/spec.md` (delta —
   1 ADDED Requirement with 2 scenarios)
10. [x] Run `openspec validate 2026-07-13-storage-memory-facade-v1
    --strict` and confirm exit 0

## Step 6 — Commit + push (10 min)

11. [x] `git add -A`
12. [x] Commit with the canonical `feat(memory):` message
13. [x] `git push --set-upstream origin pick-4-biep-v1`