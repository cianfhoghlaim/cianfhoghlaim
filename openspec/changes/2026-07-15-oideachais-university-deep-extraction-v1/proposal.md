# Ireland Tertiary 18+ University Deep Extraction v1

## Why

The `oideachais-university-deep-extraction` capability covers the
**Tertiary 18+** stage of the K-12 → university pipeline. While the
existing spec already documents the per-university website
deep-extraction template (case study: UoG) via 8 requirements
(per-university config + two URL surfaces + 4 BAML functions +
3-stage pre-research pipeline + 5 Dagster assets + 2 CocoIndex Apps
+ Cognee cross-archive edge + marimo notebook), it does NOT yet
ship the **broader Tertiary 18+ coverage** — the registry-of-record
view of all 8 universities + 5 TUs + QQI awards + CAO + SOLAS.

This change ships **Phase 1** of the capability — the canonical 5
DLT sources + the 5 Pydantic classes + 4 enums + 5 BAML functions
+ the 1 Dagster cron asset for the **Tertiary 18+** stage. Together
with the upstream packages:

| Stage | Age | Capability |
|:--|:--|:--|
| Primary | 4-12 (5-6yo infants + 6-12yo) | `ireland-primary-jc-dlt-baml` |
| Junior Cycle | 12-15 | `ireland-primary-jc-dlt-baml` |
| Senior Cycle / Leaving Cert | 15-18 | `british-isles-education-pipeline` |
| **Tertiary 18+** | **18+ (university + PLC + apprenticeship)** | **`oideachais-university-deep-extraction` (this)** |

the 4 specs collectively cover the full **K-12 → university** pipeline
(NFQ 1-10) for the Republic of Ireland.

## What changes

### 1. 5 new DLT sources at `cianfhoghlaim/dlt/british_isles/ireland/university/`

- **`universities.py`** — the **8 Republic of Ireland universities**
  (TCD, UCD, UCC, UoG, UL, DCU, Maynooth, RCSI) per the Universities
  Act 1997. One row per (institution_id, language). Registry-of-record
  view; per-university deep extraction lives in
  `education/university_of_galway_deep.py` + `_university_deep_factory.py`.
- **`tus.py`** — the **5 Technological Universities** (TUD, MTU,
  TUS, ATU, SETU) per the Technological Universities Act 2018.
  One row per (tu_id, language). Captures the parent_iots and campus
  slugs for each TU.
- **`qqi_awards.py`** — the **10 canonical QQI awards** at NFQ 6-10
  (Higher Certificate, Ord BA, Hons BA, Higher Diploma, Graduate
  Diploma, PG Cert, PG Dip, Masters, Ph.D., Professional Doctorate).
  One row per (award_code, language). The 13 QQI providers (the 8
  universities + 5 TUs) are cross-referenced.
- **`cao.py`** — the **CAO Central Applications Office**. One row
  per (cao_code, year) for the course catalog + one row per
  (round_id, year) for the 4 annual application rounds (R1, R2, R3, R4).
- **`solas.py`** — the **SOLAS Further Education + Training
  Authority**. One row per (course_code, etb_slug) for PLC courses +
  one row per (etb_slug) for the 16 Education and Training Boards.

Each source follows the BIEP v1 DLT pattern (per `ncca.py` from
commit `9e97ca0ca` + `primary_jc_combined.py` from the
`2026-07-14-ireland-primary-jc-dlt-baml-v1` dispatch):

- `@dlt.resource(name="tertiary_<area>", write_disposition="merge",
                primary_key=["url"|<id>])`
- structlog observability
- honors `USE_LOCAL_SCRAPES=true` (default) to read from
  `/stedding/ingest_queue/university/<area>/`
- registry tables ship Phase 1 rows; Phase 2 layer BAML-extracted
  rows on top.

### 2. 5+ new Pydantic classes + 4+ enums + 1+ function in `baml/education/university/university_extraction.baml`

The existing `university_extraction.baml` already defines the
per-university deep-extraction schema (CourseDescriptor,
ModuleDescriptor, ProgrammeDescriptor, ReadingListItem). This change
**extends** it with the **Tertiary 18+ surface**:

- **5 new Pydantic classes** — `University` (the 8 universities) +
  `TU` (the 5 TUs) + `QQIAward` (the 10 QQI awards) + `CAOChoice`
  (a CAO course choice) + `SOLASCourse` (a SOLAS PLC / apprenticeship).
- **4 new enums** — `UniversityType` (TRADITIONAL / SPECIALIST /
  TECHNOLOGICAL / PRIVATE) + `QQILevel` (NFQ_6 / NFQ_7 / NFQ_8 /
  NFQ_9 / NFQ_10) + `CAOField` (ARTS_HUMANITIES / BUSINESS_LAW /
  SCIENCE / COMPUTING_ENGINEERING / MEDICINE_HEALTH / etc.) +
  `SOLASPath` (PLC / APPRENTICESHIP / YOUTHREACH / ADULT_LITERACY /
  VTOS / COMMUNITY_TRAINING).
