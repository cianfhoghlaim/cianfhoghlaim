# Change: Docs-informed quest & credential generation (Ireland JC+LC, England GCSE+A-Level)

## Why

Ireland's LC extraction layer is real and working — the 5
`lc_extraction` BAML functions (`ExtractCurriculumSyllabus`,
`ExtractExamPaperLayout`, `ExtractMarkingSchemeGuideline`,
`ExtractCrossLinguisticConcept`, `ExtractSyllabusDiagram`) produce
structured, page-evidenced `SyllabusDocument`/`ExamPaper`/`MarkingScheme`/
`SyllabusDiagram` records from the official PDFs already ingested by the
BIEP pipeline. But the layer that's supposed to turn that extraction into
MMO content is not real: every generation function in all 8
`baml_src/british_isles/ireland/education/subjects/qpack_<subject>.baml`
files (`Generate<Subject>FormativeItem`, `Generate<Subject>QuestPack`,
etc.) still carries the literal placeholder body `"Auto-generated
extraction prompt."`, and where a real input type is declared at all
(`GenerateMathQuestPack`), it points at the old, superseded `_legacy/pdfs/
leaving_cert_syllabus.baml` types rather than the current v3 extraction
output. England has zero `QuestPack`/`FormativeItem` BAML symbols
anywhere. Junior Cycle is named in `cianfhoghlaim-educational-mmo`'s own
Background section but absent from its actual 8-subject build-out list.
The MMO client's `realm/$subject.tsx` renders hardcoded quest-item counts
with no data fetch and no `onClick` handler — its own landing-page copy
claiming quest packs are "generated from the official NCCA syllabus PDFs"
currently describes intended, not actual, behavior.

This change makes that claim true: real generation prompts wired to real
extraction output, for both Irish cycles and both English qualification
tracks, with the badge schema grounded in the NCCA's own commissioned
terminology (Junior Cycle Profile of Achievement, senior-cycle key
competencies) rather than invented pedagogy.

## What Changes

- Rewrite all 8 Ireland LC `qpack_<subject>.baml` generation functions
  with real prompts consuming the current v3 extraction types
  (`SyllabusDocument`, `ExamPaper`, `MarkingScheme`), replacing the
  legacy `_legacy/pdfs/leaving_cert_syllabus.baml` type references.
- Verify and, where needed, fix `Score<Subject>FormativeResponse` (the
  badge-issuance trigger's scoring function) for each subject in the same
  pass.
- Add Junior Cycle generation coverage — no new files needed, every
  subject's `<Subject>NCCALevel` enum already includes `JC`; the rewritten
  functions branch on level, issuing badges with `framework="ncca-jc"`
  alongside the existing `framework="ncca-lc"`.
- Add England GCSE + A-Level quest-pack generation
  (`baml_src/british_isles/england/education/subjects/qpack_<subject>.baml`,
  new) mirroring the fixed Ireland pattern against England's existing
  real extraction output. Also fix `ExtractAQAExamPaper` and
  `ExtractAQAMarkingScheme` (found still placeholder stubs while
  surveying England's extraction layer).
- Add `key_competencies` (the NCCA's 7 senior-cycle key competencies) and
  `evidence_type` fields to `SkillTreeBadge`
  (`tuatha/badges/schema.py`), grounded directly in
  `leaving_certificate/the-potential-of-technology-to-support-online-
  certification-and-reporting.pdf`.
- Wire `web/apps/cianfhoghlaim-mmo/src/routes/realm/$subject.tsx` to a
  real Convex query against a new `questPacks` table (added to
  `web/apps/cianfhoghlaim-mmo/convex/schema.ts`), replacing the hardcoded
  `QuestPackCard` counts and giving the "Start" button a working
  `onClick`.
- Write `orchestration/defs/2_materials/lc_extraction/quest_pack_assets.py`
  — 8 factory-generated Dagster assets (one per subject) that read the
  real PDF corpus, run the v3 extraction functions, call
  `Generate<Subject>QuestPack` across every NCCA level, and write to the
  Convex `questPacks` table. This closes a gap discovered while building
  this change: no Dagster asset anywhere called any quest-pack generation
  function for any subject.
- New capability spec `docs-informed-content-generation` documenting the
  extraction→generation wiring pattern as canonical, so future
  subjects/jurisdictions extend it instead of re-copying the placeholder
  pattern this change removes.

## Dependencies

`Blocked by: none`
`Blocked by (soft): none` — this change is the dependency root for the
sibling changes in this batch
(`2026-08-08-learn-to-earn-x402-credential-pipeline-v1`,
`2026-08-08-agui-generative-credential-ui-v1`,
`2026-08-08-vision-model-syllabus-diagram-generation-v1`).
`Affected repos: cianfhoghlaim (single repo)`

## Impact

- Capabilities: MODIFIED `cianfhoghlaim-educational-mmo` (Junior Cycle +
  England coverage, real generation replacing placeholder prompts); NEW
  `docs-informed-content-generation`.
- Code: `baml_src/british_isles/ireland/education/subjects/qpack_*.baml`,
  new `baml_src/british_isles/england/education/subjects/qpack_*.baml`,
  fixes to `baml_src/british_isles/england/education/{exam_paper_layout,
  marking_scheme}.baml`, `tuatha/badges/schema.py`,
  `web/apps/cianfhoghlaim-mmo/src/routes/realm/$subject.tsx`,
  `web/apps/cianfhoghlaim-mmo/convex/schema.ts`, new
  `web/apps/cianfhoghlaim-mmo/convex/questPacks.ts`, new
  `orchestration/defs/2_materials/lc_extraction/quest_pack_assets.py`.
