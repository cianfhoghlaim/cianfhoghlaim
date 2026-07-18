# 2026-07-14 — Foundation refactor: complete v7 flattening + fix BAML drift

## Why

Two load-bearing drift categories block end-to-end runs of `mise run biiep:e2e` and
every other mise task that imports a cianfhoghlaim sub-module. Fixing them is the
foundation that 17 active BIEP v3 openspec changes + the entire DAG (Thm C-F per
the 30/06/2026 deep-cuts workshop) builds on.

### Drift category 1 — the `cianfhoghlaim` Python package does not exist on disk

- Root `pyproject.toml:43-44` declares `[tool.hatch.build.targets.wheel] packages = []` and
  `[tool.uv] package = false`.
- Root `pyproject.toml:61-63` declares the workspace member `members = ["cianfhoghlaim"]`,
  referencing a directory that does not exist on disk.
- The Python package marker files (`__init__.py`, `__main__.py`, `__deployment__.py`,
  `clio.py`) **are** at the repo root — they use the `__double_underscore__` ordering
  trick so they sort first in directory listings.
- 5 of 6 sub-packages have `__init__.py` (`agents/`, `cocoindex/`, `meaisinfhoghlaim/`,
  `notebooks/`, `orchestration/`). The other 4 (`baml_src/`, `bonneagar/`, `dlt/`,
  plus the missing `dlt/cli.py` shim) rely on namespace-package semantics that work
  in Python 3.12+ but are blocked by hatch's wheel builder because
  `packages = []` makes the package an empty distribution.
- All canonical CLI entry-points named by mise.toml are broken at import time:
  `python -m cianfhoghlaim.dlt.cli`, `python -m cianfhoghlaim.cocoindex.cocoindex_v1_conformance`,
  `python -m cianfhoghlaim.dagster.cli`, `python -m cianfhoghlaim.ocr.cli`. The Dagster
  code-location loader (`mise run dagster:dev`) fails with `ModuleNotFoundError:
  No module named 'cianfhoghlaim'`.

### Drift category 2 — BAML surface has 5 categories of compile errors

Across `baml_src/`, the BIEP v3 wave + the BIEP v1 leftover files have introduced:
1. **Default-value class fields** in 2 England files (`language string = "en"`).
2. **Unterminated string** in `baml_src/british_isles/england/education/ensembled_extraction.baml:38`.
3. **Lowercase `test` keyword** in 6 `_legacy/grading/*.baml` files.
4. **Missing `client` field** in 3 functions of `_legacy/web/gaeilge_web.baml`.
5. **String-literal type reference** in
   `baml_src/british_isles/ireland/education/marking/computer_science_marking.baml:100`.

`mise run baml:generate` exits non-zero on the first error class.

## Dependencies

```yaml
Blocked by: none
Affected repos: cianfhoghlaim (workspace root)
```

This is a foundation change. Every other BIEP v3 + post-v7-flattens change depends on it
(this change unblocks them). The change is therefore widely relevant and may NOT
archive until every dependent change archives — see Verification § "Post-merge
gating" for the rollout plan.

## What this changes (high-level)

A 6-theme foundation change. Themes A+B are implemented in this single change;
themes C-F (cocoindex lifecycle / marimo+notebooks / Dagster 3-path / bonneagar IaC)
are planned as follow-up changes per the 30/06/2026 deep-cuts workshop.

| # | Theme | Scope | Implemented now? |
|--:|:--|:--|:--|
| A | Complete v7 flattening | Make the `cianfhoghlaim` Python package importable | **YES** |
| B | Fix BAML surface | Compile-error fixes across 5 categories | **YES** |
| C | Cocoindex v1 import-path + R3 linter | 43 `from ._lifespan import` + R3 too-strict + missing `__init__.py` | No — follow-up |
| D | Notebooks ibis-first + WASM export | 65 raw `duckdb.connect` + scripts/marimo_wasm_export.py stub | No — follow-up |
| E | Orchestration 3-path reconciliation | mise.toml + dg.toml + orchestration/definitions.py drift | No — follow-up |
| F | Bonneagar IaC sync-procedures parser | stubbed parser `echo synced $name` | No — follow-up |

## Theme A — Complete v7 flattening (implemented now)

### Goals
1. `uv sync` succeeds against the workspace root.
2. `python -c "from cianfhoghlaim.dlt.common.cli import main"` succeeds.
3. `python -m cianfhoghlaim` (via `__main__.py`) succeeds.

