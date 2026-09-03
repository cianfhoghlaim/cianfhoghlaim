# Ireland Primary + Junior Cycle DLT/BAML Loop & Leabharlann Full-Stack Demo

## Why

This change closes two of the five top items in `sruth/oideachais/REFACTORING.md`:

1. **Primary + Junior Cycle British Isles dlt + BAML loop** (Feature 1) — the BAML schemas in `baml_src/primary.baml` and `baml_src/junior_cycle.baml` define 4 extraction functions (`ExtractPrimaryFramework`, `ExtractPrimaryLearningOutcomes`, `ExtractJCSpec`, `ExtractCBADescriptor`) but **no dlt source backs them in `sruth/oideachais/dlt_sources/ireland/`** (only `aistear.py` and `senior_cycle.py` exist). The BAML extraction is unreachable. The previous `cianfhoghlaim-oideachais-baml-first` openspec change (archived) added the BAML files but never landed the dlt sources.

2. **Leabharlann full-document processing demo** (Feature 4) — the user explicitly asked to "process sample pdfs from the leabharlann/ollscoil_na_gaillimhe and zotero process pdf documents fully indexing and analysed and further analysable iwhtin our full stack oideachais project". Today the leabharlann dlt sources discover and yield the PDFs but no asset actually processes them end-to-end through the full stack.

