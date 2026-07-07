# Tasks: 2026-07-06-notebooks-flatten-refactor-and-wire-bi-ep

> Parent change: [proposal.md](./proposal.md)

## Phase 1 — Fix the 6 dev_env notebook imports (15 min)

For each of the 6 notebooks under the new `notebooks/01_dev_env/`:

- [ ] 1.1 Edit `notebooks/01_dev_env/01_ccc_search.py` — replace the
      `_tool_path = Path("cianfhoghlaim/agents/adk/tools/dev_env.py")`
      boilerplate (lines 79-82) with the absolute-path variant:
      ```python
      _HERE = Path(__file__).resolve().parent
      _TOOL = _HERE.parents[2] / "agents" / "adk" / "tools" / "dev_env.py"
      _spec = importlib.util.spec_from_file_location("dev_env", _TOOL)
      _mod = importlib.util.module_from_spec(_spec)
      _spec.loader.exec_module(_mod)
      ```
      The `parents[2]` hops = `01_dev_env` → `notebooks` → `cianfhoghlaim`
      → `agents/adk/tools/dev_env.py`.
- [ ] 1.2 Apply the same fix to `02_drift_detect.py` (line 76),
      `03_firecrawl_refactor_discover.py` (line 87),
      `04_hf_best_model.py` (line 83),
      `05_openspec_list.py` (line 76),
      `06_mise_lint_skills.py` (line 74).
- [ ] 1.3 Verify with: `git grep 'Path("cianfhoghlaim/agents/adk/tools/dev_env.py")'
      cianfhoghlaim/notebooks/01_dev_env/` returns 0 hits.
- [ ] 1.4 Smoke-test: `cd /tmp && uv run notebooks/01_dev_env/01_ccc_search.py
      --query "Dagster asset"` succeeds (cwd-independent).

## Phase 2 — Flatten notebooks/ into 10 functional groups (60 min)

Apply the move map from the proposal.md. For each row:

- [ ] 2.1 `git mv` the source to the target destination.
- [ ] 2.2 Open the moved file and re-anchor any
      `Path(__file__).resolve().parent` / `parents[N]` references
      that depended on the old location. For most notebooks
      these references are not present (they use `os.environ` or
      hardcoded paths); for `01_dev_env/0X_*.py` (Phase 1) and
      `nb_utils.py` (Phase 6), the re-anchor is mandatory.
- [ ] 2.3 Verify the new file imports cleanly:
      `python -c "import ast; ast.parse(open('<new-path>').read())"`.
- [ ] 2.4 For the 9 speedrun notebooks, the move is
      `notebooks/speedrun/notebooks/speedrun/0X_*.py` →
      `notebooks/11_speedrun/0X_*.py` (3-level nesting → 1-level).
      All 9 files inherit the same flat-numbered layout + CLI guard
      pattern as the BIEP notebooks, but they remain a separate
      functional group (SpeedRunEthereum Web3/Solidity tutorials).
- [ ] 2.5 Repeat for the remaining Phase-2 mapping-table rows (the
      `legacy/` moves: the 8 leaving_cert_teacher_view notebooks and
      the 5 Gemini-6 corpus overviews).

## Phase 3 — Delete the 6 subject_full_pipeline stubs (5 min)

- [ ] 3.1 `git rm notebooks/dashboards/education/{applied_mathematics,biology,business,chemistry,computer_science,french}_full_pipeline.py`
- [ ] 3.2 Verify: `find cianfhoghlaim/notebooks -name "*_full_pipeline.py"
      -not -path "*/legacy/*"` returns 1 hit (only the parameterised one).
- [ ] 3.3 Create `notebooks/04_biep_motherduck/07_subject_full_pipeline.py`
      — the parameterised version. Default subjects `["chemistry", "biology"]`,
      CLI flags `--subject <name>` `--level higher|ordinary|foundation`
      `--year <YYYY>` `--language en|ga`. Runs the 6-step BIEP pipeline
      (DLT → BAML ExtractCurriculumSyllabus → BAML ExtractExamPaperLayout →
      BAML ExtractMarkingSchemeGuideline → CocoIndex v1 App →
      Cognee cognify) per subject. Uses `nb_utils.connect_biep_lakehouse()`
      and `nb_utils.cl_argument_parser()`.

