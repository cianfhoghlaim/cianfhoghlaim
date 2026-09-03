# Tasks: 2026-07-09-agent-fleet-and-observability-facade-v1

Tangent **T4** of the `2026-07-09-five-tangent-modernization` plan.
The 32-hour scope is broken into the 10 numbered work items
below; each item has an explicit verification step.

## Step 1: Resolve the empty `ocr/` directory footgun (1h)

- [x] Verify the legacy `oideachas.ocr.adapters` reference
  (in `meaisinfhoghlaim/backends/adapters.py:11` docstring) is
  a docstring-only stale reference, not an actual import.
- [x] Update the docstring to point at the canonical
  `cianfhoghlaim.meaisinfhoghlaim.backends.adapters` entry.
- [x] Confirm `cianfhoghlaim/ocr/` is the canonical v4 home
  for the OCR/VLM registry (per `openspec/specs/meaisinfhoghlaim-ocr-htr/spec.md`
  line 685) — it is **not** an empty directory, so no
  structural change is needed.

**Verification**: `grep -rn "oideachas.ocr" cianfhoghlaim/` returns
no actual `import` statements (only the docstring we updated).

## Step 2: Wire the 3 unused OCR adapters (4h)

- [x] Wire `PaddleOCRAdapter` + `DoclingAdapter` +
  `DotsOCRAdapter` + `UnstractAdapter` to
  `meaisinfhoghlaim/evaluation/compare.py:_run_classical_eval()`.
- [x] Add the `_CLASSICAL_ADAPTER_FOR_STACK` mapping dict.
- [x] Add a graceful-error path (notes="adapter-error: …")
  when an adapter errors.

**Verification**: `uv run python -c "from cianfhoghlaim.meaisinfhoghlaim.evaluation.compare import _CLASSICAL_ADAPTER_FOR_STACK"` exports the 4 adapters.

## Step 3: Move the federated OCR (3h)

- [x] Move `meaisinfhoghlaim/process/irish_ocr_federated.py`
  → `meaisinfhoghlaim/federated/irish_ocr_federated.py`.
- [x] Add `meaisinfhoghlaim/federated/__init__.py` with full
  re-exports of the public surface.
- [x] Add `CelticFederatedOcrComponent` to
  `orchestration/components/layer3_model_lifecycle.py`.
- [x] Add `orchestration/defs/3_model_lifecycle/federated_ocr/defs.yaml`.

**Verification**: `uv run python -c "from cianfhoghlaim.orchestration.components.layer3_model_lifecycle import CelticFederatedOcrComponent; print('OK')"`.

## Step 4: Wire the 8 subject agents (4h)

For each of `gael_agent`, `math_agent`, `hist_agent`,
`geog_agent`, `chem_agent`, `comp_agent`, `engl_agent`,
`appm_agent`:

- [x] Create `orchestration/defs/5_agent_ops/adk/<slug>_agent/defs.yaml`
  with the `CelticAgentOpsComponent` config + NCCA-specific
  routing keywords.
- [x] Add seed entries for the 8 NCCA subjects to
  `agents/routing_keywords.py:ROUTING_KEYWORDS`.

**Verification**: 8 `defs.yaml` files exist; `grep -r
"gael_agent" cianfhoghlaim/agents/routing_keywords.py` returns a
non-empty bucket.

## Step 5: Rewrite `baml/clients.baml` (3h)

- [x] Rewrite the file from the legacy v0.x
  `client X { provider "..." }` syntax to the canonical
  baml 0.212+ `generator {}` blocks.
- [x] Add 2 `retry_policy` blocks (Simple + Exponential).
- [x] Add 3 `test` blocks for the 5-tangent's `@test`
  golden-test convention.

**Verification**: `grep -E "^client " cianfhoghlaim/baml/clients.baml`
returns 0 matches (the file uses only `generator` + `retry_policy` +
`test` blocks).

## Step 6: Add `PlatformTracer` facade (4h)

- [x] Create `observability/platform_tracer.py` with:
  - `class PlatformTracer`
  - `class PlatformSpan`
  - `class BackendState`
  - `def get_tracer()` + `def reset_tracer()`
- [x] Re-export the 5 symbols from `observability/__init__.py`
  AND add them to `__all__`.
- [x] The tracer wraps `langfuse_config`, `mlflow_config`,
  `logfire_config` — does not reimplement them.
- [x] Add the Langfuse → MLflow → Logfire fallback cascade.

