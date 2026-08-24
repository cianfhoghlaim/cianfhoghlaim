# 2026-08-24-wave-3-cocoindex-v0-stragglers-v1

## Why

Wave 0 (`2026-08-24-wave-0-cocoindex-module-path-repair-v1`) repaired the
**module-path references** in 85 L3 `defs.yaml` files, so the
`module:` strings now point to importable Python paths.

But Wave 0 surfaced a SECOND layer of issues: many of the target
modules themselves are broken because they use the **v0 CocoIndex API**
(`@coco.flow`, `@coco.App(shared_lifespan)`, `coco.AppConfig(description=...)`,
`cocoindex.connectors.lancedb`, `cocoindex.llm.IdGenerator`, etc.) which is
no longer compatible with the installed CocoIndex 1.0.20.

The 18 v0 stragglers documented in Wave 0's spec cover the
**discovered** broken files. Wave 3 actually fixes them.

Three sub-tasks:

1. **Fix the `_find_app` lookup** in
   `orchestration/components/layer3_model_lifecycle.py` — the v1 App
   stores its name in the private `_name` attribute (not in
   `obj.config.name` or `obj.name`). Without this fix, every L3
   defs.yaml still raises `cocoindex_app_not_found` even after the
   module imports cleanly.

2. **Fix the 18 v0 stragglers** + the 6 related broken files
   discovered during Wave 3. Total ~24 files:
   - 16 files: `coco.AppConfig(description=...)` → remove `description`
   - 6 files: `@coco.App(shared_lifespan)` decorator → imperative
     `coco.App(...)` calls
   - 10 files: `@coco.function(...)` → `@coco.fn(...)`
   - 4 files: missing modules created (stubs)
   - 4 files: pre-existing `baml-py` issue (NOT in Wave 3 scope)

3. **Create stub packages** for the modules referenced by L3
   defs.yaml that don't exist in `cocoindex_flows/`:
   - `cocoindex_flows/{media_personal,cultural_heritage,cv,education}/`
   - `cocoindex_flows/british_isles/_shared/`
   - `cocoindex_flows/biep_parity/{lc_subject_embedding,cross_subject_competency_embedding,en_education_embedding,...}.py`

## User preferences (locked-in from prior turns)

| Decision | Choice |
|:--|:--|
| CocoIndex v0→v1 migration scope | **All 24 files** documented in Wave 0's "v0 stragglers" inventory |
| App name resolution | **v1 `_name` private attribute** (not `obj.config.name` or `obj.name`) |
| Stubs for missing modules | **Create them as re-export shims** rather than updating defs.yaml |
| The `baml-py out of date` issue (in bi_factory.py + ireland_lc_factory.py) | **Deferred** — not a Wave 3 item; needs `pyproject.toml` `baml-py==0.223.0` pin or regen |

## Dependencies

`Blocked by: 2026-08-24-wave-0-cocoindex-module-path-repair-v1` (✅ landed commit `f0344b787`)
`Unblocks: 2026-08-24-wave-4-ducklake-v1-hardening-v1 (Lakehouse depends on CocoIndex pipeline DAG)`
`Affected repos: cianfhoghlaim` (single-repo change)

## What changes

### 1. `_find_app` rewritten for v1 App objects

`orchestration/components/layer3_model_lifecycle.py:392-413` now checks
`obj.__dict__["_name"]` first (the v1 private attribute), then falls
back to `obj.config.name` and `obj.name` for legacy apps. This
unblocks every L3 defs.yaml that previously raised
`cocoindex_app_not_found`.

### 2. v0 → v1 API fixes (24 files)