## Phase 4 — Add 4 new BIEP-aligned notebooks (60 min)

- [ ] 4.1 Create `notebooks/02_vision_models/01_vlm_dispatch.py` —
      live explorer for `select_ocr_backend()`. Walks the 6 subjects ×
      {en, ga} leaving_certificate/ corpus (12 dirs), shows the routing
      table (model × file × reason). CLI flags `--pdf-path`,
      `--page-count`. Falls back to in-memory reasoning if `meaisínfhoghlaim`
      is not importable.
- [ ] 4.2 Create `notebooks/06_observability/03_cognee_knowledge_graph.py`
      — visualises the cognify pass output per subject. Tries to read
      from `md:oideachais.cognee.<subject>_kg` (the table that the
      `lc5_<subject>_cognified` Dagster asset materialises); if
      empty, renders a 20-node synthetic KG (5 NCCA Key Competencies
      + 15 example LO nodes) so the dashboard renders offline.
      Uses `mo.ui.altair_chart` (no additional deps beyond altair).
- [ ] 4.3 Create `notebooks/07_educational_stages/07_analysis_plan_viewer.py`
      — tabbed viewer for the 5 `analysis_plan/*.md` files (Aistear,
      Primary, Junior Cycle, Senior Cycle, Tertiary). Reads the
      markdown, renders each in a `mo.ui.tabs` slot. CLI flag
      `--cycle aistear|primary|junior_cycle|senior_cycle|tertiary|all`.
- [ ] 4.4 Create `notebooks/02_vision_models/_vision_models_README.md`
      — explains the VLM dispatch contract and links to
      `.agents/skills/meaisinfhoghlaim-ocr-htr/SKILL.md`.

## Phase 5 — Add a CLI guard to every refactored notebook (90 min)

For every refactored notebook under `notebooks/{01..10}_*/`:

- [ ] 5.1 Add the `if __name__ == "__main__"` block + `_cli_main(argv)`
      function (see proposal.md Phase 5.1). Use
      `nb_utils.cl_argument_parser()` as the base argparse.
- [ ] 5.2 For the 6 dev_env notebooks, add per-notebook flags:
      - `01_ccc_search.py`: `--query`, `--limit`
      - `02_drift_detect.py`: `--packages` (repeatable)
      - `03_firecrawl_refactor_discover.py`: `--package`, `--use-local-scrapes`
      - `04_hf_best_model.py`: `--task`, `--hardware`, `--benchmark`
      - `05_openspec_list.py`: `--quadrant`
      - `06_mise_lint_skills.py`: `--path`
