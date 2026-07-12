# 2026-07-17-pipeline-directory-consolidation-v1

## Why

The data-platform packages — `baml_src/`, `dlt/`, `orchestration/`,
`cocoindex/`, `notebooks/` — have grown into an inconsistent topology
that no longer reflects the v7 post-consolidation reality. Three
failure modes:

### 1. British Isles has dual naming across every package

The same country exists under BOTH an ISO / legacy slug AND a full name
in all four data-platform packages. The orphan slug directories are
empty stubs:

| Jurisdiction | Slug dir | Full-name dir |
|:--|:--|:--|
| England | `en/` (1 subdir) | `england/` (4 subdirs) |
| Scotland | `sct/` (1 subdir) | `scotland/` (4 subdirs) |
| Wales | `wls/` (1 subdir) | `wales/` (4 subdirs) |
| Northern Ireland | `ni/` (1 subdir) | `northern_ireland/` (4 subdirs) |
| Isle of Man | `iom/` (empty) | `isle_of_man/` (4 subdirs) |
| Jersey | `jey/` (empty) | `jersey/` (4 subdirs) |
| Guernsey | `ggy/` (empty) | `guernsey/` (4 subdirs) |

This appears in `baml_src/education/`, `dlt/british_isles/`,
`orchestration/defs/1_ingestion/british_isles/`, AND
`baml_src/education/{en,england,ni,northern_ireland,sct,scotland,
wls,wales,ggy,guernsey,iom,isle_of_man,jey,jersey}/`.

### 2. European nations + commonwealth use ISO 3-letter codes 3 layers deep, but cocoindex is flat

`baml_src/european_nations/{alb,aut,...,xkx}/`, `dlt/european_nations/{alb,aut,...,xkx}/`, and `orchestration/defs/1_ingestion/european_nations/{alb,aut,...,xkx}/` mirror the same 40 ISO-3 directories.

Meanwhile `cocoindex/european_nations_{alb,aut,...,xkx}_education_embedding.py` — **41 files at root**, no subdirectory. The 113 files at `cocoindex/` root are a flat sea of jurisdiction prefixes.

### 3. Education content for British Isles is split across `baml_src/education/` and `dlt/british_isles/`

- `baml_src/education/{en,ni,sct,wls,england,northern_ireland,scotland,wales,...}/` (mix of codes + full names)
- `dlt/british_isles/ireland/`, `dlt/british_isles/{england,northern_ireland,scotland,wales,isle_of_man,jersey,guernsey}/`

No single canonical home.

### 4. `_shared/` is fragmented across 8 directories

Each region + each sub-region has its own `_shared/` (private helper module). The total surface is 8 × ~5 files = ~40 helper files when ~12 would suffice if consolidated.

### 5. Notebooks mix three conventions

Numeric-prefix (`01_dev_env/`, `02_vision_models/`), topic-named (`leaving_cert/`), and bare filename (`ie_law_explorer.py` at root, `nb_utils.py` at root).

## What

This change consolidates the data-platform directory topology into one canonical hierarchy with full-name jurisdiction naming and matches it across all four packages + notebooks. It also adds a CI parity check that fails when any layer drifts out of sync.

### Naming convention

| Layer | Convention | Example |
|:--|:--|:--|
| Region | lowercase singular | `european_nations/`, `commonwealth/`, `british_isles/`, `american_nations/` |
| Jurisdiction | snake_case full name | `germany/`, `northern_ireland/`, `isle_of_man/` |
| Sub-state (where distinct) | snake_case | `lagos/`, `ontario/`, `quebec/` |
| Domain | singular noun | `education/`, `law/`, `medicine/`, `statistics/`, `government/` |
| Cross-jurisdiction app | `_cross/` suffix | `european_nations_cross/law_embedding.py` |

### Renames — `baml_src/`

| From | To |
|:--|:--|
| `baml_src/americas/` | `baml_src/american_nations/` |
| `baml_src/education/{en,ni,sct,wls,ggy,iom,jey,england,northern_ireland,scotland,wales,isle_of_man,guernsey,jersey}/` | `baml_src/british_isles/{england,northern_ireland,scotland,wales,isle_of_man,jersey,guernsey}/` + `baml_src/british_isles/ireland/` (new) |
| `baml_src/european_nations/{alb,...,xkx}/` | `baml_src/european_nations/{albania,...,kosovo}/` (40 ISO-3 → full snake_case names) |
| `baml_src/commonwealth/{aus,can,ind,nga,nzl,zaf}/` | `baml_src/commonwealth/{australia,canada,india,nigeria,new_zealand,south_africa}/` |
| `baml_src/commonwealth/can/{ab,bc,...,yt}/` | `baml_src/commonwealth/canada/provinces/{alberta,..,yukon}/` |
| `baml_src/commonwealth/nga/_shared/nigeria_states.baml` | `baml_src/commonwealth/nigeria/states/_states.baml` |
| `baml_src/education/usa_us_ca/` (compound code hack) | `baml_src/american_nations/united_states/california.baml` |