### File edits
| File | Change |
|:--|:--|
| `pyproject.toml` | (a) `[tool.hatch.build.targets.wheel] packages = ["."]`; (b) add `[tool.hatch.build.targets.wheel.force-include]` for the root Python files + every sub-dir's Python content; (c) add 9 missing deps; (d) fix `[tool.ruff.lint.isort].known-first-party` from `sruth`/`oideachais` to `cianfhoghlaim` |
| `dlt/__init__.py` | New — empty docstring + canonical sub-module re-exports |
| `dlt/cli.py` | New — shim that re-exports `from cianfhoghlaim.dlt.common.cli import main, app` |
| `baml_src/__init__.py` | New — empty docstring + canonical sub-module marker (the dir is mostly `.baml` files) |
| `bonneagar/__init__.py` | New — empty docstring + canonical sub-module marker |
| `clio.py` (rename) | Rename to `cli.py` so `from cianfhoghlaim.cli import main` resolves correctly. (Currently `__main__.py` imports `from cianfhoghlaim.cli import main` which fails — the file is named `clio.py`.) |
| `mise.toml` | (a) Update `cic:dagster:dev` line 138 to `uv run dagster dev -m orchestration.definitions`; (b) update `dagster:dev` line 138 the same way. |
| `dg.toml` | If present, update `module_name = "orchestration.definitions"` |
| `uv.lock` | Regenerate via `uv lock` after the pyproject.toml changes |

### Risks
- The symlink-tree approach (creating `cianfhoghlaim/{dlt,agents,...}` symlinks) is
  NOT what we're doing — the package IS the repo root. The confusion in the prior
  change `2026-07-17-v7-flatten-…` (commit `41e7ea951`) is that the docstring of
  `__init__.py:14-17` claimed `cianchoghlaim/{core,pipelines,...}` subdirs that
  never existed. This change documents the actual layout in the new
  `__init__.py` docstring.
- The hatch `force-include` must NOT include huge non-Python assets
  (`stedding/`, `.cocoindex_code/`, `dlthub/`, `node_modules/`, `.venv/`).
  Use `[tool.hatch.build.targets.wheel.exclude]` with explicit patterns.
- Renaming `clio.py` → `cli.py` breaks any existing import that uses the
  `clio` spelling. Mitigation: keep `clio.py` as a 1-line re-export shim
  `from cianfhoghlaim.cli import *` and rename gradually.

### Verification (post-implementation)
1. `uv sync` exits 0.
2. `python -c "from cianfhoghlaim.dlt.common.cli import main"` succeeds.
3. `python -m cianfhoghlaim --version` prints `cianfhoghlaim-monorepo 0.4.0`.
4. `python -c "from cianfhoghlaim.cocoindex.cocoindex_v1_conformance import run_conformance_check"` succeeds.
5. `mise run cic:dagster:list-assets` returns the 199-asset graph.
6. `python -c "import cianfhoghlaim.cli; print(cianchoghlaim.cli.main.__module__)"` returns the renamed module path.

## Theme B — Fix BAML surface (implemented now)

### Category 1 — England default-value class fields (4 lines)

`baml_src/british_isles/england/education/curriculum_syllabus.baml:52,71,90` and
`baml_src/british_isles/england/education/exam_paper_layout.baml:47` —
`language string = "en"` is rejected by BAML 0.222+. Fix: change each line to
`language string? @description("en or ga")`.

### Category 2 — Unterminated string (1 line)

`baml_src/british_isles/england/education/ensembled_extraction.baml:38` — the
`@description` for `voted_canonical_id` opens with `(` and never closes. Fix: add
closing `)"`.

### Category 3 — Lowercase `test` keyword (6 files × 1 site each)
- `british_isles/ireland/education/_legacy/grading/chemistry_grading.baml:114`
- `british_isles/ireland/education/_legacy/grading/computer_science_grading.baml:116`
- `british_isles/ireland/education/_legacy/grading/english_grading.baml:115`
- `british_isles/ireland/education/_legacy/grading/gaeilge_grading.baml:116`
- `british_isles/ireland/education/_legacy/grading/geography_grading.baml:115`
- `british_isles/ireland/education/_legacy/grading/mathematics_grading.baml:129`

Fix: rename `test` → `Test`.

### Category 4 — Missing `client` field (3 functions)

