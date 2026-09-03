# Tasks — University of Galway Deep Extraction (case study + template)

## Phase 0 — OpenSpec (this document)

- [ ] 1. Create `openspec/changes/university-of-galway-deep-extraction/{proposal.md, tasks.md, specs/}` with 5 spec deltas.
- [ ] 2. Add the new capability `oideachais-university-deep-extraction` to `openspec/AGENTS.md` and `openspec/project.md`.
- [ ] 3. Validate: `openspec validate university-of-galway-deep-extraction --strict`.

## Phase 1 — BAML extraction (week 1)

- [ ] 4. Create `cianfhoghlaim/core/baml/_oideachais_src/university_extraction.baml` with 5 BAML classes (`CourseDescriptor`, `ModuleDescriptor`, `ProgrammeDescriptor`, `LecturerInfo`, `ReadingListItem`) + 4 functions (`ExtractCourseDescriptor`, `ExtractModuleDescriptor`, `ExtractProgrammeDescriptor`, `ExtractReadingList`) + 4 deterministic tests (M.Sc. AI 25/26 happy path, ISBN-13 regex, programme ECTS sum, no-LLM graceful fallback).
- [ ] 5. Run `mise run baml:generate` to regenerate the BAML client.
- [ ] 6. Verify: `from baml_client.sync_client import b; b.ExtractModuleDescriptor(...)` works against a sample UoG module page (e.g. a saved `ct516-deep-learning.html` from the local `stedding/ingest_queue/` cache).
- [ ] 7. Add 3 new evals to the `oideachais-baml-schemas` spec's "Runtime deterministic evals" Requirement: `course_code_format_regex_match`, `ects_sum_within_programme`, `module_count_within_programme`.

## Phase 2 — DLT factory + Galway source (week 1-2)

- [ ] 8. Create `cianfhoghlaim/pipelines/ingest/_oideachais_dlt_sources/_university_deep_factory.py` with the `UniversityDeepExtractionConfig` Pydantic v2 model + the `create_university_deep_extraction_source()` factory function. The factory MUST yield 5 resources (`course_pages`, `module_pages`, `programme_pages`, `handbook_pdfs`, `lecturer_pages`) and MUST call the existing `BackendRouter.bulk_scrape` from `cianfhoghlaim.core.browser`.
- [ ] 9. Create `cianfhoghlaim/pipelines/ingest/_oideachais_dlt_sources/ie/education/university_of_galway_deep.py` — the Galway case-study source. Calls the factory with the UoG config (`base_url = "https://www.universityofgalway.ie"`, `academic_year = 2025`, `catalogue_paths = ["/courses/**", "/programmes/**"]`, `school_subdomain_paths = ["/colleges/science-engineering/**", "/schools/computer-science/**", "/schools/mathematical-science/**", "/schools/education/**"]`, `handbook_root_path = "/handbooks/2025-26/"`, `programme_code_regex = "[A-Z]{2,4}\\d{3,4}"`).
- [ ] 10. Update `cianfhoghlaim/sources/_oideachais_sources.yaml` line 560-568 — change `kind: firecrawl_pages` → `kind: university_deep_extraction`; replace the `crawl: { include_paths: ["/about-us/**", ...] }` block with the new `catalogue_paths` + `school_subdomain_paths` + `handbook_root_path` fields; bump `asset_key` to `[ie, education, university, galway, deep]`.
- [ ] 11. Update `cianfhoghlaim/core/dlt/_oideachais_dlt_utils/source_factory.py` to dispatch `kind: university_deep_extraction` to `_build_university_deep_source(config_dict)`.
- [ ] 12. Verify: `python -c "from dlt_sources.ie.education.university_of_galway_deep import university_of_galway_deep_source; print(university_of_galway_deep_source().name)"` prints `"university_ie-university-galway_deep"`.
- [ ] 13. Verify: `python -c "from sources_factory import build_source; print(build_source({'kind': 'university_deep_extraction', 'university_id': 'ie-university-galway', ...}).name)"` prints the same value.

## Phase 3 — Dagster assets (week 2)

- [ ] 14. Create `cianfhoghlaim/assets/_oideachais_dagster_defs/assets/university_deep_extraction/__init__.py` exporting the 5 assets.
- [ ] 15. Create `cianfhoghlaim/assets/_oideachais_dagster_defs/assets/university_deep_extraction/uog_assets.py` with the 5 `@asset` functions:
    - `uog_pre_research` (group `university_deep_extraction`, compute_kind `scrape`) — calls `BackendRouter.pre_research(base_url, goal, budget_hint=2)`, persists to `oideachais.education.ie.university_research_sitemap` (LanceDB).
    - `uog_bulk_scrape` (group `university_deep_extraction`, compute_kind `scrape`) — calls `BackendRouter.bulk_scrape` with the `ResearchSiteMap` from pre_research.
    - `uog_extract_courses` (group `university_deep_extraction`, compute_kind `baml`) — calls `b.ExtractCourseDescriptor` per row, persists to `oideachais.education.ie.university_courses` (DuckLake). Memoised on `(url, content_hash)`.
    - `uog_extract_modules` (group `university_deep_extraction`, compute_kind `baml`) — calls `b.ExtractModuleDescriptor` per row → `oideachais.education.ie.university_modules`. Memoised.
    - `uog_extract_programmes` (group `university_deep_extraction`, compute_kind `baml`) — calls `b.ExtractProgrammeDescriptor` per row → `oideachais.education.ie.university_programmes`. Memoised.
- [ ] 16. Update `cianfhoghlaim/assets/_oideachais_dagster_defs/assets/__init__.py` to re-export the 5 new `uog_*` assets.
- [ ] 17. Verify: `from cianfhoghlaim.assets.definitions import defs; assert len([a for a in defs.assets if a.key.path[0] == "uog"]) == 5` passes.

