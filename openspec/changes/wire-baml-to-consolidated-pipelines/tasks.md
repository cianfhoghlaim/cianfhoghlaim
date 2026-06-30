# wire-baml-to-consolidated-pipelines — Tasks

## Phase 1 — Create the BAML project config + symlink

- [ ] 1.1 Create `cianfhoghlaim/baml/baml.toml` with the 2-generator config
- [ ] 1.2 Create `cianfhoghlaim/baml_src` as a symlink to `cianfhoghlaim/baml/`
- [ ] 1.3 Add `baml_src` to `.gitignore` (the symlink is only used at regen time)
- [ ] 1.4 Validate: `cat cianfhoghlaim/baml/baml.toml` shows the 2 generators
- [ ] 1.5 Validate: `ls -la cianfhoghlaim/baml_src` shows `baml_src -> baml/`
- [ ] 1.6 Validate: `git check-ignore cianfhoghlaim/baml_src` returns 0 (the symlink is gitignored)

## Phase 2 — Sweep consumer docstrings + comments

For each file, replace `baml_src/X.baml` references in docstrings/comments with
the canonical new path. The full mapping table is in `proposal.md`.

### 2a — DLT consumer files

- [ ] 2.1 `dlt/british_isles/ie/education/aistear.py` — sweep docstring
- [ ] 2.2 `dlt/british_isles/ie/education/primary.py` — sweep docstring
- [ ] 2.3 `dlt/british_isles/ie/education/junior_cycle.py` — sweep docstring
- [ ] 2.4 `dlt/subjects/mathematics/sources.py` — sweep docstring
- [ ] 2.5 `dlt/subjects/applied_mathematics/sources.py` — sweep docstring
- [ ] 2.6 `dlt/subjects/chemistry/sources.py` — sweep docstring
- [ ] 2.7 `dlt/subjects/physics/sources.py` — sweep docstring (verify exists)
- [ ] 2.8 `dlt/subjects/computer_science/sources.py` — sweep docstring
- [ ] 2.9 `dlt/subjects/english/sources.py` — sweep docstring
- [ ] 2.10 `dlt/subjects/gaeilge/sources.py` — sweep docstring
- [ ] 2.11 `dlt/subjects/history/sources.py` — sweep docstring
- [ ] 2.12 `dlt/subjects/geography/sources.py` — sweep docstring
- [ ] 2.13 `dlt/leabharlann/university_of_galway.py` — sweep docstring
- [ ] 2.14 `dlt/leabharlann/gemini_deep_research.py` — sweep docstring
- [ ] 2.15 `dlt/leabharlann/zotero.py` — sweep docstring (verify exists)

### 2b — Dagster consumer files

- [ ] 2.16 `dagster/assets/gaeilge_assets.py` — sweep docstring
- [ ] 2.17 `dagster/assets/chemistry_assets.py` — sweep docstring
- [ ] 2.18 `dagster/assets/computer_science_assets.py` — sweep docstring
- [ ] 2.19 `dagster/assets/english_assets.py` — sweep docstring
- [ ] 2.20 `dagster/assets/history_assets.py` — sweep docstring
- [ ] 2.21 `dagster/assets/geography_assets.py` — sweep docstring
- [ ] 2.22 `dagster/assets/applied_mathematics_assets.py` — sweep docstring
- [ ] 2.23 `dagster/assets/leabharlann_assets.py` — sweep docstring
- [ ] 2.24 `dagster/assets/leabharlann_full_stack_demo.py` — sweep docstring
- [ ] 2.25 `dagster/assets/leabharlann_email_full_stack_demo.py` — sweep docstring
- [ ] 2.26 `dagster/assets/leabharlann_inbox_assets.py` — sweep docstring
- [ ] 2.27 `dagster/assets/author_archive_assets.py` — sweep docstring
- [ ] 2.28 `dagster/assets/duchas_assets.py` — sweep docstring (verify)
- [ ] 2.29 `dagster/assets/senior_cycle_kg.py` — sweep docstring (verify)
- [ ] 2.30 `dagster/definitions.py` — sweep docstring (line 95 mentions ExtractAistearFramework)

