# Tasks — Ireland Tertiary 18+ University Deep Extraction v1

## 1. Read the spec + audit the existing infrastructure (30 min)

- [x] Read `openspec/specs/oideachais-university-deep-extraction/spec.md`
      (8 requirements: per-university config schema / two URL surfaces
      per university / BAML course+module+programme+reading-list
      extraction / 3-stage pre-research→bulk-scrape→condense pipeline /
      5 Dagster assets / CocoIndex v1 App for course+module embeddings /
      Cognee cross-archive edge / marimo notebook with 4 tabs).
- [x] Audited the existing `dlt/british_isles/ireland/`
      tree: `education/university_of_galway_deep.py` +
      `_university_deep_factory.py` are the per-university deep
      extraction (UoG case study); `education/tertiary.py` already
      covers CAO + matriculation + QQI + Apprenticeships at the
      cross-stage level. The 5 NEW sources at
      `dlt/british_isles/ireland/university/` cover the broader
      Tertiary 18+ registry-of-record view.
- [x] Audited the existing `baml/education/university/`
      tree: `university_extraction.baml` already defines the
      per-university deep-extraction schema (CourseDescriptor /
      ModuleDescriptor / ProgrammeDescriptor / ReadingListItem + 4
      functions). This change **extends** it with the Tertiary 18+
      surface (University / TU / QQIAward / CAOChoice / SOLASCourse
      + 4 enums + 5 functions).
- [x] Audited the existing `orchestration/defs/
      1_ingestion/` tree: no `university/` subdir exists yet;
      existing `curriculum/{primary, junior_cycle, primary_jc_combined,
      lc5, lc6_ncca, lc6_examinations, ie_ncca_curriculum, ie_sec_examinations}/`
      cover the K-12 + LC stages.

## 2. Ship the 5 DLT sources for the Tertiary 18+ stage (2-3 hours)

- [x] `dlt/british_isles/ireland/university/universities.py`
      — covers the **8 Republic of Ireland universities** (TCD, UCD,
      UCC, UoG, UL, DCU, Maynooth, RCSI) per the Universities Act 1997.
      2 dlt resources (`tertiary_universities` +
      `tertiary_university_faculties`). Honors `USE_LOCAL_SCRAPES=true`.
- [x] `dlt/british_isles/ireland/university/tus.py` —
      covers the **5 Technological Universities** (TUD, MTU, TUS, ATU,
      SETU) per the Technological Universities Act 2018. 2 dlt
      resources (`tertiary_tus` + `tertiary_tu_campuses`).
- [x] `dlt/british_isles/ireland/university/qqi_awards.py`
      — covers the **10 canonical QQI awards** at NFQ 6-10 (Higher
      Certificate, Ord BA, Hons BA, Higher Diploma, Graduate Diploma,
      PG Cert, PG Dip, Masters, Ph.D., Professional Doctorate). 2 dlt
      resources (`tertiary_qqi_awards` + `tertiary_qqi_providers`).
- [x] `dlt/british_isles/ireland/university/cao.py` —
      covers the **CAO Central Applications Office**. 2 dlt resources
      (`tertiary_cao_courses` + `tertiary_cao_application_rounds`).
      The 4 annual application rounds (R1, R2, R3, R4) are emitted as
      3-year time-series rows (current year ± 2).
- [x] `dlt/british_isles/ireland/university/solas.py` —
      covers the **SOLAS Further Education + Training Authority** +
      the **16 Education and Training Boards (ETBs)**. 2 dlt resources
      (`tertiary_solas_courses` + `tertiary_solas_apprenticeships`).
- [x] `dlt/british_isles/ireland/university/__init__.py`
      — re-exports all 5 sources for easy import from downstream.

## 3. Extend the BAML extractor with the Tertiary 18+ surface (1 hour)

- [x] Extended `baml/education/university/university_extraction.baml`
      with **5 new Pydantic classes** (`University` + `TU` +
      `QQIAward` + `CAOChoice` + `SOLASCourse`).
- [x] Added **4 new enums** (`UniversityType` + `QQILevel` +
      `CAOField` + `SOLASPath`).
- [x] Added **5 new BAML functions** (`ExtractUniversityInfo` +
      `ExtractTuInfo` + `ExtractQQIAward` + `ExtractCAOChoice` +
      `ExtractSOLASCourse`); all route through the canonical `ExtractEn`
      LiteLLM client (per the `oideachais-baml-schemas` spec → the
      `minimax-m3` single text generator from commit `667635dfd`).
- [x] Added **3 new tests** (`ExtractUniversityInfoTest` +
      `ExtractQQIAwardTest` + `ExtractCAOChoiceTest`).
- [x] Verified: the new content has zero parse errors under
      `mise run baml:generate` (the 6 remaining errors in
      `baml/processing/_shared/video_kg.baml` are another agent's
      dirty state — out of scope, do not touch).

## 4. Create the 1 defs.yaml cron asset (30 min)

- [x] `orchestration/defs/1_ingestion/university/defs.yaml`
      — 5 `CelticIngestionComponent` entries (one per DLT source);
      daily 06:00 UTC cron (later than primary_jc_combined's 05:00 to
      avoid clashing); per-source partitions (language for universities
      / TUs / QQI / SOLAS; year for CAO; solas_path + language for
      SOLAS); `use_local_scrapes=true`; tags `[biep, tertiary,
      university, ingestion]`.

## 5. Verify (30 min)

- [x] All 5 DLT sources AST-parse OK
      (`universities.py` + `tus.py` + `qqi_awards.py` + `cao.py` +
      `solas.py`).
- [x] The extended BAML file has zero parse errors attributable to
      the new Tertiary 18+ content under `mise run baml:generate`
      (errors are exclusively from the parallel agent's
      `baml/processing/_shared/video_kg.baml` — out of scope).
- [x] The 1 new `defs.yaml` cron asset is valid YAML and contains
      5 `CelticIngestionComponent` entries.

## 6. Write the openspec change (15 min)

- [x] `openspec/changes/2026-07-15-oideachais-university-deep-extraction-v1/proposal.md`
      — explains the 8 requirements + the 5 DLT sources + the
      BAML extension + the 1 defs.yaml.
- [x] `openspec/changes/2026-07-15-oideachais-university-deep-extraction-v1/tasks.md`
      — this file.
- [x] `openspec/changes/2026-07-15-oideachais-university-deep-extraction-v1/specs/
      oideachais-university-deep-extraction/spec.md` — MODIFIED delta
      with 1 ADDED Requirement "Phase 1 complete".

## 7. Commit + push (5 min)

- [ ] Commit on `pick-4-biep-v1` branch.
- [ ] Push to `origin/pick-4-biep-v1` (NOT `main`).