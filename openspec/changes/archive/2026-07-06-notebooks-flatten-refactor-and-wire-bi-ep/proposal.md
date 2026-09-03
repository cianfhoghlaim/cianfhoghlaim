# Change: 2026-07-06-notebooks-flatten-refactor-and-wire-bi-ep

## Why

The `cianfhoghlaim/notebooks/` tree has accumulated 100+ marimo
notebooks across 13+ nested subdirectories (`meaisinfhoghlaim/`,
`leaving_cert/`, `dashboards/{duckdb,education,leaving_cert,leabharlann,observability,
mmo,pdf_processing,politics,culture,other,medical,labor,law,author_archive,
official_media,technology,site_analysis}/`). Three problems are blocking
BIEP v1 (`2026-07-06-british-isles-education-pipeline-v1`) ship:

1. **Broken dev-env notebook family.** All 6 notebooks under
   `meaisinfhoghlaim/dev_env/{01..06}_*.py` use the relative
   `Path("cianfhoghlaim/agents/adk/tools/dev_env.py")` (the
   `importlib.util.spec_from_file_location` boilerplate at line 79 of
   `01_ccc_search.py`). The path resolves against the **notebook's cwd**,
   which marimo sets to the notebook directory. The user reported:

   ```
   FileNotFoundError: [Errno 2] No such file or directory:
   '/Users/.../cianfhoghlaim/notebooks/meaisinfhoghlaim/dev_env/
    cianfhoghlaim/agents/adk/tools/dev_env.py'
   ```

   So the relative path becomes
   `<notebook_dir>/cianfhoghlaim/agents/adk/tools/dev_env.py` — a path
   that doesn't exist. The notebooks only run when invoked from the
   repo root via `uv run python <nb>.py`, never via
   `marimo edit <nb>.py` from any other cwd.

2. **8× duplicated stub.** `dashboards/education/<subject>_full_pipeline.py`
   for `applied_mathematics`, `biology`, `business`, `chemistry`,
   `computer_science`, `french`, and (separately, identical except
   `physics`) — all 108 lines, all differ only in the `<subject>`
   substitution. `diff -q` confirms:
   ```
   applied_mathematics_full_pipeline.py ↔ biology_full_pipeline.py:
   identical except for the subject name
   ```
   Removing the duplication saves 864 lines and surfaces the canonical
   BIEP 6-step pipeline (DLT → BAML → CocoIndex → Cognee → marimo).

3. **Nested subdir sprawl.** The `dashboards/` tree alone has 16
   immediate children (one per domain). Half are 1–3 notebook stubs
   that share a theme; grouping them by function (BIEP / Lakehouse /
   PDF / Observability / Stages / Sources / Media / MMO) is much
   clearer for a teacher / agent who scans the dir.

This change addresses all three plus adds 2 missing BIEP-aligned
notebooks (a parameterised subject pipeline + a Cognee graph
visualiser) and makes every refactored notebook runnable both via
`marimo edit` AND as a CLI script (`python <nb>.py --subject
chemistry --year 2025`).

## What

### Phase 1 — Fix the 6 dev-env notebook imports

For each of the 6 notebooks under `meaisinfhoghlaim/dev_env/`:

- [ ] 1.1 Replace the `_run_*` cell's
      `importlib.util.spec_from_file_location` boilerplate with an
      inline absolute path:
      ```python
      from pathlib import Path
      _HERE = Path(__file__).resolve().parent
      # meaisinfhoghlaim/dev_env/<n>.py → cianfhoghlaim/agents/adk/tools/dev_env.py
      _TOOL = (
          _HERE.parents[2] / "agents" / "adk" / "tools" / "dev_env.py"
      )
      _spec = importlib.util.spec_from_file_location("dev_env", _TOOL)
      ```
      The number of `parents[N]` hops is determined by the new
      final location (see Phase 2). For Phase 1 the existing location
      requires `parents[2]`.
- [ ] 1.2 Add a module-level docstring note documenting the runtime
      contract: "Run via `marimo edit 01_ccc_search.py` from any cwd,
      OR `python 01_ccc_search.py --query 'Dagster asset'` from any cwd."

### Phase 2 — Flatten `notebooks/` into 10 functional groups

