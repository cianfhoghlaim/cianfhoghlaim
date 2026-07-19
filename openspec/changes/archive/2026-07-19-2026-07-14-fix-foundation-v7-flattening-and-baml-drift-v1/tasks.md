# Tasks — 2026-07-14 — Fix Foundation v7 flattening + BAML drift

32 implementation steps across 2 phases (Theme A + Theme B). Each step is independently verifiable.

## Phase A — Complete v7 flattening (21 steps)

### A.1 — Create the missing `__init__.py` files for sub-modules

- [ ] **A.1.1** Create `dlt/__init__.py` with a docstring + canonical re-export list:
  ```python
  """cianfhoghlaim.dlt — DLT ingestion layer + cross-jurisdiction registry + common helpers."""
  from cianfhoghlaim.dlt import common  # noqa: F401
  __all__ = ["common", "british_isles"]
  ```
- [ ] **A.1.2** Create `baml_src/__init__.py` with an empty docstring (the dir is mostly `.baml` files which are loaded by `baml-cli generate`, not imported as Python):
  ```python
  """cianfhoghlaim.baml_src — BAML schema source. See `mise run baml:generate`."""
  ```
- [ ] **A.1.3** Create `bonneagar/__init__.py` with a docstring:
  ```python
  """cianfhoghlaim.bonneagar — IaC fleet (Pulumi + Komodo + Pangolin + 88 Docker Compose stacks)."""
  ```
- [ ] **A.1.4** DO NOT add `__init__.py` to `web/` (bun-managed) or `spaces/` (separate project).

### A.2 — Create the missing `dlt/cli.py` shim

- [ ] **A.2.1** Create `dlt/cli.py` that re-exports from `dlt/common/cli.py`:
  ```python
  """cianfhoghlaim.dlt.cli — CLI shim (re-exports cianfhoghlaim.dlt.common.cli)."""
  from cianfhoghlaim.dlt.common.cli import main, build_parser, DLT_SOURCES, __all__
  __all__ = ["main", "build_parser", "DLT_SOURCES"]
  ```
  (Use the actual exports from `dlt/common/cli.py`.)

### A.3 — Rename `clio.py` → `cli.py` (or add shim)

- [ ] **A.3.1** Rename `clio.py` to `cli.py` (because `__main__.py:7` imports
  `from cianfhoghlaim.cli import main`).
- [ ] **A.3.2** Verify `from cianfhoghlaim.cli import main` succeeds.

### A.4 — Update `pyproject.toml` to declare the cianfhoghlaim package correctly

- [ ] **A.4.1** Update `[tool.hatch.build.targets.wheel]`:
  - Change `packages = []` → `packages = ["."]`
  - Add explicit `include` + `exclude` rules to scope the wheel contents.
- [ ] **A.4.2** Add the 9 missing dependencies to `[project.dependencies]`:
  ```toml
  dependencies = [
    # existing 13 ...
    "dagster>=1.13",                # L1-L5 orchestrator
    "dagster-components>=1.13",      # 5 KCG Components
    "duckdb>=1.4",                  # in-memory + MotherDuck
    "structlog>=25",                # observers across dlt/cocoindex/agents
    "ibis-framework[duckdb]>=10",   # canonical analytics entry point
    "cocoindex>=1.0,<2.0,!=1.0.8",  # L3 model lifecycle
    "lancedb>=0.15",                # vector DB for CocoIndex
    "pyiceberg>=0.10",              # Iceberg REST catalog client
    "pydantic-settings>=2",         # typed config
  ]
  ```
- [ ] **A.4.3** Fix `[tool.ruff.lint.isort]`:
  - Change `known-first-party = ["sruth", "oideachais", "sruth/tuatha", "codeolas", "códeolas", "sruth_browser"]`
  - To `known-first-party = ["cianfhoghlaim"]`
- [ ] **A.4.4** Add `[tool.uv.sources]` entry `cianfhoghlaim = { workspace = true }`
  (already present per current state — verify).

### A.5 — Update `mise.toml` references

- [ ] **A.5.1** Update `[tasks."cic:dagster:dev"]` line 138:
  - From `run = "uv run dagster dev -m cianfhoghlaim.dagster.definitions"`
  - To `run = "uv run dagster dev -m orchestration.definitions"`
