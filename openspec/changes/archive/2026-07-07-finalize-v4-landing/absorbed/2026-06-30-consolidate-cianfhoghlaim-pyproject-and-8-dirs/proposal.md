# 2026-06-30-consolidate-cianfhoghlaim-pyproject-and-8-dirs — Consolidate cianfhoghlaim pyproject, mise, and 8 stale directories

## Why

The v4 cianfhoghlaim consolidation (`openspec/changes/archive/2026-06-28-2026-06-28-consolidate-sruth-into-cianfhoghlaim-v4/`) merged 5 former `sruth/*` quadrants + `infrastructure/browser/` + `leabharlann/` into a single `cianfhoghlaim/` Python package, but the **on-disk outcome is structurally broken** in five concrete ways:

1. **3 frozen `_quadrant_pyproject.toml` files** at `cianfhoghlaim/{_oideachais_pyproject.toml, _meaisinfhoghlaim_pyproject.toml, _tuatha_pyproject.toml}` describe packages (`oideachais`, `tuath`, `meaisinfhoghlaim`) that **no longer exist as separate uv-workspace members** post-v4. They were left behind because the consolidation removed the members but did not delete the manifests.

2. **The wheel package list doesn't match on-disk directories.** `pyproject.toml [tool.hatch.build.targets.wheel] packages` declares `core`, `pipelines`, `sources`, `assets`, `ocr`, `embeddings`, `cognify`, `notebooks` — **none of these directories exist on disk**. Conversely, `baml/`, `dagster/`, `dlt/`, `browser/`, `cocoindex/`, `meaisinfhoghlaim/`, `observability/`, `geospatial/`, `storage/` are real Python packages with `__init__.py` but are **not** in the wheel.

3. **100+ broken imports** from the deleted `sruth.*` and `oideachais.*` namespaces remain across `dagster/`, `dlt/`, `agents/`, `cocoindex/`, `meaisinfhoghlaim/`, `observability/`, `notebooks/`, `scripts/`, `tests/`. Verified via Grep — representative cases: `dlt/duchas.py:35` (`from sruth.oideachais.observability.logging import get_logger`), `meaisinfhoghlaim/llm_router.py:21-24` (`from sruth.oideachais.core.utils import CircuitBreaker`), `dagster/asset_checks.py:23` (`from sruth.oideachais.dagster_defs.assets.llm_gateway_assets import minimax_alias_health`), `dagster/sensors/cognee_cron_sensor.py:28`, `dagster/assets/embedding_assets.py:59`, etc.

4. **`browser/__init__.py` is a broken deprecation stub** that imports from `cianfhoghlaim.core.browser` — a package that was never created. The real sruth-browser source was renamed from `infrastructure/stacks/browser/` to `bonneagar/stacks/browser/` during the v4 follow-on (`openspec/changes/archive/2026-06-29-2026-06-29-per-domain-web-app-consolidation/`), but the local `cianfhoghlaim/browser/` copy was never deleted.

5. **`meaisinfhoghlaim/` is a stale partial-migration snapshot.** It holds 22 loose `.py` files at the top level that were never redistributed to their canonical v4 homes (`ocr/_meaisinfhoghlaim_src/`, `pipelines/process/_meaisinfhoghlaim_pipelines/`, `core/{evaluation,quality,alignment,ml_training}/`). Six top-level files import from the deleted `sruth.*` namespace. `evaluation/compare.py:25` imports `from cianfhoghlaim.ocr.models.registry import (...)` — a path that does not exist.

The platform's **distinct focus** is now `cocoindex + dagster + dlt + meaisínfhoghlaim pipelines`. This change consolidates the pyproject, mise, and import surface around that focus and sets the stage for the upcoming **`/Users/cianmacandeisigh/dev/kings_college_galway/cianfhoghlaim/web/` rewrite** (a separate follow-on change `rewrite-cyanfhoghlaim-web-v1`).

## What

A single openspec change with **7 numbered phases** executed sequentially. Each phase has its own validation gates and must pass before the next begins.

### Phase 1 — Manifest consolidation (no functional change)
Replace the broken `pyproject.toml` wheel/deps/scripts with the merged manifest, fix `dg.toml` workspace wiring, delete the 3 stale `_quadrant_pyproject.toml` files, create the missing CLI entry-point modules.

### Phase 2 — 8-directory import migration (HARD CUTOVER)
**PREREQUISITE:** `openspec/changes/cianfhoghlaim-educational-mmo-v1/` Phase 2 (T2.7/T2.9/T2.10/T2.12 — theme rename) must have landed first. Mechanically rewrite all 100+ stale `from sruth.*` / `from oideachais.*` imports to the canonical `from cianfhoghlaim.*` namespace across the 8 directories.