The `_shared/` per-region directories (`baml_src/commonwealth/_shared/`, `baml_src/european_nations/_shared/`, `baml_src/education/_shared/`, `baml_src/processing/_shared/`, `baml_src/european_union/_shared/`, `baml_src/americas/_shared/`) **remain per-region** — they encode region-specific helpers (jurisdiction.baml, province.baml, strand_catalog.yaml). We add a new `baml_src/_shared/` for the 4 truly cross-region helpers (`semantic_search.baml`, `document_metadata.baml`, `content_types.baml`, `eiraic_treasures.baml`).

### Renames — `dlt/`

Same jurisdiction renames as `baml_src/` plus:
- `dlt/british_isles/{en,england,ni,northern_ireland,sct,scotland,wls,wales,jey,jersey,iom,isle_of_man,ggy,guernsey}/` → collapse to single full-name dirs only
- `dlt/commonwealth/{aus,can,ind,nga,nzl,zaf}/` → full names
- `dlt/commonwealth/can/{ab,...,yt}/` → `dlt/commonwealth/canada/provinces/{alberta,...,yukon}/`
- `dlt/americas/` → `dlt/american_nations/`
- `dlt/commonwealth/can/quebec/` (already a subdir) → `dlt/commonwealth/canada/provinces/quebec/`? **No** — keep as-is, the existing `quebec/` subdir already represents the province; just move it under `provinces/` once we establish the parent.

### Renames — `orchestration/defs/1_ingestion/`

Same jurisdiction renames. Domain-specific directories that are NOT jurisdiction-keyed (`law/`, `medicine/`, `marking/`, `government/`, `site_analysis/`, `legal_research/`, `university/`) are kept as-is — they reference IE-specific or subject-specific defs.yaml files.

### Renames — `cocoindex/`

The biggest change: 113 files at root → ~9 subdirectories.

```
cocoindex/
├── _shared/                            # NEW
├── american_nations/                   # NEW
├── british_isles/                      # NEW (the 8 nations + cross)
│   ├── _cross/                         # cross-jurisdiction BIEP app
│   ├── england/
│   ├── ireland/
│   ├── northern_ireland/
│   ├── scotland/
│   ├── wales/
│   ├── isle_of_man/
│   ├── jersey/
│   └── guernsey/
├── european_nations/                   # NEW
│   └── <40 jurisdictions>/
├── european_nations_cross/             # NEW (renamed from root: european_nations_law_embedding.py etc.)
├── commonwealth/                       # NEW
│   └── <6 jurisdictions>/
├── commonwealth_cross/                 # NEW
├── celtic/                             # NEW
├── subjects/                           # NEW (mathematics, chemistry, …)
├── media/                              # NEW (artwork, cv, apple_photos, ocr_aware_flow)
├── portfolio/                          # NEW (heritage, culture_heritage)
├── knowledge_graph/                    # NEW (cognify, multihop_search, youtube_kg)
├── infrastructure/                     # NEW (codebase_indexing, api_indexing, filesystem_indexing, …)
├── corpus/                             # NEW (leabharlann, root_pdfs, government_circulars, duchas, unified)
└── biep_parity/                        # KEEP (already a subdir; the 7 nation embeddings)
```

Cross-jurisdiction apps get the `_cross/` suffix:
- `cocoindex/european_nations_law_embedding.py` → `cocoindex/european_nations_cross/law_embedding.py`
- `cocoindex/european_nations_medicine_embedding.py` → `cocoindex/european_nations_cross/medicine_embedding.py`
- `cocoindex/commonwealth_education_embedding.py` → `cocoindex/commonwealth_cross/education_embedding.py`
- `cocoindex/american_nations_california_education_embedding.py` → `cocoindex/american_nations/united_states/california_education_embedding.py`

### Renames — `notebooks/`