Replace the 13+ nested subdirs with the following **flat-numbered**
structure (the option the user picked: "Flatten all dashboards/* into
one `dashboards/` dir with numbered prefixes"):

```
notebooks/
├── README.md                  (rewrite to describe the new layout)
├── cli.py                     (extend list/registry)
├── nb_utils.py                (extend with import_helpers + cli_argparse)
├── __init__.py
│
├── 01_dev_env/                (the 6 dev-env demos, fixed in Phase 1)
│   ├── 01_ccc_search.py
│   ├── 02_drift_detect.py
│   ├── 03_firecrawl_refactor_discover.py
│   ├── 04_hf_best_model.py
│   ├── 05_openspec_list.py
│   └── 06_mise_lint_skills.py
│
├── 02_vision_models/          (NEW — VLMs + OCR backends for the LC PDFs)
│   ├── 01_vlm_dispatch.py             (select_ocr_backend live explorer)
│   ├── 02_ocr_model_comparison.py     (gemma-4 vs qwen3-vl vs glm-4.6v vs molmo2)
│   ├── 03_dense_ocr_benchmark.py      (WER / CER per (model, page, subject))
│   ├── 04_layout_extraction.py        (Granite-Docling DocTags)
│   ├── 05_table_extraction.py
│   └── 06_diagram_detection.py        (Molmo2-8B figure pointing)
│
├── 03_leaving_cert/           (16 BIEP LC5 subject + cross-subject analyses)
│   ├── 01_chemistry_analysis.py
│   ├── 02_computer_science_analysis.py
│   ├── 03_gaeilge_analysis.py
│   ├── 04_geography_analysis.py
│   ├── 05_mathematics_analysis.py
│   ├── 06_en_vs_ga_comparison.py
│   ├── 07_syllabus_topic_overlap.py
│   ├── 08_exam_paper_difficulty.py
│   ├── 09_marking_scheme_complexity.py
│   ├── 10_curriculum_evolution.py
│   ├── 11_runtime_comparison_llama_swap_vs_cpp.py
│   ├── 12_pdf_processing.py           (was meaisinfhoghlaim/03_pdf_processing.py)
│   ├── 13_pdf_extraction_quality.py
│   ├── 14_pdf_processing_benchmark.py
│   ├── 15_pdf_ocr_model_comparison.py
│   ├── 16_pdf_download_dashboard.py
│   └── 17_root_pdfs_explorer.py       (was root_pdfs_explorer.py)
│
├── 04_biep_motherduck/        (BIEP MotherDuck + DuckLake analytics)
│   ├── 01_curriculum_educator.py
│   ├── 02_syllabus_visualizer.py
│   ├── 03_all_nations.py
│   ├── 04_university_courses.py
│   ├── 05_marking_scheme_analyzer.py
│   ├── 06_exam_papers_explorer.py
│   ├── 07_subject_full_pipeline.py    (NEW — replaces the 8 stubs)
│   ├── 08_leabharlann_full_stack_demo.py
│   ├── 09_pipeline_e2e_test.py
│   ├── 10_leabharlann_descriptive.py
│   └── 11_dpre_lag_analysis.py
│
├── 05_lakehouse_inspect/      (DuckLake + Lance + CocoIndex stack inspection)
│   ├── 01_ducklake_explorer.py
│   ├── 02_lakehouse_inspector.py
│   ├── 03_dlt_pipeline_overview.py
│   └── 04_cocoindex_embedding_coverage.py
│
├── 06_observability/          (BIEP drift, Irish fada, Cognee KG)
│   ├── 01_baml_drift_audit.py
│   ├── 02_irish_extraction_quality.py
│   └── 03_cognee_knowledge_graph.py   (NEW — visualise cognify pass per subject)
│
├── 07_educational_stages/     (the 5 NCCA stages + cross-domain)
│   ├── 01_aistear.py
│   ├── 02_primary.py
│   ├── 03_junior_cycle.py
│   ├── 04_senior_cycle.py
│   ├── 05_tertiary.py
│   ├── 06_cross_domain.py
│   └── 07_analysis_plan_viewer.py     (NEW — render analysis_plan/*.md)
│
├── 08_sources/                (sources.yaml federation)
│   └── 01_sources_load.py
│
├── 09_official_media/         (Instagram → government resolver)
│   ├── 01_official_media.py
│   └── 02_email_inbox_triage.py
│
├── 10_mmo/                    (Tuatha MMO + mission control)
│   ├── 01_mission_control.py
│   └── 02_cianfhoghlaim_mmo_progress.py
│
├── 11_speedrun/               (SpeedRunEthereum Web3/Solidity tutorial set,
│   │                            9 challenges × Celtic-creature NFT theme)
│   ├── 00_celtic_nft.py
│   ├── 01_language_staking.py
│   ├── 02_token_shop.py
│   ├── 03_quest_randomness.py
│   ├── 04_item_exchange.py
│   ├── 05_skill_lending.py
│   ├── 06_learning_tokens.py
│   ├── 07_exam_predictions.py
│   └── 08_anonymous_voting.py
│
├── legacy/                    (1-release-cycle preservation window; deleted at archive time)
│   ├── leaving_cert_teacher_view/      (the 8 chemistry/math/.../diagram_library.py)
│   └── corpora/                        (the 5 Gemini-6 corpus overviews)
│
└── analysis_plan/             (KEEP — plan artifacts)
```

Mapping table for moves:

| From | To |
|:--|:--|
| `meaisinfhoghlaim/01_leabharlann_descriptive.py` | `04_biep_motherduck/10_leabharlann_descriptive.py` |
| `meaisinfhoghlaim/02_dpre_lag_analysis.py` | `04_biep_motherduck/11_dpre_lag_analysis.py` |
| `meaisinfhoghlaim/03_pdf_processing.py` | `03_leaving_cert/12_pdf_processing.py` |
| `meaisinfhoghlaim/dev_env/01..06_*.py` | `01_dev_env/01..06_*.py` |
| `leaving_cert/{history,chemistry,...}.py` | `legacy/leaving_cert_teacher_view/...` |
| `dashboards/duckdb/ducklake_explorer.py` | `05_lakehouse_inspect/01_ducklake_explorer.py` |
| `dashboards/duckdb/lakehouse_inspector.py` | `05_lakehouse_inspect/02_lakehouse_inspector.py` |
| `dashboards/duckdb/dlt_pipeline_overview.py` | `05_lakehouse_inspect/03_dlt_pipeline_overview.py` |
| `dashboards/duckdb/cocoindex_embedding_coverage.py` | `05_lakehouse_inspect/04_cocoindex_embedding_coverage.py` |
| `dashboards/education/curriculum_educator.py` | `04_biep_motherduck/01_curriculum_educator.py` |
| `dashboards/education/syllabus_visualizer.py` | `04_biep_motherduck/02_syllabus_visualizer.py` |
| `dashboards/education/all_nations.py` | `04_biep_motherduck/03_all_nations.py` |
| `dashboards/education/university_courses.py` | `04_biep_motherduck/04_university_courses.py` |
| `dashboards/education/marking_scheme_analyzer.py` | `04_biep_motherduck/05_marking_scheme_analyzer.py` |
| `dashboards/education/exam_papers_explorer.py` | `04_biep_motherduck/06_exam_papers_explorer.py` |
| `dashboards/leabharlann_full_stack_demo.py` | `04_biep_motherduck/08_leabharlann_full_stack_demo.py` |
| `dashboards/observability/pipeline_e2e_test.py` | `04_biep_motherduck/09_pipeline_e2e_test.py` |
| `dashboards/observability/baml_drift_audit.py` | `06_observability/01_baml_drift_audit.py` |
| `dashboards/observability/irish_extraction_quality.py` | `06_observability/02_irish_extraction_quality.py` |
| `dashboards/leaving_cert/01_chemistry_analysis.py` | `03_leaving_cert/01_chemistry_analysis.py` |
| `dashboards/leaving_cert/02_computer_science_analysis.py` | `03_leaving_cert/02_computer_science_analysis.py` |
| `dashboards/leaving_cert/03_gaeilge_analysis.py` | `03_leaving_cert/03_gaeilge_analysis.py` |
| `dashboards/leaving_cert/04_geography_analysis.py` | `03_leaving_cert/04_geography_analysis.py` |
| `dashboards/leaving_cert/05_mathematics_analysis.py` | `03_leaving_cert/05_mathematics_analysis.py` |
| `dashboards/leaving_cert/06_en_vs_ga_comparison.py` | `03_leaving_cert/06_en_vs_ga_comparison.py` |
| `dashboards/leaving_cert/07_syllabus_topic_overlap.py` | `03_leaving_cert/07_syllabus_topic_overlap.py` |
| `dashboards/leaving_cert/08_exam_paper_difficulty.py` | `03_leaving_cert/08_exam_paper_difficulty.py` |
| `dashboards/leaving_cert/09_marking_scheme_complexity.py` | `03_leaving_cert/09_marking_scheme_complexity.py` |
| `dashboards/leaving_cert/10_curriculum_evolution.py` | `03_leaving_cert/10_curriculum_evolution.py` |
| `dashboards/leaving_cert/11_ocr_model_comparison.py` | `02_vision_models/02_ocr_model_comparison.py` |
| `dashboards/leaving_cert/12_layout_extraction.py` | `02_vision_models/04_layout_extraction.py` |
| `dashboards/leaving_cert/13_dense_ocr_benchmark.py` | `02_vision_models/03_dense_ocr_benchmark.py` |
| `dashboards/leaving_cert/14_table_extraction.py` | `02_vision_models/05_table_extraction.py` |
| `dashboards/leaving_cert/15_diagram_detection.py` | `02_vision_models/06_diagram_detection.py` |
| `dashboards/leaving_cert/16_runtime_comparison_llama_swap_vs_cpp.py` | `03_leaving_cert/11_runtime_comparison_llama_swap_vs_cpp.py` |
| `dashboards/pdf_processing/pdf_extraction_quality.py` | `03_leaving_cert/13_pdf_extraction_quality.py` |
| `dashboards/pdf_processing/pdf_processing_benchmark.py` | `03_leaving_cert/14_pdf_processing_benchmark.py` |
| `dashboards/pdf_processing/pdf_ocr_model_comparison.py` | `03_leaving_cert/15_pdf_ocr_model_comparison.py` |
| `dashboards/leabharlann/pdf_download_dashboard.py` | `03_leaving_cert/16_pdf_download_dashboard.py` |
| `dashboards/aistear.py` | `07_educational_stages/01_aistear.py` |
| `dashboards/primary.py` | `07_educational_stages/02_primary.py` |
| `dashboards/junior_cycle.py` | `07_educational_stages/03_junior_cycle.py` |
| `dashboards/senior_cycle.py` | `07_educational_stages/04_senior_cycle.py` |
| `dashboards/tertiary.py` | `07_educational_stages/05_tertiary.py` |
| `dashboards/cross_domain.py` | `07_educational_stages/06_cross_domain.py` |
| `root_pdfs_explorer.py` | `03_leaving_cert/17_root_pdfs_explorer.py` |
| `sources_load.py` | `08_sources/01_sources_load.py` |
| `dashboards/official_media/official_media.py` | `09_official_media/01_official_media.py` |
| `dashboards/email_inbox_triage.py` | `09_official_media/02_email_inbox_triage.py` |
| `dashboards/mmo/mission_control.py` | `10_mmo/01_mission_control.py` |
| `dashboards/mmo/cianfhoghlaim_mmo_progress.py` | `10_mmo/02_cianfhoghlaim_mmo_progress.py` |
| `speedrun/notebooks/speedrun/00_celtic_nft.py` | `11_speedrun/00_celtic_nft.py` |
| `speedrun/notebooks/speedrun/01_language_staking.py` | `11_speedrun/01_language_staking.py` |
| `speedrun/notebooks/speedrun/02_token_shop.py` | `11_speedrun/02_token_shop.py` |
| `speedrun/notebooks/speedrun/03_quest_randomness.py` | `11_speedrun/03_quest_randomness.py` |
| `speedrun/notebooks/speedrun/04_item_exchange.py` | `11_speedrun/04_item_exchange.py` |
| `speedrun/notebooks/speedrun/05_skill_lending.py` | `11_speedrun/05_skill_lending.py` |
| `speedrun/notebooks/speedrun/06_learning_tokens.py` | `11_speedrun/06_learning_tokens.py` |
| `speedrun/notebooks/speedrun/07_exam_predictions.py` | `11_speedrun/07_exam_predictions.py` |
| `speedrun/notebooks/speedrun/08_anonymous_voting.py` | `11_speedrun/08_anonymous_voting.py` |
| `dashboards/medicine/all_nations.py` | `legacy/corpora/medicine/all_nations.py` |
| `dashboards/medical/01_medical_corpus_overview.py` | `legacy/corpora/medical/01_medical_corpus_overview.py` |
| `dashboards/law/all_nations.py` | `legacy/corpora/law/all_nations.py` |
| `dashboards/law/01_law_corpus_overview.py` | `legacy/corpora/law/01_law_corpus_overview.py` |
| `dashboards/law/02_cross_corpus_timeline.py` | `legacy/corpora/law/02_cross_corpus_timeline.py` |
| `dashboards/law/03_jurisdictional_map.py` | `legacy/corpora/law/03_jurisdictional_map.py` |
| `dashboards/law/04_pattern_detection.py` | `legacy/corpora/law/04_pattern_detection.py` |
| `dashboards/law/statute_book.py` | `legacy/corpora/law/statute_book.py` |
| `dashboards/politics/01_politics_corpus_overview.py` | `legacy/corpora/politics/01_politics_corpus_overview.py` |
| `dashboards/culture/01_culture_corpus_overview.py` | `legacy/corpora/culture/01_culture_corpus_overview.py` |
| `dashboards/technology/01_technology_corpus_overview.py` | `legacy/corpora/technology/01_technology_corpus_overview.py` |
| `dashboards/other/01_other_corpus_overview.py` | `legacy/corpora/other/01_other_corpus_overview.py` |
| `dashboards/author_archive/unified_dashboard.py` | `legacy/corpora/author_archive/unified_dashboard.py` |
| `dashboards/observability/pipeline_e2e_test.py` | `04_biep_motherduck/09_pipeline_e2e_test.py` |

### Phase 3 — Delete the 8 subject_full_pipeline stubs

- [ ] 3.1 Delete
      `dashboards/education/{applied_mathematics,biology,business,chemistry,computer_science,french}_full_pipeline.py`
      (6 × 108 LOC stubs).
- [ ] 3.2 Create `04_biep_motherduck/07_subject_full_pipeline.py` —
      the parameterised version that subsumes all 8. Takes a
      `mo.ui.multiselect` (default `["chemistry", "biology"]`) and
      executes the canonical 6-step BIEP pipeline (DLT → BAML →
      CocoIndex → Cognee → marimo) for each selected subject. Also
      wires the CLI flags `--subject chemistry --level higher --year 2025`.

### Phase 4 — Add 2 new notebooks

- [ ] 4.1 **`02_vision_models/01_vlm_dispatch.py`** — interactive
      explorer for `select_ocr_backend()` from
      `cianfhoghlaim/meaisinfhoghlaim/models/registry.py`. Given a
      PDF path, shows which of the 5 VLM backends (`gemma-4-E2B`,
      `qwen3-vl-8b`, `glm-4.6v-flash`, `molmo2-8b`, `dots.ocr`)
      would be chosen and why. Live-mode: walks the actual
      `leaving_certificate/` corpus.
- [ ] 4.2 **`06_observability/03_cognee_knowledge_graph.py`** —
      visualise the cognify pass output for each BIEP subject.
      Reads from `md:oideachais.cognee.<subject>_kg` (the Cognee
      node/edge tables) and renders an interactive force-directed
      graph using `mo.ui.altair_chart` (or NetworkX → igraph
      projection if the KG is large). Falls back to a small synthetic
      20-node KG if the table is empty.
- [ ] 4.3 **`07_educational_stages/07_analysis_plan_viewer.py`** —
      render the 5 `analysis_plan/*.md` artifacts (Aistear / Primary /
      Junior Cycle / Senior Cycle / Tertiary) as a tabbed marimo
      dashboard. Surfaces the planning metadata the user wrote
      during the earlier `ireland-primary-jc-dlt-baml-and-full-stack-demo`
      work.

### Phase 5 — Add a CLI guard to every refactored notebook

For every refactored notebook under `notebooks/{01..10}_*/`:

- [ ] 5.1 Add the following tail block (PEP 723 + argparse) that lets
      the notebook run as `python <nb>.py --subject chemistry --year 2025`
      from any cwd:
      ```python
      def _cli_main(argv: list[str] | None = None) -> int:
          """Run the notebook's main query outside the marimo server.

          Honours the same PEP 723 dependency block — uv resolves the
          inline dependencies and executes the CLI in one shot:
              uv run cianfhoghlaim/notebooks/03_leaving_cert/01_chemistry_analysis.py \\
                  --subject chemistry --year 2025
          """
          import argparse
          parser = argparse.ArgumentParser(
              prog=Path(__file__).name,
              description=__doc__,
          )
          # Notebook-specific flags go here (e.g. --subject, --year, --limit)
          args = parser.parse_args(argv)
          # Delegate to the marimo runtime
          from marimo._runtime.runtime import Kernel
          kernel = Kernel()
          return kernel.run(Path(__file__))

      if __name__ == "__main__":
          raise SystemExit(_cli_main())
      ```
- [ ] 5.2 For the 6 dev_env notebooks, expose `--query` / `--packages`
      / `--task` flags so they work as scripts:
      ```
      uv run notebooks/01_dev_env/01_ccc_search.py --query "LANCE_DB lifespan"
      uv run notebooks/01_dev_env/02_drift_detect.py --packages dlt dagster
      uv run notebooks/01_dev_env/04_hf_best_model.py --task "bge embedding"
      ```
- [ ] 5.3 For each refactored BIEP dashboard (04_biep_motherduck/*),
      expose `--subject`, `--level`, `--language`, `--year` flags.
- [ ] 5.4 For each refactored vision model notebook (02_vision_models/*),
      expose `--pdf-path`, `--model`, `--page-count` flags.

### Phase 6 — Extend `nb_utils.py` with shared helpers

- [ ] 6.1 Add `import_dev_env_tool()` — the single absolute-path
      `importlib.util.spec_from_file_location` helper. Used by the
      6 dev_env notebooks to remove 6× duplication of the broken
      boilerplate.
- [ ] 6.2 Add `connect_biep_lakehouse(use_md: bool = True) ->
      duckdb.DuckDBPyConnection` — wraps the MotherDuck / local-DuckDB
      fallback pattern that is duplicated in 12+ notebooks (every
      `_lakehouse` cell that does `try: con = duckdb.connect("md:oideachais")
      except: con = duckdb.connect(":memory:")`).
- [ ] 6.3 Add `cl_argument_parser()` — the standard argparse factory
      with the BIEP canonical flags (`--subject`, `--level`,
      `--language`, `--year`, `--pdf-path`, `--limit`). Each notebook
      imports it and adds its own custom flags.
- [ ] 6.4 Add `lc_subject_query(subject, level, language)` and
      `leabharlann_join_to_lc(...)` (already present, just export
      them more cleanly via `__all__`).

### Phase 7 — Update `cli.py`

- [ ] 7.1 Replace the hard-coded `list` subcommand with a glob walk
      over `notebooks/{01..10}_*/**/*.py` (excluding `legacy/`,
      `speedrun/`, `__pycache__`). The CLI now auto-discovers every
      refactored notebook.
- [ ] 7.2 Add a `run` subcommand that uses `uv run <nb-path>` (PEP 723
      inline deps) instead of the stub message:
      ```python
      def cmd_run(name: str) -> int:
          nb = find_notebook(name)
          return subprocess.call(["uv", "run", str(nb), *sys.argv[2:]])
      ```
- [ ] 7.3 Add a `dashboard` subcommand that delegates to
      `marimo run <nb-path>` for production deployment (the existing
      marimo-stack pipeline mounts these).

### Phase 8 — Update the README + nb_utils + cli docs

- [ ] 8.1 Rewrite `notebooks/README.md` to describe the new 10-group
      layout, the `notebooks/<group>/<NN>_<name>.py` convention, and
      the dual-mode (marimo + CLI) usage.
- [ ] 8.2 Add an `__init__.py` that re-exports the helpers from
      `nb_utils.py` so notebooks can `from cianfhoghlaim.notebooks import
      connect_biep_lakehouse`.

## Files (NEW + modified)

### New notebooks

- `notebooks/02_vision_models/01_vlm_dispatch.py`
- `notebooks/04_biep_motherduck/07_subject_full_pipeline.py`
  (replaces the 8 stubs)
- `notebooks/06_observability/03_cognee_knowledge_graph.py`
- `notebooks/07_educational_stages/07_analysis_plan_viewer.py`

### Deleted notebooks (replaced by stubs or relocated to legacy/)

- `notebooks/dashboards/education/{applied_mathematics,biology,business,chemistry,computer_science,french}_full_pipeline.py`
  (6 × 108 LOC stubs → `04_biep_motherduck/07_subject_full_pipeline.py`)
- All old paths in the mapping table above (after being moved to
  `notebooks/{01..10}_*/`).

### Modified files

- `notebooks/nb_utils.py` (extend with the 4 helpers in Phase 6)
- `notebooks/cli.py` (rewrite `list` + add `run`/`dashboard`)
- `notebooks/README.md` (rewrite)
- `notebooks/__init__.py` (NEW — re-export helpers)

### Spec delta

- `openspec/specs/oideachais-marimo-dashboards/spec.md` (the
  7 Requirements + 5 Scenarios update — see `specs/...` in this change)

## Acceptance

- `openspec validate 2026-07-06-notebooks-flatten-refactor-and-wire-bi-ep --strict`
  passes.
- `git grep "Path(\"cianfhoghlaim/agents/adk/tools/dev_env.py\")" cianfhoghlaim/notebooks/`
  returns **0 hits** (the broken relative-path import is gone).
- `git grep "from cianfhoghlaim.notebooks" cianfhoghlaim/notebooks/`
  returns ≥ 6 hits (every notebook now uses the shared `nb_utils.py`
  helpers).
- `find cianfhoghlaim/notebooks -name "*_full_pipeline.py" | wc -l`
  returns 1 (only `07_subject_full_pipeline.py` remains — the 6
  duplicates are gone). Combined with the legacy/ move, the 8
  duplicated stubs are fully eliminated.
- `find cianfhoghlaim/notebooks -maxdepth 2 -name "*.py" -not -path
  "*/legacy/*" -not -path "*/speedrun/*" -not -path "*/__pycache__/*"
  -not -path "*/analysis_plan/*" | wc -l` returns ≥ 60 (the 10
  functional groups each have a numbered roster).
- For each of the 6 dev_env notebooks:
  `cd /tmp && uv run /Users/.../cianfhoghlaim/notebooks/01_dev_env/01_ccc_search.py
   --query "Dagster asset"` succeeds (cwd-independent, dual-mode).
- For `04_biep_motherduck/07_subject_full_pipeline.py`:
  `cd /tmp && uv run .../07_subject_full_pipeline.py --subject chemistry
   --level higher --year 2025` succeeds.
- All 60+ refactored notebooks parse via
  `python -c "import ast; ast.parse(open(p).read())"`.

## Cross-references

- [`openspec/changes/2026-07-04-dev-env-setup-latest-packages-and-wire-25-notebooks/`](2026-07-04-dev-env-setup-latest-packages-and-wire-25-notebooks/)
  (the 25-notebook wire-up this change inherits from)
- [`openspec/changes/2026-07-06-british-isles-education-pipeline-v1/`](2026-07-06-british-isles-education-pipeline-v1/)
  (the BIEP v1 whose 6 LC subject notebooks this change reshapes)
- [`openspec/specs/oideachais-marimo-dashboards/spec.md`](../specs/oideachais-marimo-dashboards/spec.md)
  (the capability spec this change updates — see `specs/` delta below)
- [`.agents/skills/marimo/SKILL.md`](../../.agents/skills/marimo/SKILL.md)
  (the canonical marimo skill)
- [`.agents/skills/motherduck/SKILL.md`](../../.agents/skills/motherduck/SKILL.md)
  (the MotherDuck `md:oideachais` connection contract)
- [`.agents/skills/dlt/SKILL.md`](../../.agents/skills/dlt/SKILL.md)
  (the dlt filesystem → DuckLake sink contract for the BIEP DLT sources)
- [`.agents/skills/baml/SKILL.md`](../../.agents/skills/baml/SKILL.md)
  (the canonical 5 BAML extraction functions for the 6 LC subjects)
- [`.agents/skills/cocoindex/SKILL.md`](../../.agents/skills/cocoindex/SKILL.md)
  (the v1 App canonical pattern + the `_lifespan.py` shared home)
