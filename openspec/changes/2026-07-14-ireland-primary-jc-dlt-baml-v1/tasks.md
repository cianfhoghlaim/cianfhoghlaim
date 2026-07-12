# Tasks — Ireland Primary + Junior Cycle DLT + BAML v1

## 1. Read the spec + audit the existing infrastructure (30 min)

- [x] Read `openspec/specs/ireland-primary-jc-dlt-baml/spec.md` (3 requirements:
      Primary stage DLT sources / Junior Cycle DLT sources (24 subjects) /
      Stage-specific BAML schemas).
- [x] Audited the existing `dlt/british_isles/ireland/education/`
      tree: `primary.py` + `junior_cycle.py` already exist (committed at
      `24f671f43`); `ncca.py` + `examinations.py` + `gov_ie_circulars.py` are
      the BIEP v1 sources (do not touch).
- [x] Audited the existing `baml/education/stages/` tree:
      `primary.baml` + `junior_cycle.baml` already exist (committed at
      `54c21dd52`); they use the legacy class names. The new stage-specific
      schemas will use the `Stage` suffix to avoid class-name collisions.
- [x] Confirmed no `defs.yaml` cron assets exist for primary/jc under
      `orchestration/defs/1_ingestion/curriculum/`.

## 2. Ship the 3 DLT sources + the BAML extractors (2-3 hours)

- [x] `primary.py` — already shipped (12 NCCA Primary areas × EN + GA;
      honours `USE_LOCAL_SCRAPES=true`; dlt pattern follows the BIEP v1
      canonical form).
- [x] `junior_cycle.py` — already shipped (18 NCCA JC subjects + 16 short
      courses + CBAs; honours `USE_LOCAL_SCRAPES=true`).
- [x] `primary_jc_combined.py` (NEW) — 3 dlt resources
      (`primary_jc_unified` + `primary_jc_subjects` + `primary_jc_strands`)
      walking the combined `/stedding/ingest_queue/{primary,junior_cycle}/`
      cache. Honours `USE_LOCAL_SCRAPES=true`.
- [x] `baml/education/primary/primary_extraction.baml` (NEW) — 3 enums
      (`PrimaryYearLevel` × 8 + `PrimaryArea` × 4 + `PrimaryMathsStrand` × 5)
      + 3 Pydantic classes + 1 `ExtractPrimaryArea` function (uses
      canonical `ExtractEn` client → `minimax-m3`).
- [x] `baml/education/junior_cycle/junior_cycle_extraction.baml` (NEW) —
      4 enums (`JCYearLevel` × 3 + `JCSubject` × 24 + `JCScienceStrand` × 4
      + `JCLevel` × 3) + 3 Pydantic classes + 1 `ExtractJCSubjectSpec`
      function.

## 3. Create the 3 DLT defs YAMLs (30 min)

- [x] `orchestration/defs/1_ingestion/curriculum/primary/defs.yaml` —
      daily 04:00 UTC cron, 4 areas × EN+GA (8 partitions).
- [x] `orchestration/defs/1_ingestion/curriculum/junior_cycle/defs.yaml` —
      Monday-only 04:00 UTC cron, 24 subjects × EN+GA (48 partitions).
- [x] `orchestration/defs/1_ingestion/curriculum/primary_jc_combined/defs.yaml` —
      daily 05:00 UTC cron, 2 stages × EN+GA (4 partitions).

## 4. Wire the BAML extractors into the lakehouse (30 min)

- [x] `ExtractPrimaryArea` + `ExtractJCSubjectSpec` use the canonical
      `ExtractEn` client (which routes to `minimax-m3` per commit
      `667635dfd` — the single text generator).
- [x] The 2 new BAML files are syntactically clean: 0 errors under
      `mise run baml:generate`. (The 6 remaining errors in
      `video_kg.baml` are another agent's dirty state — out of scope.)

## 5. Verify (30 min)

- [x] All 3 DLT sources AST-parse OK (`primary.py` +
      `junior_cycle.py` + `primary_jc_combined.py`).
- [x] All 2 new BAML files have zero parse errors under
      `mise run baml:generate`.
- [x] All 3 new `defs.yaml` cron assets are valid YAML.

## 6. Write the openspec change (30 min)

- [x] `openspec/changes/2026-07-14-ireland-primary-jc-dlt-baml-v1/proposal.md`
      — explains the 3 DLT sources + the BAML extractors + the 3 defs.yaml.
- [x] `openspec/changes/2026-07-14-ireland-primary-jc-dlt-baml-v1/tasks.md`
      — this file.
- [x] `openspec/changes/2026-07-14-ireland-primary-jc-dlt-baml-v1/specs/
      ireland-primary-jc-dlt-baml/spec.md` — MODIFIED delta with 1 ADDED
      Requirement.

## 7. Commit + push (5 min)

- [x] Commit on `pick-4-biep-v1` branch.
- [x] Push to `origin/pick-4-biep-v1` (NOT `main`).