### 2c — Agents consumer files

- [ ] 2.31 `agents/baml_integration.py` — sweep docstring
- [ ] 2.32 `agents/adk/email_triage_agent.py` — sweep docstring
- [ ] 2.33 `agents/agno/stage_teams/_shared/baml_client.py` — sweep docstring
- [ ] 2.34 `agents/agno/stage_teams/_primary.py` — sweep docstring
- [ ] 2.35 `agents/agno/stage_teams/_junior_cycle.py` — sweep docstring
- [ ] 2.36 `agents/agno/stage_teams/_senior_cycle.py` — sweep docstring
- [ ] 2.37 `agents/tuatha/tools/math_syllabus_lookup.py` — sweep docstring

### 2d — CocoIndex + notebook consumer files

- [ ] 2.38 `cocoindex/mathematics_embedding.py` — sweep docstring (if needed)
- [ ] 2.39 `cocoindex/upstream_blog_monitor.py` — sweep docstring (if needed)
- [ ] 2.40 `cocoindex/upstream_api_surface.py` — sweep docstring (if needed)
- [ ] 2.41 `cocoindex/docs_skills_consolidation.py` — sweep docstring (if needed)
- [ ] 2.42 `notebooks/leaving_cert/mathematics.py` — sweep docstring
- [ ] 2.43 `notebooks/leaving_cert/english.py` — sweep docstring
- [ ] 2.44 `notebooks/leaving_cert/gaeilge.py` — sweep docstring
- [ ] 2.45 `notebooks/leaving_cert/history.py` — sweep docstring
- [ ] 2.46 `notebooks/leaving_cert/geography.py` — sweep docstring
- [ ] 2.47 `notebooks/leaving_cert/chemistry.py` — sweep docstring
- [ ] 2.48 `notebooks/leaving_cert/computer_science.py` — sweep docstring
- [ ] 2.49 `notebooks/leaving_cert/applied_mathematics.py` — sweep docstring
- [ ] 2.50 `notebooks/meaisinfhoghlaim/03_pdf_processing.py` — sweep docstring (line 37 mentions ExtractLeavingCertSyllabus etc.)
- [ ] 2.51 `notebooks/dashboards/leabharlann_full_stack_demo.py` — sweep docstring

## Phase 3 — Validate the docstring sweep

- [ ] 3.1 `ccc search "baml_src/"` returns 0 hits in `cianfhoghlaim/dlt/` + `cianfhoghlaim/dagster/` + `cianfhoghlaim/agents/` + `cianfhoghlaim/cocoindex/` + `cianfhoghlaim/notebooks/`
- [ ] 3.2 `ccc search "baml_src/"` returns hits only in:
  - `openspec/changes/wire-baml-to-consolidated-pipelines/`
  - `openspec/specs/oideachais-baml-schemas/spec.md` (the STATUS note)
- [ ] 3.3 `grep -rln "baml_src/" cianfhoghlaim/dlt cianfhoghlaim/dagster cianfhoghlaim/agents cianfhoghlaim/cocoindex cianfhoghlaim/notebooks --include="*.py" 2>/dev/null` returns 0 hits

## Phase 4 — Document the pre-existing baml_client gap in the spec

- [ ] 4.1 Add a STATUS note to `openspec/specs/oideachais-baml-schemas/spec.md`
  documenting the pre-existing baml_client gap (1480+ BAML syntax
  validation errors prevent regeneration; tracked as
  `fix-pre-existing-baml-syntax-errors` follow-up)

## Phase 5 — Final validation

- [ ] 5.1 `ls cianfhoghlaim/baml/baml.toml` exists
- [ ] 5.2 `ls -la cianfhoghlaim/baml_src` shows the symlink → `baml/`
- [ ] 5.3 `grep -E "^baml_src$" .gitignore` returns 1 hit (or similar gitignore entry)
- [ ] 5.4 `openspec validate wire-baml-to-consolidated-pipelines --strict` passes
- [ ] 5.5 `ccc search "baml_src/aistear"` returns 0 hits in the cianfhoghlaim/ subtree