- [ ] 5.3 For each refactored BIEP dashboard (04_biep_motherduck/*),
      add `--subject`, `--level`, `--language`, `--year`.
- [ ] 5.4 For each vision model notebook (02_vision_models/*), add
      `--pdf-path`, `--model`, `--page-count`.
- [ ] 5.5 For each leaving_cert subject analysis (03_leaving_cert/01..05),
      add `--subject`, `--year` (defaults: subject=`chemistry`, year=`2025`).

## Phase 6 — Extend `nb_utils.py` (30 min)

- [ ] 6.1 Add `import_dev_env_tool()` — computes the absolute path to
      `agents/adk/tools/dev_env.py` from `__file__` (uses `parents[2]`).
      Returns the loaded module object. Note: this is a convenience
      helper; the Phase 1 fix is inline-only per the user's choice.
- [ ] 6.2 Add `connect_biep_lakehouse(*, use_md: bool = True) ->
      duckdb.DuckDBPyConnection` — the canonical MotherDuck / local-DuckDB
      fallback. Reads `MOTHERDUCK_ENABLED` env var; if true, connects
      to `md:oideachais` (with the `MOTHERDUCK_TOKEN` from Infisical);
      else falls back to a `:memory:` DuckDB. Wraps the 12+ duplicated
      try/except blocks across the BIEP dashboards.
- [ ] 6.3 Add `cl_argument_parser(*, description: str = "") ->
      argparse.ArgumentParser` — factory for the BIEP canonical flags
      (`--subject`, `--level`, `--language`, `--year`). Each notebook
      imports this and adds its own custom flags.
- [ ] 6.4 Add `__all__` to `nb_utils.py` (currently missing).

## Phase 7 — Update `cli.py` (20 min)

- [ ] 7.1 Replace the hard-coded `list` subcommand (currently a 9-element
      tuple) with a glob walk over `notebooks/{01..10}_*/**/*.py`
      excluding `legacy/`, `speedrun/`, `__pycache__`.
- [ ] 7.2 Add `cmd_run(name, *args)` that shells out to
      `uv run <nb-path> <args>`.
- [ ] 7.3 Add `cmd_dashboard(name)` that shells out to
      `marimo run <nb-path>` (production deployment).
- [ ] 7.4 Keep the existing `edit` subcommand (still useful for
      local dev).

## Phase 8 — Update README + nb_utils + cli docs (15 min)

- [ ] 8.1 Rewrite `notebooks/README.md` — describe the new 10-group
      layout, the numbering convention, and the dual-mode usage
      (`marimo edit` + CLI).
- [ ] 8.2 Create `notebooks/__init__.py` — re-export the 4 helpers
      from `nb_utils.py` so notebooks can
      `from cianfhoghlaim.notebooks import connect_biep_lakehouse`.
- [ ] 8.3 Update `notebooks/cli.py` docstring with the new
      10-group list and the dual-mode usage examples.

## Phase 9 — Archive-time `legacy/` cleanup (run at `openspec archive` time)

The `legacy/` preservation window is **1 release cycle** per the user's
choice. At `openspec archive 2026-07-06-notebooks-flatten-refactor-and-wire-bi-ep
--yes` time, the archive step runs:

- [ ] 9.1 Verify no caller imports anything under
      `notebooks/legacy/`: `git grep "notebooks/legacy/" -- ':!*.md'`
      returns 0 hits (allow .md mentions in this proposal).
- [ ] 9.2 `git rm -r cianfhoghlaim/notebooks/legacy/`
- [ ] 9.3 Verify: `find cianfhoghlaim/notebooks/legacy -type f`
      returns 0 hits.
- [ ] 9.4 The openspec `archive` step then updates
      `openspec/specs/oideachais-marimo-dashboards/spec.md` to remove
      the legacy/ rows from the migration table in the REMOVED
      Requirements section.

## Acceptance gates

- [ ] AG.1 `openspec validate 2026-07-06-notebooks-flatten-refactor-and-wire-bi-ep --strict`
      passes.
- [ ] AG.2 `git grep 'Path("cianfhoghlaim/agents/adk/tools/dev_env.py")' cianfhoghlaim/notebooks/`
      returns 0 hits.
- [ ] AG.3 `git grep 'from cianfhoghlaim.notebooks' cianfhoghlaim/notebooks/`
      returns ≥ 6 hits.
- [ ] AG.4 `find cianfhoghlaim/notebooks -name "*_full_pipeline.py"
      -not -path "*/legacy/*"` returns exactly 1 hit.
- [ ] AG.4b `find cianfhoghlaim/notebooks/legacy -type f | wc -l`
      returns ≥ 8 (the 8 leaving_cert_teacher_view files + the
      5 Gemini-6 corpus overviews are preserved verbatim).
      At archive time (Phase 9) this should return 0.
- [ ] AG.4c `find cianfhoghlaim/notebooks/11_speedrun -name "*.py"
      | wc -l` returns 9 (the 9 SpeedRunEthereum challenges).
- [ ] AG.5 For each of the 6 dev_env notebooks:
      `cd /tmp && uv run <repo>/notebooks/01_dev_env/0X_*.py --help`
      prints usage (cwd-independent).
- [ ] AG.6 `cd /tmp && uv run <repo>/notebooks/04_biep_motherduck/07_subject_full_pipeline.py
      --subject chemistry --level higher --year 2025` succeeds.
- [ ] AG.7 All 60+ refactored notebooks pass `python -c "import ast;
      ast.parse(open(p).read())"`.