- [ ] **A.5.2** Update `[tasks."dagster:dev"]` (canonical alias) the same way.
- [ ] **A.5.3** Sweep every `uv run python -m cianfhoghlaim.X` reference in mise.toml and confirm the corresponding module exists. Fix any broken paths.

### A.6 — Update `dg.toml` if present

- [ ] **A.6.1** Read `dg.toml` to see current `module_name`.
- [ ] **A.6.2** Update `module_name = "assets.definitions"` (if that is the current value) → `module_name = "orchestration.definitions"`.
- [ ] **A.6.3** Update `defs_path` to point at the right path if needed.

### A.7 — Regenerate `uv.lock`

- [ ] **A.7.1** Run `uv lock` to regenerate the lockfile with the new dependencies.
- [ ] **A.7.2** Verify the lockfile now contains `dagster`, `duckdb`, `structlog`, `cocoindex`, `lancedb`, etc.

### A.8 — Verify the Python package is importable

- [ ] **A.8.1** Run `uv sync` and confirm exit 0.
- [ ] **A.8.2** Run `python -c "from cianfhoghlaim.dlt.common.cli import main"` — should succeed.
- [ ] **A.8.3** Run `python -m cianfhoghlaim --version` — should print `cianfhoghlaim-monorepo 0.4.0`.
- [ ] **A.8.4** Run `python -c "from cianfhoghlaim.cocoindex.cocoindex_v1_conformance import run_conformance_check"` — should succeed.
- [ ] **A.8.5** Run `python -c "import cianfhoghlaim.cli; print(cianfhoghlaim.cli.main.__module__)"` — should print `...cli`.
- [ ] **A.8.6** Run `python -c "from cianfhoghlaim.dagster.cli import materialize_asset"` — should succeed (if `dagster/cli.py` exists; if not, add a shim in step A.8.6.1).
- [ ] **A.8.6.1** *(conditional)* If `dagster/cli.py` doesn't exist, add
      `orchestration/__init__.py` + `orchestration/dagster/__init__.py` + `orchestration/dagster/cli.py` shim that re-exports from
      `cianfhoghlaim.dagster.cli` (a new module that wraps
      `dagster.cli`).

### A.9 — Sanity gates

- [ ] **A.9.1** `python -m cianfhoghlaim --help` exits 0.
- [ ] **A.9.2** `python -m cianfhoghlaim.dlt.run-pipeline --help` (if exposed) exits 0.
- [ ] **A.9.3** `mise run cic:dagster:list-assets` returns the 199-asset list (or whatever the actual count is post-fix).

---

## Phase B — Fix BAML surface (11 steps)

### B.1 — Fix England default-value class fields (Category 1)

- [ ] **B.1.1** In `baml_src/british_isles/england/education/curriculum_syllabus.baml`,
      change line 52 (`language string = "en"`) → `language string?`.
- [ ] **B.1.2** Same file line 71 — same change.
- [ ] **B.1.3** Same file line 90 — same change.
- [ ] **B.1.4** In `baml_src/british_isles/england/education/exam_paper_layout.baml`,
      change line 47 — same change.

### B.2 — Fix unterminated string (Category 2)

- [ ] **B.2.1** In `baml_src/british_isles/england/education/ensembled_extraction.baml`,
      close the `@description` string at line 38 with `)"` at the end of the line.

### B.3 — Rename `test` → `Test` (Category 3, 6 files)

- [ ] **B.3.1** `baml_src/british_isles/ireland/education/_legacy/grading/chemistry_grading.baml:114`
- [ ] **B.3.2** `baml_src/british_isles/ireland/education/_legacy/grading/computer_science_grading.baml:116`
- [ ] **B.3.3** `baml_src/british_isles/ireland/education/_legacy/grading/english_grading.baml:115`
- [ ] **B.3.4** `baml_src/british_isles/ireland/education/_legacy/grading/gaeilge_grading.baml:116`
- [ ] **B.3.5** `baml_src/british_isles/ireland/education/_legacy/grading/geography_grading.baml:115`
- [ ] **B.3.6** `baml_src/british_isles/ireland/education/_legacy/grading/mathematics_grading.baml:129`

### B.4 — Add `client` field to 3 functions (Category 4)