### Phase 3 — `meaisinfhoghlaim/` redistribution per the v4 spec
Move the 22 loose `.py` files + 9 sub-directories to their canonical v4 homes (`ocr/`, `pipelines/process/_meaisinfhoghlaim_pipelines/`, `core/{evaluation,quality,alignment,ml_training,ci,document_factory,config}/`, `assets/_tuatha_dagster_defs/`, `leabharlann/samplai/`, `observability/ocr.py`). Delete the now-empty `meaisinfhoghlaim/` directory.

### Phase 4 — Observability consolidation
Implement the 3 missing `UnifiedTracer` backends (`DatadogBackend`, `LangfuseBackend`, `LogfireBackend`) — currently stubs that only `logger.debug(...)`. Flatten `logfire_config.py` re-exports into `observability/__init__.py`. Add `init_all_observability()` convenience function. Wire the `@observe` / `@track_agent_run` / `@trace_adk_agent` decorators into the 12-agent fleet.

### Phase 5 — Browser consolidation
Delete the stale duplicate `cianfhoghlaim/browser/` directory (real home is `bonneagar/stacks/browser/`). Update 4 + 8 + 4 = 16 import sites across Dagster + DLT + scripts + notebooks to point at `bonneagar.stacks.browser.sruth_browser`.

### Phase 6 — CocoIndex + BAML consolidation
Consolidate the 4 stacked `baml/clients*.baml` files → 2 (`clients.baml` canonical + `clients_llama_swap.baml` specialty). Create the canonical `cocoindex/_lifespan.py` shared home for `LANCE_DB`, `EMBEDDER`, `RESOLVED_FILE_REGISTRY` (per `oideachais-cocoindex-v1` skill REFACTORING.md item 12). Add `cocoindex/__init__.py`.

### Phase 7 — `mise.toml` consolidation
Add ~30 new task aliases under the `[tasks.cic:]` (CIANFHOGHLAIM) namespace (sub-groups `cic:ocr:`, `cic:baml:`, `cic:cocoindex:`, `cic:dagster:`, `cic:dlt:`, `cic:meaisin:`, `cic:browser:`). **Delete 4 stale dagster aliases** (`dagster:tuatha`, `dagster:croilar`, `dagster:meaisin`, `dagster:crypteolas`). **Keep `dagster:oideachais` renamed to `dagster:dev`** as the single canonical alias.

## Impact

| Metric | Before | After |
|--|--|--|
| pyproject.toml files in `cianfhoghlaim/` | 4 (1 real + 3 stale underscores) | 1 |
| Wheel packages declared in `[tool.hatch.build.targets.wheel]` | 10 (mostly missing on disk) | 18 (all real, all on disk) |
| Stale `sruth.*` / `oideachais.*` imports inside `cianfhoghlaim/` | 100+ | 0 |
| `baml/clients*.baml` files | 4 stacked | 2 |
| `[project.scripts]` entry-points that resolve to real modules | 2 of 5 | 8 of 8 |
| `dg.toml` module_name matches a real module | no (`cianfhoghlaim.assets.definitions`) | yes (`cianfhoghlaim.dagster.definitions`) |
| `mise.toml` task aliases under the cianfhoghlaim umbrella | ~20 (spread) | ~50 (under `cic:` namespace) |
| Stale dagster aliases pointing at the same module | 5 | 1 (`dagster:dev`) |
| `meaisinfhoghlaim/` loose .py files at top level | 22 | 0 (all redistributed) |
| Browser package locations | 2 (`cianfhoghlaim/browser/` + `bonneagar/stacks/browser/`) | 1 (`bonneagar/stacks/browser/`) |
| In-tree observability backends with real SDK calls | 6 of 9 | 9 of 9 |
| Tests inside `cianfhoghlaim/tests/_meaisinfhoghlaim/` | 5 broken (legacy paths) | 5 passing (canonical paths) |

## Risks

1. **Breaking the active `dg dev` workspace.** T1.8 directly changes `dg.toml [[workspace.locations]] module_name`. If T2.3 isn't complete by then, `dagster dev` will fail to start. **Mitigation:** T1.8 only lands AFTER T2.3; the validation gate for Phase 1 includes `uv run dagster dev -m cianfhoghlaim.dagster.definitions` (the new path).

2. **The parallel `cianfhoghlaim-educational-mmo-v1` change's Phase 2 (theme rename) runs in parallel.** Its T2.7 (`agents/tuatha/` → `agents/meaisinfhoghlaim/educational/`), T2.9 (`dlt/destinations_tuatha.py` → `destinations_educational.py`), T2.10 (`baml/tuatha_clients.baml` → `educational_clients.baml`), and T2.12 (import path updates) directly conflict with our Phase 2 import migration. **Mitigation:** Phase 2 of this change has a **hard gate** — it does not start until `openspec list --changes` shows `cianfhoghlaim-educational-mmo-v1` archived or its Phase 2 commit landed.

3. **Hard cutover for `sruth.*` / `oideachais.*` imports** breaks anything outside the monorepo that consumes these paths. **Mitigation:** these were internal pre-v4 namespaces — no external consumer should depend on them.