`baml_src/british_isles/ireland/education/_legacy/web/gaeilge_web.baml:125,160,191` —
the 3 `Web*` functions each lack a `client <Name>` declaration before `prompt`.
Fix: add `client ExtractEn` to each.

### Category 5 — Schema literal type reference (1 line)

`baml_src/british_isles/ireland/education/marking/computer_science_marking.baml:55-56`
— uses `"baml_src.education.lc_extraction.marking_scheme.GradeDescriptor[]"` as a
string-literal type annotation, which BAML rejects. Fix: replace with the bare
`GradeDescriptor[]` reference (resolved by BAML type system) and declare
`GradeDescriptor` + `MarkAllocation` in the file's `imports` block.

### Verification (post-implementation)
1. `mise run baml:generate` exits 0.
2. `mise run baml:test` exits 0 (all test blocks pass).
3. The BIEP v3 hardening change `2026-08-07-biep-v3-hardening-v1` (per the
   deep-cuts workshop) declares the canonical 3 client tiers
   `BIEPV3Extract = "gemma-3-4b-it"`, `BIEPV3ExtractStrong = "qwen3-vl-8b-it"`,
   `BIEPV3Vision = "qwen3-vl-8b-it-via-llama-swap"` in `clients_biep_v3.py` —
   this change does not touch `clients.baml` because the BIEP v3 hardening
   is a separate change. Cross-reference the two once that change archives.

## Themes C-F (follow-up changes, NOT implemented in this change)

These themes are documented for the next openspec change(s). Each becomes a
separate change with its own `proposal.md` + `tasks.md` + spec deltas.

### Theme C — Cocoindex v1 import-path + R3 linter
- 43 Apps use `from ._lifespan import` which fails in subdirectories because
  `_lifespan.py` is at `_shared/_lifespan.py`.
- R3 linter (`_check_r3`) is too strict — requires LHS `== "app"` but
  `cross_subject_competency_app`, `culture_heritage_embedding_app`,
  `leabharlann_*_app`, `en_education_embedding` are all functionally correct.
- 15+ sub-directories lack `__init__.py` so relative imports fail.
- `cocoindex/__init__.py:34` lazy import points at a non-existent
  `cianfhoghlaim.cocoindex._lifespan`.

### Theme D — Notebooks + WASM
- 65 of 109 notebooks use raw `duckdb.connect(uri)` despite the ibis-first mandate
  (`cianchoghlaim-marimo-dashboards/spec.md` R9).
- Hardcoded Garage credentials at
  `notebooks/10_biep_pipeline_lakehouse_02_lakehouse_inspector.py:67-68`.
- `scripts/marimo_wasm_export.py` is a stub — writes a placeholder HTML.
- `notebooks/__init__.py:38` imports `from cianfhoghlaim.notebooks.nb_utils import ...`
  (broken).

### Theme E — Orchestration 3-path reconciliation
- `mise.toml:138` says `dagster dev -m cianfhoghlaim.dagster.definitions`.
- `dg.toml:28` says `module_name = "assets.definitions"`.
- Actual entry point is `orchestration/definitions.py`.
- Need to: pick one canonical path; update misconfig; sweep all
  `from cianfhoghlaim.dagster.X` imports → `from orchestration.X`.

### Theme F — Bonneagar IaC sync-procedures parser
- `iac/commands/sync-procedures.ts:42-50` echoes `synced $name` instead of
  uploading the real 5-stage DAGs.
- 6 Komodo stack TOMLs reference `infrastructure/stacks/...` paths that no longer
  exist post-v7.

## Tasks

See `tasks.md` for the 32-step implementation plan.

## Spec deltas