| Fix | Files |
|:--|:--|
| Remove `coco.AppConfig(description=...)` (v0 used this kwarg; v1 doesn't accept it) | `european_nations_cross/{law,medicine,education}_embedding.py`, `american_nations/united_states/california_education_embedding.py`, `commonwealth/{nigeria/education,canada/provinces/quebec/montreal_education}_embedding.py`, `commonwealth_cross/education_embedding.py`, `corpus/{duchas,local_documents}_embedding.py`, `celtic/{gaois,ud_celtic,curriculum}_embedding.py`, `biep_parity/{bi_factory,ireland_lc_factory}.py`, `british_isles/ireland/canuint_embedding.py`, `european_union/{eu_multilingual_alignment,official}_embedding.py`, `portfolio/heritage_embedding.py` |
| Convert `@coco.App(shared_lifespan)` decorator → imperative `coco.App(AppConfig(name=...), main_fn, shared_lifespan=...)` | `infrastructure/{agent_registry,agents_md}.py`, `media/{apple_photos_chunks,apple_photos_metadata,tg4_foghlaim_embedding}.py`, `knowledge_graph/youtube_kg_embedding.py` |
| Convert `@coco.function(...)` → `@coco.fn(...)` (v0 name → v1 name; strip `lifespan=` kwarg) | `british_isles/england/{ocr,edexcel,aqa}_education_embedding.py`, `media/{apple_photos_chunks,apple_photos_metadata,apple_photos_geospatial,tg4_foghlaim_embedding}.py`, `infrastructure/{agent_registry,agents_md}.py`, `subjects/junior_cycle_embedding.py`, `knowledge_graph/youtube_kg_embedding.py` |
| Add `main_fn` parameter to `coco.App(...)` calls missing it | `british_isles/england/aqa_education_embedding.py` |
| Fix dataclass field ordering (`embedding: ...` had no default after fields with defaults) | `knowledge_graph/youtube_kg_embedding.py`, `media/tg4_foghlaim_embedding.py` |
| Convert `import cocoindex.llm import IdGenerator` → `import cocoindex.resources.id import IdGenerator` | `portfolio/culture_heritage_embedding.py` |
| Convert `import cocoindex.targets.lancedb` → `import cocoindex.connectors.lancedb` | `celtic/mythology_embedding.py` |
| Re-export `MythologyEmbedding` symbol at module scope | `celtic/mythology_embedding.py` |
| Stub main_fn for v1 App that has no real main function | All 6 stub packages below |

### 3. Stub packages created

| Stub | Re-exports from |
|:--|:--|
| `cocoindex_flows/media_personal/__init__.py` + 3 sibling files | `cocoindex_flows.media.{apple_photos_chunks,apple_photos_geospatial,apple_photos_metadata}` |
| `cocoindex_flows/cultural_heritage/__init__.py` + `embedding.py` + `celtic_mythology_embedding.py` | `cocoindex_flows.portfolio.culture_heritage_embedding`, `cocoindex_flows.celtic.mythology_embedding` |
| `cocoindex_flows/cv/embedding.py` | `cocoindex_flows.media_personal` |
| `cocoindex_flows/education/__init__.py` + `tertiary/__init__.py` + `tertiary/uog/{courses,modules}.py` | Standalone stubs (Wave 2 primary examples) |
| `cocoindex_flows/british_isles/_shared/{__init__.py,_lifespan.py}` | `cocoindex_flows._shared._lifespan` |
| `cocoindex_flows/biep_parity/{lc_subject_embedding,cross_subject_competency_embedding,en_education_embedding,guernsey_education_embedding,isle_of_man_education_embedding,jersey_education_embedding,ni_education_embedding,sct_education_embedding,wls_education_embedding}.py` | Standalone stubs |
| `cocoindex_flows/infrastructure/{ocr_aware_flow,root_pdfs_embedding}.py` | Standalone stubs |
| `cocoindex_flows/biep_parity/bi_factory.py` + `ireland_lc_factory.py` | **Syntax fix** (orphaned `f""` continuations from Wave 0's `description=` removal) |

### 4. Out of scope (NOT addressed by Wave 3)

- `baml-py is likely out of date` in `bi_factory.py` and `ireland_lc_factory.py` —
  requires `pyproject.toml` `baml-py==0.223.0` pin OR `baml_client`
  regeneration via `baml-cli generate`. Deferred to a separate openspec
  change.
- The actual implementation of the 18 v0 stragglers (their real
  embedding logic) — Wave 3 only made them loadable. The full v1
  rewrite lands in Wave 3 follow-up PRs.
- `apple_photos_geospatial` requires `geoparquet` connector which is
  an optional dependency not installed in this environment.

## Verification

After Wave 3 lands:

1. `dg.load_defs(defs_root=orchestration.defs)` loads all 192 defs.yaml
   without `cocoindex_v1_module_import_failed`
2. 97 of 99 L3 defs.yaml target modules import cleanly (only
   `bi_factory.py` + `ireland_lc_factory.py` blocked by the baml-py
   pre-existing issue)
3. `_find_app` finds the v1 App in `celtic.gaeilge_embedding` (was
   previously failing with `cocoindex_app_not_found`)
4. `mise run sync:dagster` passes

## References

- Master plan: `openspec/plans/2026-08-24-master-refactor-plan.md`
- Wave 0 (unblocker): `openspec/changes/2026-08-24-wave-0-cocoindex-module-path-repair-v1/`
- Wave 0 v0 stragglers inventory: `openspec/changes/2026-08-24-wave-0-cocoindex-module-path-repair-v1/specs/cocoindex-v1-module-path-migration/spec.md`
  Requirement "v0 stragglers (deferred to Wave 3)"