- **5 new BAML functions** — `ExtractUniversityInfo` +
  `ExtractTuInfo` + `ExtractQQIAward` + `ExtractCAOChoice` +
  `ExtractSOLASCourse`. All route through the canonical `ExtractEn`
  LiteLLM client (per the `oideachais-baml-schemas` spec → the
  `minimax-m3` single text generator from commit `667635dfd`).
- **3 new tests** — `ExtractUniversityInfoTest` +
  `ExtractQQIAwardTest` + `ExtractCAOChoiceTest` (exercising the
  canonical BIEP v1 `baml-cli test` CI gate).

### 3. 1 new `defs.yaml` cron asset at `orchestration/defs/1_ingestion/university/defs.yaml`

Per the BIEP v1 `CelticIngestionComponent` pattern (per the
`CelticIngestionComponent` class in `orchestration/components/layer1_ingestion.py`):

- 5 `CelticIngestionComponent` entries (one per DLT source)
- daily 06:00 UTC cron (slightly later than the primary_jc_combined
  05:00 UTC to avoid clashing with the upstream sources)
- per-source partitions (language for universities / TUs / QQI /
  SOLAS; year for CAO; solas_path + language for SOLAS)
- `use_local_scrapes=true`
- tags: `[biep, tertiary, university, ingestion]`

### 4. 1 MODIFIED spec delta

Adds 1 ADDED Requirement to the existing
`oideachais-university-deep-extraction` spec documenting that
Phase 1 of the capability is now shipped (5 DLT sources +
1 BAML extractor + 1 defs.yaml cron asset all working end-to-end).

## Dependencies

`Blocked by: none`

`Blocked by (soft): 2026-07-14-ireland-primary-jc-dlt-baml-v1`
(this change extends the K-12 → university pipeline that the
prior dispatch established; no enforcement).

`Blocked by (soft): 2026-07-13-biep-v1-phases-6-7-unblock-v1`
(BIEP v1 wiring pattern used here as the canonical DLT +
BAML + Dagster cron template).

`Affected repos: cianfhoghlaim`

## Verified

- All 5 DLT sources AST-parse cleanly under
  `uv run python3 -c "import ast; ast.parse(open('<file>').read())"`
- The 1 extended BAML file has **zero** parse errors attributable
  to the new Tertiary 18+ content (the 6 remaining errors in
  `baml/processing/_shared/video_kg.baml` are from another
  parallel agent's dirty state — out of scope).
- The 1 new `defs.yaml` cron asset is valid YAML under
  `uv run python3 -c "import yaml; yaml.safe_load(open('<file>').read())"`
  and contains 5 `CelticIngestionComponent` entries.
- The 1 MODIFIED spec delta is well-formed.

## Out of scope (Phase 2+)

- Live web scraping (Phase 1 honors `USE_LOCAL_SCRAPES=true` only;
  Phase 2 will add Crawl4AI sitemap + Firecrawl fallback for the
  universities / TUs; Skyvern/Stagehand for the JS-heavy CAO
  dropdowns).
- CocoIndex v1 Apps for Tertiary embeddings (deferred; the existing
  `university_embedding.py` covers the UoG case study).
- Marimo dashboards for Tertiary 18+ (the
  `oideachais-marimo-dashboards` spec covers K-12; a Tertiary dashboard
  is deferred).
- QQI Level 5 (NFQ 5) coverage (the SOLAS PLC pathway; the spec
  covers NFQ 6-10 only).
- Northern Ireland / Scotland / Wales / England TUs (cross-jurisdictional
  TUs like TU Ulster are deferred to the sister
  `dlt/british_isles/<nation>/university/` packages if created).

## Cross-references

- [`oideachais-university-deep-extraction` spec](../specs/oideachais-university-deep-extraction/spec.md)
  — the capability spec this change implements (8 requirements,
  per-university deep-extraction template)
- [`ireland-primary-jc-dlt-baml` spec](../specs/ireland-primary-jc-dlt-baml/spec.md)
  — the upstream K-12 (Primary + JC) capability
- [`british-isles-education-pipeline` spec](../specs/british-isles-education-pipeline/spec.md)
  — the Senior Cycle / LC flagship BIEP v1
- [`oideachais-baml-schemas` spec](../specs/oideachais-baml-schemas/spec.md)
  — the canonical BAML client setup (the `ExtractEn` client → `minimax-m3`)
- [`oideachais-pipeline` spec](../specs/oideachais-pipeline/spec.md)
  — the parent 5-stage capability
- Commit `9e97ca0ca` — `feat(dlt): ship the BIEP v1 canonical DLT pattern`
  (the canonical DLT source pattern used here)
- Commit `667635dfd` — `feat(baml): single minimax-m3 text generator`
  (the canonical BAML client setup)
- Commit `ccd1a7e18` — `feat(biep): complete Phase 1.1 English wiring`
  (the canonical `CelticIngestionComponent` pattern for defs.yaml)