Drop numeric prefixes; consolidate the dual `10_marimo_dashboards/` + `11_marimo_dashboards_v2/` into a single `marimo_dashboards/`. Add topical structure:

| From | To |
|:--|:--|
| `01_dev_env/` | `dev_env/` |
| `02_vision_models/` | `vision_models/` |
| `03_leaving_cert/` + `leaving_cert/` | `leaving_cert/` (canonical, absorbs both) |
| `04_biep_motherduck/` | `data_platform/biep_motherduck/` |
| `05_lakehouse_inspect/` | `data_platform/lakehouse_inspect/` |
| `06_observability/` | `observability/` |
| `07_educational_stages/` | `educational_stages/{primary,junior_cycle,senior_cycle,tertiary}/` |
| `08_sources/` | `sources/` |
| `09_official_media/` | `official_media/` |
| `10_cognify/` | `data_platform/cognify/` |
| `10_marimo_dashboards/` + `11_marimo_dashboards_v2/` | `marimo_dashboards/` (consolidated) |
| `10_mmo/` | `mmo/` |
| `11_speedrun/` | `speedrun/` |
| `12_ireland_law/` | `ireland_law/` |
| `12_semantic_search/` | `semantic_search/` |
| `12_subject_study_tools/` | `subject_study_tools/` |
| `13_baml_cocoindex_tutorial/` | `baml_cocoindex_tutorial/` |
| `14_academic_history/` | `academic_history/` |
| `16_celtic_language/` | `celtic_language/` |
| `analysis_plan/` | KEEP |
| `legacy/` | KEEP |

### Backward compatibility

Every renamed directory gets a deprecation shim:

- **Python packages** (`dlt/`, `cocoindex/`, `orchestration/`): a stub `__init__.py` emits `DeprecationWarning` and re-exports from the new path.
- **BAML** (`baml_src/`): baml.toml `search_paths` + `baml_pkg` aliases route old references to new files; class/function names already covered by the existing `2026-07-14-rename-jurisdictions-to-full-names-v1` change.
- **Notebooks**: a `LEGACY_ALIASES.md` at `notebooks/LEGACY_ALIASES.md` documents the rename. No code shim needed (notebooks are leaf artefacts).

### Parity CI check (NEW)

Add `mise run pipelines:parity` (under `scripts/check_pipeline_parity.py`) that:
1. Walks `baml_src/{european_nations,commonwealth,british_isles,american_nations,european_union}/`
2. Walks `dlt/{european_nations,commonwealth,british_isles,american_nations}/`
3. Walks `orchestration/defs/1_ingestion/{european_nations,commonwealth,british_isles,american_nations}/`
4. Walks `cocoindex/{european_nations,commonwealth,british_isles,american_nations}/`
5. Emits a 4-column CSV (`jurisdiction`, `baml_src`, `dlt`, `orchestration`, `cocoindex`)
6. Exits non-zero if any cell is `MISSING` (configurable via env var `PIPELINE_PARITY_STRICT=1`)

The check is **advisory only** for the first release (any jurisdiction may have layers in-progress); strict mode is opt-in.

## Why now

The v7 flattening just landed — `baml_src/`, `dlt/`, `orchestration/`, `cocoindex/`, `notebooks/` are at the repo root with no nesting, so the path-rewrite surface is small. The existing `2026-07-14-rename-jurisdictions-to-full-names-v1` change renamed the **display strings** (BAML class + function names, Python class names, docstrings); this change is the **directory** complement.

## Dependencies

Blocked by:
- `2026-07-17-v7-flatten-cianfhoghlaim-merge-bonneagar-rewrite-readme-license-v1` (must archive first; provides the flat-root context this change assumes)

## Cross-repo

No cross-repo impact. `leabharlann/` (separate repo) does not reference these directories. `bonneagar/` is IaC only.

## Out of scope

- Renaming the `baml_src/`, `dlt/`, `orchestration/`, `cocoindex/`, `notebooks/` directories themselves.
- Renaming cross-jurisdiction app names (e.g., `cocoindex/commonwealth_education_embedding.py` → `cocoindex/commonwealth_cross/education_embedding.py` IS in scope; renaming the underlying LanceDB table `oideachais.lc.<subject>` is OUT of scope and belongs in `oideachais-pipeline/spec.md` separately).
- BAML class + function name renames (covered by `2026-07-14-rename-jurisdictions-to-full-names-v1`).
- Renaming jurisdiction-specific `_shared/` files (`province.baml`, `jurisdiction.baml`) — keep their semantics, only move them.