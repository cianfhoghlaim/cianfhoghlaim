# Tasks — Celtic Data-Engineering + Gradio Ensemble Patterns

## Phase 0: OpenSpec
- [ ] 1. Create `openspec/changes/celtic-data-engineering-patterns/{proposal.md, tasks.md, specs/{celtic-data-engineering-pipeline,gradio-ensemble-pattern}/spec.md}`
- [ ] 2. Add 2 new capabilities to `openspec/AGENTS.md` and `openspec/project.md`
- [ ] 3. Validate: `openspec validate celtic-data-engineering-patterns --strict`

## Phase 1: Documentation (this commit)
- [ ] 4. Create `spaces/README.md` (the full pattern catalogue, ~500 lines)
- [ ] 5. Append 3-line cross-link to `spaces/STATUS.md`

## Phase 2: Marimo notebooks (this commit — skeletons with TODO data bindings)
- [ ] 6. Create `meaisinfhoghlaim/marimo/__init__.py`
- [ ] 7. Create `meaisinfhoghlaim/marimo/01_leabharlann_descriptive.py` (skeleton with 4 altair cells + 1 `mo.sql` cell)
- [ ] 8. Create `meaisinfhoghlaim/marimo/02_dpre_lag_analysis.py` (skeleton with 1 correlation heatmap + 1 line chart)
- [ ] 9. Add `[marimo]` extra to `meaisinfhoghlaim/pyproject.toml` (marimo>=0.13, altair>=5, ibis-framework[duckdb,motherduck])
- [ ] 10. Add marimo row to `meaisinfhoghlaim/AGENTS.md` "Quick routing" table

## Phase 3: Tests (this commit)
- [ ] 11. Add `meaisinfhoghlaim/tests/test_marimo_notebooks.py` — `py_compile` the 2 notebooks + assert the SQL cells reference valid table names

## Phase 4: Code artefacts (follow-up commit)
- [ ] 12. Create `oideachais/dbt_project/{dbt_project.yml, profiles.yml, models/{weekly_downloads,language_distribution,ocr_confidence_by_model}.sql, models/schema.yml, models/sources.yml}`
- [ ] 13. Add `dbt-duckdb` to `oideachais/pyproject.toml` dependencies
- [ ] 14. Create `oideachais/dagster_defs/dbt_translator.py` (CelticDagsterDbtTranslator)
- [ ] 15. Register the 3 dbt models in `oideachais/dagster_defs/definitions.py`
- [ ] 16. Add 1 asset check on `weekly_downloads` (row count > 100)
- [ ] 17. Create `meaisinfhoghlaim/pipelines/ensemble_gradio.py` with `build_ensemble_interface()`
- [ ] 18. Add unit test `meaisinfhoghlaim/tests/test_ensemble_gradio.py` (3 model stubs, 2 examples, assert outputs is a list of 3)
- [ ] 19. Create `spaces/_common/hf_hub_push.py` with `push_model_to_hub()`
- [ ] 20. Migrate 2 existing `pipeline.push_to_hub` call-sites in `meaisinfhoghlaim/ocr/` to use the new helper
- [ ] 21. Bind the 2 marimo notebooks to real data (replace TODO markers with ibis queries against `md:oideachais`)
- [ ] 22. Add `oideachais/dbt_project` to the dbt `parse` invocation in `oideachais/dagster_defs/`

## Phase 5: Tests + validation (follow-up commit)
- [ ] 23. `uv run pytest meaisinfhoghlaim/tests/test_ensemble_gradio.py oideachais/tests/test_dbt_translator.py meaisinfhoghlaim/tests/test_marimo_notebooks.py -q`
- [ ] 24. `dbt build --project-dir oideachais/dbt_project --target dev` (smoke)
- [ ] 25. `marimo edit meaisinfhoghlaim/marimo/01_leabharlann_descriptive.py` and `02_dpre_lag_analysis.py` — verify both render
- [ ] 26. Re-validate: `openspec validate celtic-data-engineering-patterns --strict`

## Phase 6: Commit + push + archive
- [ ] 27. `git pull --rebase && git add -A && git commit -m "feat(data+ml): celtic data-engineering + gradio ensemble patterns" && git push`
- [ ] 28. `openspec archive celtic-data-engineering-patterns --yes`

## Total: 28 tasks, ~1.5 weeks (this commit covers 1-11; the rest are deferred)

## Note on this change bundle (this commit)

Tasks 1, 2, 4, 5, 6, 7, 8, 9, 10, 11, 27 are completed in this commit.
Tasks 3, 12-22, 23-26, 28 are **explicitly deferred** to the follow-up
commit (Phase 4 + 5 + 6).

Validation in this commit covers the OpenSpec change bundle itself
(`openspec validate celtic-data-engineering-patterns --strict`) and the
marimo notebook parseability (`py_compile`).