4. **`meaisinfhoghlaim/` redistribution** moves 22 files; risk of breaking the v4 OCR/VLM registry. **Mitigation:** T3.2 is the registry move (`registry.py` → `ocr/models/registry.py`); T3.3 archives the legacy 9×6 model_registry to `.archive/`. Validation: `mise run upstream:conformance` must report 14/14 PASS after T3.x.

5. **Observability backends are currently stubs.** T4.4 makes them real SDK calls; risk of Latency regression if Datadog is enabled. **Mitigation:** keep Datadog disabled per the current `.infisical.env` template (lines 27-43 commented out); only MLflow + Langfuse + Logfire will make real calls.

6. **Phase 7 (mise consolidation) deletes 4 dagster aliases.** Any external script invoking `mise run dagster:tuatha` will break. **Mitigation:** the rename preserves `dagster:oideachais` (the most common historical alias) under the new name `dagster:dev`. The 4 deleted aliases have no known external consumers per the v4 audit.

## Acceptance criteria

After all 7 phases complete, every one of these must be true:

- [ ] `openspec validate 2026-06-30-consolidate-cianfhoghlaim-pyproject-and-8-dirs --strict` passes (run after Phase 1)
- [ ] `uv sync` succeeds with the merged dependency list
- [ ] `python -c "import cianfhoghlaim.agents, cianfhoghlaim.baml, cianfhoghlaim.cocoindex, cianfhoghlaim.dagster, cianfhoghlaim.dlt, cianfhoghlaim.meaisinfhoghlaim, cianfhoghlaim.observability, cianfhoghlaim.ocr"` succeeds (all 8 in a single Python process)
- [ ] All 8 `[project.scripts]` entry-points (`cianfhoghlaim`, `cianfhoghlaim-ocr`, `cianfhoghlaim-baml`, `cianfhoghlaim-marimo`, `cianfhoghlaim-stack-doctor`, `cianfhoghlaim-dagster`, `cianfhoghlaim-dlt`, `cianfhoghlaim-cocoindex`) print `--help` without `ModuleNotFoundError`
- [ ] `grep -rE "from sruth\.|from oideachais\." cianfhoghlaim/ --include='*.py' --exclude-dir=.archive` returns zero matches
- [ ] `mise run dagster:dev` (renamed from `dagster:oideachais`) launches and the asset graph contains all 199 assets + 31 jobs + 6 schedules + 16 sensors + 22 asset checks
- [ ] `mise run upstream:conformance` reports 14/14 v1 CocoIndex Apps passing R1-R4
- [ ] `mise run baml:generate` succeeds with no errors
- [ ] `mise run lint:skills` reports 123/123 (no skill metadata changed)
- [ ] `mise run turbo typecheck` passes (all 5 bun workspaces)
- [ ] `uv run pytest cianfhoghlaim/tests/` passes (all 5 test directories: `_meaisinfhoghlaim/`, `_oideachais/`, `_tuatha/`, `_croilar/`, `shared/`)
- [ ] `uv run pytest bonneagar/stacks/browser/tests/` passes (4 browser test files + 1 conformant browser `__init__.py`)
- [ ] `mise doctor` reports all `cic:*` task aliases resolve

## What this change does NOT cover (handoff to next change)

After this change is archived, the follow-on work will be:

| Change | Scope |
|:--|:--|
| `rewrite-cyanfhoghlaim-web-v1` | **Complete rewrite of `cianfhoghlaim/web/`** — TanStack Start 2D MMO client (`apps/cianfhoghlaim-mmo/`), 8 subject realm routes, badge wallet, mastery dashboard, teacher view, Merkle anchor verification. Implements `openspec/changes/cianfhoghlaim-educational-mmo-v1/` Phase 6. |
| `tuatha-platform-spec-removal` | After 1 release, mark `openspec/specs/tuatha-platform/spec.md` as `## REMOVED Requirements` (already in MMO change T2.6) |
| `meaisinfhoghlaim-platform-spec-update` | Update `openspec/specs/meaisinfhoghlaim-platform/spec.md` to reflect the post-redistribution homes (`agents/meaisinfhoghlaim/educational/`, `ocr/_meaisinfhoghlaim_src/`) |

## Coordination with parallel work

This change is part of a 3-change refactor sequence:

```
openspec/changes/cianfhoghlaim-educational-mmo-v1/    (parallel session, Phase 0-1 in progress)
   └── Phase 2 (T2.7/T2.9/T2.10/T2.12) — theme rename
         │  [HARD GATE]
         ▼
openspec/changes/2026-06-30-consolidate-cianfhoghlaim-pyproject-and-8-dirs/   [THIS CHANGE]
   └── Phase 1-7
         │  [handoff]
         ▼
openspec/changes/rewrite-cyanfhoghlaim-web-v1/        (FUTURE — web/ rewrite)
```

The Phase 2 hard gate is encoded in `tasks.md`.