## Phase 4 — CocoIndex v1 Apps (week 2-3)

- [ ] 18. Create `cianfhoghlaim/core/cocoindex/university_embedding.py` with the 2 v1 Apps:
    - `UniversityCoursesApp` (BGE-M3 1024-dim embedding on `course_description + learning_outcomes`) → `university_courses` LanceDB table.
    - `UniversityModulesApp` (BGE-M3 1024-dim embedding on `module_title + module_description + learning_outcomes`) → `university_modules` LanceDB table.
- [ ] 19. Register the 2 new Apps in the canonical v1 App registry (per the `oideachais-cocoindex-v1-migration` spec) so `cocoindex_v1_conformance` counts them (11 → 13).
- [ ] 20. Run `mise run cocoindex:update -- university_embedding:UniversityCoursesApp` to materialise the first batch (against a saved sample in `stedding/ingest_queue/`).
- [ ] 21. Run `mise run lint:v1-conformance`; expect pass with 13/13 Apps.
- [ ] 22. Verify: `from cianfhoghlaim.core.cocoindex import APP_REGISTRY; assert len(APP_REGISTRY) == 13` passes.

## Phase 5 — Cross-archive edge (week 3)

- [ ] 23. Create `cianfhoghlaim/cognify/rules/university_cross_archive.py` with the `UoGArtifact-MATCHES-CourseDescriptor` rule. Match condition: `(left.course_code = right.programme_code) OR (fuzzy_title_similarity(left.module_title, right.course_title) > 0.85)`.
- [ ] 24. Update `cianfhoghlaim/cognify/rules/leabharlann_cross_archive.py` to register the new rule alongside the existing 3 (`GeminiReport-CITES-ZoteroPaper`, `UoGArtifact-TEACHES-ZoteroPaper`, `TakeoutDoc-CITES-GeminiReport`).
- [ ] 25. Run the cognify pass against a sample of 10 UoG artefacts + 10 scraped course descriptors; expect ≥ 5 edges.
- [ ] 26. Verify: the rule emits the `CT511 → HDSD` edge when both nodes exist (per the `oideachais-leabharlann` MODIFIED scenario).

## Phase 6 — Marimo notebook (week 3)

- [ ] 27. Create `cianfhoghlaim/notebooks/_oideachais/university_courses.py` with 4 tabs:
    1. **M.Sc. AI 25/26 modules** — `mo.ui.table` filtered to `programme_codes = ["MSCAI"]` + `academic_year = 2025`.
    2. **All UoG courses** — `mo.ui.table` with `mo.ui.search` + `mo.ui.multiselect` filters for school / NFQ level / ECTS / stage.
    3. **Reading lists** — `mo.ui.table` with a "Group by module" vs "Group by ISBN-13" toggle (`mo.ui.radio`).
    4. **Cross-archive** — `mo.ui.table` joining `uog_coursework_artifact` ↔ `university_course_descriptor` via the new Cognee edge.
- [ ] 28. Register the new marimo app in `cianfhoghlaim/marimo/__init__.py` (or equivalent) so it mounts at `/dashboards/university-courses`.
- [ ] 29. Verify: `python -c "import ast; ast.parse(open('cianfhoghlaim/notebooks/_oideachais/university_courses.py').read())"` passes (the notebook is syntactically valid).

## Phase 7 — Tests (week 3-4)

- [ ] 30. Add `cianfhoghlaim/tests/_oideachais/test_university_deep_extraction.py` with tests for:
    - The `UniversityDeepExtractionConfig` Pydantic model (rejects missing fields, accepts valid configs, validates the `programme_code_regex` compiles).
    - The `create_university_deep_extraction_source()` factory (returns 5 resources with the correct primary keys: `(url, content_hash)` for pages, `(handbook_year, programme_code, module_code)` for handbook entries).
    - The BAML `ExtractModuleDescriptor` function (returns all 12 required fields for a sample CT516 page, graceful degradation when the BAML client is missing).
    - The 5 Dagster assets (importable with the right `group_name == "university_deep_extraction"` and `compute_kind`).
    - The 2 CocoIndex v1 Apps (pass `cocoindex_v1_conformance`).
    - The marimo notebook file (parseable, has 4 tabs, has the 4 documented tabs).
    - The `UoGArtifact-MATCHES-CourseDescriptor` cognify rule (emits the expected edges for sample inputs).
- [ ] 31. Run `mise run test -- cianfhoghlaim/tests/_oideachais/test_university_deep_extraction.py -q`; all tests pass.
- [ ] 32. Re-validate: `openspec validate university-of-galway-deep-extraction --strict`.

## Phase 8 — Documentation (week 4)

- [ ] 33. Create `cianfhoghlaim/docs/04-data-platform/university-deep-extraction.md` — the **template tutorial** (how to add a new British Isles university in 5 lines of `sources.yaml`). Include 1 worked example (Maynooth), 1 anti-pattern (commit the wrong `kind`), and a link to the marimo notebook.
- [ ] 34. Update `openspec/specs/oideachais-university-deep-extraction/spec.md` (the canonical spec, created in Phase 0 task 1) to link to the tutorial in the Cross-references section.

## Phase 9 — Commit + push + archive (week 4)

- [ ] 35. Git: `git pull --rebase`, `git add -A`, `git commit -m "feat(oideachais): University of Galway deep extraction (BAML + DLT + Dagster + CocoIndex v1 + marimo)"`, `git push`.
- [ ] 36. Run `openspec archive university-of-galway-deep-extraction --yes` to move the change to `archive/`.

## Total: 36 tasks, ~4 weeks.