**Verification**: `uv run python -c "from cianfhoghlaim.observability
import PlatformTracer, get_tracer, PlatformSpan, BackendState,
reset_tracer; t = get_tracer(); print('OK')"`.

## Step 7: Add `MemoryBackend` Protocol (4h)

- [x] Create `storage/memf.py` with:
  - `class MemoryBackend(Protocol)`
  - `class GraphitiBackend` (canonical primary)
  - `class FalkorDBBackend` (cascade fallback)
  - `class InMemoryLanceDBBackend` (last-resort)
  - `async def get_default_backend() -> MemoryBackend`
  - `Episode`, `Node`, `SearchResult` dataclasses

**Verification**: `uv run python -c "import asyncio; from
cianfhoghlaim.storage.memf import get_default_backend, MemoryBackend,
GraphitiBackend, FalkorDBBackend, InMemoryLanceDBBackend, Episode;
b = asyncio.run(get_default_backend()); print('OK', b.kind)"`.

## Step 8: Split the `memgraph_client.py` monolith (3h)

- [x] Create `storage/_memgraph_protocol.py` (Protocol +
  4 dataclasses + MemgraphConfig + get_config() + FalkorDBConfig).
- [x] Create `storage/_memgraph_client.py` (the 28-method
  `MemgraphClient` class body).
- [x] Create `storage/_memgraph_queries.py` (`CurriculumGraph`,
  `CurriculumDataLoader`, `load_curriculum_to_graph`,
  `get_curriculum_graph`).
- [x] Replace `storage/memgraph_client.py` with a thin
  back-compat re-export shim.
- [x] Also fix the pre-existing `from ..storage.config import`
  dead-import in `falkordb_client.py` (it pointed at the same
  non-existent module; redirects to `_memgraph_protocol`).

**Verification**: `uv run python -c "from cianfhoghlaim.storage.memgraph_client import MemgraphClient, CurriculumGraph, CurriculumDataLoader, MemgraphConfig, get_config, Subject, Strand, StrandUnit, LearningOutcome, CurriculumNode; print('OK')"`.

## Step 9: Add `subject_router` smoke tests (2h)

- [x] Create `tests/test_subject_router_smoke.py` with 20 tests
  covering:
  - subject_router module imports cleanly
  - `NCCA_SUBJECTS` enumerates exactly 8 subjects
  - the 8 NCCA subject agents each instantiate when imported
  - the `ROUTING_KEYWORDS` seed is populated for all 8
  - `list_all_agents()` enumerates 8 entries
  - `make_subject_team()` raises `ValueError` on unknown subject

**Verification**: `uv run pytest cianfhoghlaim/tests/test_subject_router_smoke.py` returns 20 passed.

**Side-effect fix** (uncovered during implementation):
wrapped 3 pre-existing unconditional imports in
`try/except` so subject agents can be imported without `agno`:

- `agents/__init__.py:56` (`from .agno import (...)`)
- `agents/agno/__init__.py:15` (`from .education_team import (...)`)
- `agents/tools/__init__.py:14-71` (the eager
  `corpus_search` / `corpus_tools` / `curriculum_search` etc.
  block)

Without these wraps, the test imports `agents.tuatha.math_agent`
triggers `agents.tools.corpus_tools` which fails on
`from agno.tools import Toolkit` — blocking the T4 acceptance gate.

## Step 10: Write the openspec change (4h)

- [x] `openspec/changes/2026-07-09-agent-fleet-and-observability-facade-v1/proposal.md`
- [x] `openspec/changes/2026-07-09-agent-fleet-and-observability-facade-v1/tasks.md`
- [x] 4 spec deltas:
  - `specs/meaisinfhoghlaim-agent-frameworks/spec.md` — MODIFIED (6 → 10)
  - `specs/meaisinfhoghlaim-ocr-htr/spec.md` — MODIFIED (4 → 6)
  - `specs/agent-observability/spec.md` — MODIFIED (12 → 14)
  - `specs/storage-memory-facade/spec.md` — NEW (6 requirements)

**Verification**: `openspec validate 2026-07-09-agent-fleet-and-observability-facade-v1 --strict` passes.

## Final report gates

- [x] Commit hash(es) recorded
- [x] `openspec validate` output captured
- [x] All 10 step statuses: ✅ (all 10 done; 1 with degraded
  `mise run baml:generate` due to pre-existing repo-wide
  baml schema errors unrelated to T4)
- [x] 4 spec delta summaries recorded
- [x] Push target: `origin/pick-4-biep-v1`
