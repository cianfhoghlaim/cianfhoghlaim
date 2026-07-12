# Tasks: 2026-07-17-pipeline-directory-consolidation-v1

## 1. Openspec change

- [x] 1.1 Create `openspec/changes/2026-07-17-pipeline-directory-consolidation-v1/`
- [x] 1.2 Write `proposal.md`
- [ ] 1.3 Write `cross-repo-sync.md`
- [x] 1.4 Write the 8 spec deltas
- [ ] 1.5 `openspec validate 2026-07-17-pipeline-directory-consolidation-v1 --strict` passes

## 2. British Isles collapse (every package)

For each package (`baml_src/`, `dlt/`, `orchestration/defs/1_ingestion/`, `cocoindex/`):

- [ ] 2.1 Build the jurisdiction rename map (code → full snake_case)
- [ ] 2.2 `git mv` each renamed jurisdiction dir
- [ ] 2.3 Delete the empty stub dirs (`en/`, `ni/`, `sct/`, `wls/`, `jey/`, `iom/`, `ggy/`)
- [ ] 2.4 Add `LEGACY_ALIASES.md` at the package root listing all rename mappings

## 3. baml_src migration

- [ ] 3.1 `baml_src/education/{en,ni,sct,wls,england,northern_ireland,scotland,wales,isle_of_man,jersey,guernsey,iom,jey,ggy}/` → `baml_src/british_isles/<full>/`
- [ ] 3.2 Create `baml_src/british_isles/ireland/` (lift from `dlt/british_isles/ireland/` equivalents)
- [ ] 3.3 Move `baml_src/education/law/`, `baml_src/education/statistics/`, `baml_src/education/university/`, `baml_src/education/marking/`, `baml_src/education/grading/`, `baml_src/education/web/`, `baml_src/education/pdfs/`, `baml_src/education/subjects/`, `baml_src/education/stages/`, `baml_src/education/lc_extraction/`, `baml_src/education/cross_nation/`, `baml_src/education/primary/`, `baml_src/education/junior_cycle/` → into `baml_src/british_isles/ireland/` (since these are all IE-specific) and/or `baml_src/education_cross/` (for cross-jurisdiction schemas)
- [ ] 3.4 `baml_src/european_nations/{alb,aut,...,xkx}/` → `baml_src/european_nations/<full>/`
- [ ] 3.5 `baml_src/commonwealth/{aus,can,ind,nga,nzl,zaf}/` → `baml_src/commonwealth/<full>/`
- [ ] 3.6 `baml_src/commonwealth/can/{ab,bc,...,yt}/` → `baml_src/commonwealth/canada/provinces/<full>/`
- [ ] 3.7 `baml_src/americas/` → `baml_src/american_nations/`
- [ ] 3.8 `baml_src/americas/us_us_ca/` → `baml_src/american_nations/united_states/`
- [ ] 3.9 Create `baml_src/_shared/` with the 4 truly cross-region helpers
- [ ] 3.10 Update `baml_src/baml.toml` if present
- [ ] 3.11 Add `baml_src/LEGACY_ALIASES.md`

## 4. dlt migration

- [ ] 4.1 `dlt/british_isles/{en,england,ni,northern_ireland,sct,scotland,wls,wales,jey,jersey,iom,isle_of_man,ggy,guernsey}/` → `dlt/british_isles/<full>/` (collapse dual naming)
- [ ] 4.2 `dlt/european_nations/{alb,...,xkx}/` → `dlt/european_nations/<full>/`
- [ ] 4.3 `dlt/commonwealth/{aus,can,ind,nga,nzl,zaf}/` → `dlt/commonwealth/<full>/`
- [ ] 4.4 `dlt/commonwealth/can/{ab,bc,...,yt}/` → `dlt/commonwealth/canada/provinces/<full>/`
- [ ] 4.5 `dlt/americas/{bra,mex,us,ven}/` → `dlt/american_nations/{brazil,mexico,united_states,venezuela}/`
- [ ] 4.6 Update `dlt/commonwealth/can/_shared/province.baml` callers if any
- [ ] 4.7 Add `dlt/LEGACY_ALIASES.md`
- [ ] 4.8 Add deprecation shim `__init__.py` to old ISO-3 dirs

## 5. orchestration migration

- [ ] 5.1 `orchestration/defs/1_ingestion/british_isles/{en,england,ni,northern_ireland,sct,scotland,wls,wales}/` → full names only
- [ ] 5.2 `orchestration/defs/1_ingestion/european_nations/{alb,...,xkx}/` → full names
- [ ] 5.3 `orchestration/defs/1_ingestion/commonwealth/{aus,can,ind,nga,nzl,zaf}/` → full names
- [ ] 5.4 `orchestration/defs/1_ingestion/americas/{bra,mex,us,ven}/` → `american_nations/<full>/`
- [ ] 5.5 `orchestration/defs/1_ingestion/commonwealth/can/{ab,...,yt}/` → `commonwealth/canada/provinces/<full>/`
- [ ] 5.6 Add `orchestration/defs/1_ingestion/LEGACY_ALIASES.md`

## 6. cocoindex migration (largest — flat → hierarchical)