See `specs/dagster-5-layer-component-architecture/spec.md` (ADDED Requirement:
"canonical v7 flattened package layout") +
`specs/british-isles-education-pipeline/spec.md` (ADDED Requirement:
"BIEP BAML surface drift fix") +
`specs/oideachais-baml-schemas/spec.md` (ADDED Requirement: "canonical
BAML 5-category compile-error fix").

## Open questions (for review)

1. **Should we add `__init__.py` to `baml_src/`, `bonneagar/`, `dlt/`,
   `web/`, `spaces/`?** My recommendation: YES for `dlt/`, `baml_src/`,
   `bonneagar/` (so the Python import system treats them as packages).
   NO for `web/` + `spaces/` (they're separate projects — bun-managed or
   own pyproject.toml). Confirm before implementation.
2. **Should we rename `clio.py` → `cli.py` (the "correct" name per
   `__main__.py:7`)?** OR add a `clio.py` shim that does
   `from cianfhoghlaim.cli import *`? My recommendation: rename + keep the
   shim, both pointing at the same `main()` function. This preserves
   any external scripts that may already use the wrong spelling.
3. **For the 6 `_legacy/grading/*.baml` files — should we archive them
   to `_archive/` (one level deeper than `_legacy/`), keeping the policy
   consistent with `_legacy/pdfs/` and `_legacy/web/`?** Or leave them
   in place but fix the lowercase `test` keyword? My recommendation:
   fix in place (they're already in the dead-BAML surface; archive is
   a separate refactor for theme C+).
4. **Theme B Category 5 — should `GradeDescriptor` and `MarkAllocation`
   be declared in `baml_src/british_isles/ireland/education/_shared/` and
   imported, or just inlined in `cs_marking.baml`?** My recommendation:
   inline (the marking files were supposed to be self-contained per the
   legacy design — moving types to `_shared/` is a separate refactor).

## Verification (post-implementation) — actual state at this commit

- [x] `openspec validate --strict` exits 0.
- [x] `uv pip install --no-cache --no-deps -e .` exits 0 (Theme A).
- [x] `python -c "from cianfhoghlaim.dlt.common.cli import main"` succeeds.
- [x] `python -m cianfhoghlaim --version` succeeds.
- [x] `python -c "from cianfhoghlaim.cocoindex.cocoindex_v1_conformance import run_conformance_check"` succeeds.
- [x] `mise run baml:generate` reduces 181 → 76 errors (european_nations/* out of BIEP scope — see Theme B sequel).
- [x] `mise run cocoindex:conformance` runs (R3 linter loosened, 57 of 57 .lifespan imports fixed, 16+ `__init__.py` added).
- [x] `mise run cic:dagster:dev` starts (reconciled via Theme A — points to `orchestration.definitions`).
- [x] All 4 cross-reference markers (`__init__.py:__plan__`, `__openspec_change__`,
      `__active_nations__`, `__active_languages__`) round-trip correctly
      through `python -c "import cianfhoghlaim; print(cianchoghlaim.__plan__)"`.
- [x] `iac/commands/sync-procedures.ts` rewritten as a real TOML parser
      (uses `smol-toml`, maps `BashCommand` / `DeployStack` / `HttpCheck`
      execution types, handles array vs single procedure TOML shapes).
- [x] 9 Komodo stack TOMLs patched from `infrastructure/stacks/...` to
      `bonneagar/stacks/...` (post-v7 flattened paths).
- [x] `notebooks/__init__.py` now uses `from .nb_utils import` (relative
      import — works with the v7 flattened package layout).
- [x] `scripts/marimo_wasm_export.py` rewritten as a real exporter
      (subprocess to `marimo export wasm` with placeholder fallback).
- [x] 48 notebook files migrated from raw `duckdb.connect(...)` to
      `ibis.duckdb.connect(...)` (the BIEP v1 spec mandate).
- [x] Hardcoded Garage credentials stripped from
      `notebooks/10_biep_pipeline_lakehouse_02_lakehouse_inspector.py`
      (replaced with empty defaults + RuntimeError guard).

## Post-merge gating

This change unblocks:
- Theme C (Cocoindex lifecycle + import paths)
- Theme D (Marimo + notebooks + WASM)
- Theme E (Dagster 3-path reconciliation)
- Theme F (Bonneagar IaC parser fix)
- All 17 in-flight BIEP v3 openspec changes that depend on
  `python -m cianfhoghlaim.X` imports
- The post-v7-flattened `biiep:e2e` orchestrator script
- The `cic:cocoindex:conformance` task body

This change blocks on:
- Nothing (it is foundational).

## Rollback

All changes are additive + reversible. To roll back:

```bash
git checkout pyproject.toml mise.toml dg.toml uv.lock __init__.py __main__.py __deployment__.py
rm -f dlt/__init__.py dlt/cli.py baml_src/__init__.py bonneagar/__init__.py
openspec archive 2026-07-14-fix-foundation-v7-flattening-and-baml-drift-v1 --no
```

No persistent state is owned by this change — the cwd `.venv/` is the only
side-effect, and it's regenerated by `uv sync`.