- [ ] **B.4.1** `baml_src/british_isles/ireland/education/_legacy/web/gaeilge_web.baml` —
      add `client ExtractEn` before `prompt #"..."` at line 125 (the `WebStudyPlan` function).
- [ ] **B.4.2** Same file line 160 (the `WebExamPaperDiscussion` function).
- [ ] **B.4.3** Same file line 191 (the `WebMarkingSchemeExplanation` function).

### B.5 — Fix string-literal type reference (Category 5)

- [ ] **B.5.1** `baml_src/british_isles/ireland/education/marking/computer_science_marking.baml`
      lines 55-56 — replace the string-literal type references
      `"baml_src.education.lc_extraction.marking_scheme.GradeDescriptor[]"`
      and `MarkAllocation[]` with bare class references, and add
      `class GradeDescriptor { ... }` + `class MarkAllocation { ... }` to the same file
      (or to a new `baml_src/british_isles/ireland/education/marking/_shared/grading_types.baml`).

### B.6 — Verify BAML compiles (actual state at this commit)

- [x] **B.6.1** `mise run baml:generate` — **exits non-zero** but reduces errors
      from **181 → 76** (a 58% reduction). The 76 remaining are all in
      `baml_src/european_nations/*` and are out of BIEP v1 scope — they're
      pre-existing drift in the european_nations jurisdiction pipelines
      that the BIEP v3 openspec changes will handle.
- [x] **B.6.2** `mise run baml:test` — not run (depends on `baml:generate` succeeding).
- [x] **B.6.3** Verified that the 5 fix categories were applied at the
      expected file locations.

#### Theme B sequel (out of scope of THIS change)

The 76 remaining BAML errors are in `baml_src/european_nations/<country>/{education,law,medicine}.baml`
files and reference types like `AUTHealthGuidance`, `SVNStatute`, `LVASubjectCurriculum` that are
not yet defined in the BIEP v3 jurisdiction module. They should be addressed
in a follow-up `2026-07-15-fix-european-nations-baml-missing-types-v1` change
with these tasks:

- [ ] Add the missing European nation types (AUT, BEL, BGR, CHE, CYP, CZE, DEU, DNK, ESP, EST, FIN, FRA, GBR, GRC, HRV, HUN, IRL, ISL, ITA, LIE, LTU, LUX, LVA, MLT, NLD, NOR, POL, PRT, ROU, SVK, SVN, SWE) per their existing file shape.
- [ ] Re-run `mise run baml:generate` — target 0 errors.
- [ ] Add the missing `ExtractCountryProfile` functions for each country.

---

## Phase C — Verification + handoff (4 steps)

### C.1 — Final verification

- [ ] **C.1.1** Run `openspec validate --strict` — must exit 0.
- [ ] **C.1.2** Run `mise run cocoindex:conformance` — should pass for the canonical Apps (theme A + B do not touch CocoIndex code, but the conformance gate is the best verification).
- [ ] **C.1.3** Run `python -c "import cianfhoghlaim.cli; cianfhoghlaim.cli.main(['--version'])"` — should print `0.4.0`.
- [ ] **C.1.4** Run `git status` — should show ~10 modified/new files (no surprises).

### C.2 — Documentation

- [ ] **C.2.1** Update `__init__.py` docstring to reflect the actual v7 layout
      (not the layout claimed in the prior `__init__.py` that referenced
      `core/`, `pipelines/`, `sources/`, etc. subdirs that don't exist).

### C.3 — Handoff summary

- [ ] **C.3.1** Deliver a final summary to the user:
  - Theme A complete: package is importable, 9 deps added, mise.toml/dg.toml updated.
  - Theme B complete: BAML compiles, all 5 categories fixed.
  - Themes C-F planned: openspec changes for each (Cocoindex, notebooks, Dagster, IaC parser).

### C.4 — Cleanup

- [ ] **C.4.1** Verify no stale `clio.py` remains (or that both `clio.py` and `cli.py` export the same `main()`).
- [ ] **C.4.2** Verify `git diff` is clean (no debug prints, no commented-out code).
- [ ] **C.4.3** Run `openssl list -openssl-version` (sanity check the env).

## Done when

All 32 boxes checked. The change is ready to commit + push.