- [ ] 6.1 Create subdirs: `_shared/`, `american_nations/`, `british_isles/{_cross,england,ireland,northern_ireland,scotland,wales,isle_of_man,jersey,guernsey}/`, `european_nations/<40>/`, `european_nations_cross/`, `commonwealth/<6>/`, `commonwealth_cross/`, `celtic/`, `subjects/`, `media/`, `portfolio/`, `knowledge_graph/`, `infrastructure/`, `corpus/`
- [ ] 6.2 `git mv cocoindex/european_nations_{alb,...,xkx}_education_embedding.py` → `cocoindex/european_nations/<full>/education_embedding.py`
- [ ] 6.3 `git mv cocoindex/european_nations_law_embedding.py` → `cocoindex/european_nations_cross/law_embedding.py`
- [ ] 6.4 `git mv cocoindex/european_nations_medicine_embedding.py` → `cocoindex/european_nations_cross/medicine_embedding.py`
- [ ] 6.5 `git mv cocoindex/commonwealth_*_education_embedding.py` → `cocoindex/commonwealth/<jurisdiction>/education_embedding.py`
- [ ] 6.6 `git mv cocoindex/commonwealth_education_embedding.py` → `cocoindex/commonwealth_cross/education_embedding.py`
- [ ] 6.7 `git mv cocoindex/americas_california_education_embedding.py` → `cocoindex/american_nations/united_states/california_education_embedding.py`
- [ ] 6.8 `git mv cocoindex/american_nations_*_education_embedding.py` → `cocoindex/american_nations/<full>/education_embedding.py`
- [ ] 6.9 `git mv cocoindex/{mathematics,chemistry,english,gaeilge,geography,computer_science,history,applied_mathematics,cross_subject_competency}_embedding.py` → `cocoindex/subjects/`
- [ ] 6.10 `git mv cocoindex/{artwork,cv}_embedding.py` → `cocoindex/media/`
- [ ] 6.11 `git mv cocoindex/{apple_photos_chunks,apple_photos_geospatial,apple_photos_metadata,ocr_aware_flow}.py` → `cocoindex/media/`
- [ ] 6.12 `git mv cocoindex/{heritage,culture_heritage}_embedding.py` → `cocoindex/portfolio/`
- [ ] 6.13 `git mv cocoindex/{cognify,multihop_search,terminology_linking,youtube_kg_embedding,file_graph}.py` → `cocoindex/knowledge_graph/`
- [ ] 6.14 `git mv cocoindex/{codebase_indexing,api_indexing,config_indexing,filesystem_indexing,storage_indexing,agents_md,agent_registry,upstream_api_surface,upstream_blog_monitor,arch_doc_cache,cocoindex_v1_conformance,academic_history_flow,test_phase0_primitives,test_youtube_kg_smoke}.py` → `cocoindex/infrastructure/`
- [ ] 6.15 `git mv cocoindex/{leabharlann_flow,leabharlann_embedding,root_pdfs_embedding,local_documents_embedding,government_circulars_embedding,university_embedding,duchas_embedding,unified_embedding}.py` → `cocoindex/corpus/`
- [ ] 6.16 `git mv cocoindex/{celtic_curriculum_embedding,ud_celtic_embedding,gaeilge_embedding,gaois_embedding,mythology_embedding}.py` → `cocoindex/celtic/`
- [ ] 6.17 `git mv cocoindex/ie_law_{courts,court_rules,judgements,legal_aid,piab}.py` → `cocoindex/british_isles/ireland/`
- [ ] 6.18 `git mv cocoindex/ireland_legal_embedding.py` → `cocoindex/british_isles/ireland/legal_embedding.py`
- [ ] 6.19 `git mv cocoindex/{languages,reranker,caighdean_standardize,repo_type_detector,repo_embedding,_lifespan,cli}.py` → `cocoindex/_shared/`
- [ ] 6.20 Add `cocoindex/LEGACY_ALIASES.md`
- [ ] 6.21 Add deprecation shim `__init__.py` at the OLD paths

## 7. notebooks migration

- [ ] 7.1 Drop numeric prefixes (01_.., 02_.., …)
- [ ] 7.2 Consolidate `10_marimo_dashboards/` + `11_marimo_dashboards_v2/` → `marimo_dashboards/`
- [ ] 7.3 Move `04_biep_motherduck/`, `05_lakehouse_inspect/`, `10_cognify/` → `data_platform/`
- [ ] 7.4 Move `07_educational_stages/` content under `educational_stages/{primary,junior_cycle,senior_cycle,tertiary}/`
- [ ] 7.5 Add `notebooks/LEGACY_ALIASES.md`

## 8. Parity CI check

- [ ] 8.1 Write `scripts/check_pipeline_parity.py`
- [ ] 8.2 Add `mise.toml` task `pipelines:parity`
- [ ] 8.3 Wire into `.github/workflows/data-platform-pr.yml` if exists

## 9. Verification

- [ ] 9.1 `mise run lint` passes
- [ ] 9.2 `mise run py:typecheck` passes
- [ ] 9.3 `mise run turbo typecheck` passes
- [ ] 9.4 `openspec validate --strict` passes for all 8 spec deltas
- [ ] 9.5 `dg list defs` enumerates all 200+ assets (no orphan defs.yaml)
- [ ] 9.6 `mise run pipelines:parity` exits 0
- [ ] 9.7 `baml-cli generate` succeeds
- [ ] 9.8 `uv run pytest` for the data-platform tests passes

## 10. Archive

- [ ] 10.1 Mark this change as `openspec archive 2026-07-17-pipeline-directory-consolidation-v1 --yes`
- [ ] 10.2 Ensure the existing `2026-07-14-rename-jurisdictions-to-full-names-v1` change adds this as a sub-task in its `tasks.md`