The third small change bundled here is **wire `b.ExtractZoteroMetadata` into `sruth/oideachais/dlt_sources/author_archive/zotero.py`** (item #11 in `sruth/oideachais/REFACTORING.md`) so the new BAML function is actually invoked from a dlt source.

## What Changes

### 1. Ireland Primary dlt source

`sruth/oideachais/dlt_sources/ireland/primary.py` — new `@dlt.source name="ireland_primary"`. Yields 4 resources (per the BAML schema classes):

- `primary_specifications` — NCCA primary curriculum spec documents (PDFs from curriculumonline.ie/en/primary/).
- `primary_strands` — strands within each curriculum area.
- `primary_learning_outcomes` — `PrimaryLearningOutcome` rows.
- `primary_curriculum_areas` — 12 curriculum areas (English, Gaeilge, Maths, SESE, SPHE, Arts, PE, etc.).

Source URLs: `https://www.curriculumonline.ie/en/primary/`, `https://ncca.ie/en/primary/`, `https://www.gov.ie/en/department-of-education/topics/primary/`.

Cached scrape (per `stedding/ingest_queue/primary/`): 12 curriculum areas × ~3 docs × 1-2 PDFs.

BAML extraction (per `baml_src/primary.baml`):
- `b.ExtractPrimaryFramework(text)` → `PrimaryCurriculumArea[]`
- `b.ExtractPrimaryLearningOutcomes(text)` → `PrimaryLearningOutcome[]`

### 2. Ireland Junior Cycle dlt source

`sruth/oideachais/dlt_sources/ireland/junior_cycle.py` — new `@dlt.source name="ireland_junior_cycle"`. Yields 3 resources:

- `jc_specifications` — NCCA JC subject specs (18 subjects × 1 spec each).
- `jc_short_courses` — 16 JC short courses (Coding, Chinese, etc.).
- `cba_tasks` — `CBATask[]` (2 CBAs per JC subject × 18 subjects = 36 tasks).

Source URLs: `https://www.curriculumonline.ie/en/junior-cycle/`, `https://ncca.ie/en/junior-cycle/`, `https://www.examinations.ie/?l=en&mc=jc&fs=c` (CBA descriptors).

BAML extraction (per `baml_src/junior_cycle.baml`):
- `b.ExtractJCSpec(text)` → `JCSubjectSpec`
- `b.ExtractCBADescriptor(text)` → `CBATask`

### 3. 2 new Dagster assets

`sruth/oideachais/dagster_defs/assets/ireland_curriculum_assets.py` (extend existing) — 2 new `@asset`s:

- `ireland_primary_raw` (group `ireland_seed`, compute_kind `dlt`) — partitions: `ireland_primary_curriculum_areas` (12 subdirs).
- `ireland_junior_cycle_raw` (group `ireland_seed`, compute_kind `dlt`) — partitions: `ireland_jc_subjects` (18 subjects).

Both register in `sruth/oideachais/dagster_defs/definitions.py`.

### 4. Wire `b.ExtractZoteroMetadata` into `zotero.py`

`sruth/oideachais/dlt_sources/author_archive/zotero.py` — add a 4th resource `arxiv_papers_baml` that invokes `b.ExtractZoteroMetadata(pdf_text, file_name, arxiv_id)` for each arXiv paper (and falls back to a stub when the BAML client is not generated). The `leabharlann_paper_metadata` Dagster asset then invokes this resource and writes the structured `ZoteroPaper` rows.

This closes `sruth/oideachais/REFACTORING.md` item #11.

### 5. Leabharlann full-stack demo asset + Marimo notebook

`sruth/oideachais/dagster_defs/assets/leabharlann_demo_assets.py` — 1 new `@asset`:

- `oideachais_cocoindex_leabharlann_full_stack_demo` — takes 2 sample PDFs:
  - `leabharlann/ollscoil_na_gaillimhe/irish/gaeilge.pdf` (Irish language exam)
  - `leabharlann/zotero/Handwritten Text Recognition (HTR) for Irish-Langu.pdf` (relevant Zotero paper)

The asset:
1. Extracts text via pymupdf
2. Calls `b.ExtractUoGArtifact` and `b.ExtractZoteroMetadata` respectively
3. Embeds the chunks via the v1 CocoIndex Apps (`LeabharlannBooksEmbedding`, `LeabharlannZoteroEmbedding`)
4. Stores the embedded chunks in LanceDB (REST endpoint at `lance-api.cianfhoghlaim.ie`)
5. Records the result metadata in a DuckDB table `leabharlann_full_stack_demo`

Asset checks (1 new asset check):
- `pdf_extraction_status == "ok"`
- `baml_extraction_status == "ok"`
- `cocoindex_chunks_count > 10`
- `lance_table_size_bytes > 1000`

`sruth/oideachais/notebooks/leabharlann_full_stack_demo.py` (new Marimo notebook) — interactive UI rendering the 5-step pipeline: text extraction preview, BAML extracted fields, top-5 similar chunks from LanceDB, status panel.

Mounted at the existing `/dashboards/leabharlann` route via the new Marimo app definition in `sruth/oideachais/marimo/`.

## Impact

| Surface | Before | After |
|:--|:--|:--|
| `sruth/oideachais/dlt_sources/ireland/primary.py` | (absent) | New — 4 dlt resources |
| `sruth/oideachais/dlt_sources/ireland/junior_cycle.py` | (absent) | New — 3 dlt resources |
| `sruth/oideachais/dlt_sources/author_archive/zotero.py` | 3 resources, no BAML | 4 resources, BAML invoked (when client generated) |
| `sruth/oideachais/dagster_defs/assets/ireland_curriculum_assets.py` | (existing senior_cycle assets) | + 2 new (primary + JC) |
| `sruth/oideachais/dagster_defs/assets/leabharlann_demo_assets.py` | (absent) | New — 1 asset + 4 asset checks |
| `sruth/oideachais/notebooks/leabharlann_full_stack_demo.py` | (absent) | New Marimo notebook |
| BAML extraction functions invoked | 2 of 12 | 4 of 12 (UOG, Gemini, Primary, JC) |
| Dagster asset groups | 16 | 16 (no new group) |
| Test files | 26 | 27 (+ 1 new) |

## Out of scope

- Features 2, 3, 5 from `sruth/oideachais/REFACTORING.md` (Cognee+FalkorDB, LanceDB blob storage, public web exposure) — separate openspec changes.
- Migrating the 10 v0 CocoIndex flows to v1 — separate change.
- Bilingual BAML (`*_ga` fields) — deferred.
- 5 British Isles nations (England, Scotland, Wales, NI, Crown Dependencies) primary/secondary dlt sources — separate change (`primary-secondary-british-isles-dlt-baml` is the queued name; this change lands the Ireland subset to prove the BAML-without-dlt loop, then the other 5 territories follow).
- FalkorDB live query API for the cross-archive graph — Feature 2 of the `REFACTORING.md` backlog.

## Cross-references

- `sruth/oideachais/REFACTORING.md` — refactor backlog (Features 1 + 4 are addressed here).
- `sruth/oideachais/STATUS.md` § 1, § 2 — the BAML × dlt × Dagster matrix and per-nation × per-cycle coverage matrix that this change updates.
- `baml_src/{primary,junior_cycle,author_archive}.baml` — the BAML schemas this change wires up.
- `sruth/oideachais/dlt_sources/ireland/{aistear,senior_cycle,leaving_cert}.py` — the existing dlt source pattern that the new `primary.py` and `junior_cycle.py` mirror.
- `sruth/oideachais/dagster_defs/assets/ie/education/curriculum_dlt_assets.py` — the existing 70+ @dlt_assets pattern that the new `ireland_curriculum_assets.py` extends.
- `docs/06-infrastructure/leabharlann-stack-overview.md` — the stack diagram that this change makes end-to-end-runnable.
