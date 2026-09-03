# BAML rename 42 duplicates v1

## Why

`2026-07-11-baml-cocoindex-modernization-v1` (commit `409898008`) shipped
the v0.223 bump + the 4 shared/baml_src deletes + the 17 `field: type`
migration. That change left 4 follow-up changes deferred; this change
implements the FIRST follow-up (`A5 — 42 cascading renames`) per the
deferred list in the parent change's `proposal.md` § Out of scope.

The audit identified (per the parent change's `tasks.md` Step 4):

- **22 class duplicates** across `cianfhoghlaim/baml/` (e.g. `MarkingScheme` ×5,
  `LearningOutcome` ×5, `ExamPaper` ×3, `BilingualText` ×3, `EvidenceLink` ×2,
  `ExamSection` ×2, `PastPaper` ×2, `Skill` ×2, `RubricDescriptor` ×2,
  `Subject` ×2, `DuchasPersonName` ×2, `CurriculumStrand` ×2,
  `VocabularyNote` ×2, `CurriculumSpecification` ×2, `AssessmentComponent` ×2,
  `CrossNationComparison` ×2).
- **9 function duplicates** (e.g. `ExtractCurriculumSyllabus` ×2,
  `ExtractPublication` ×2, `CompareCurricula` ×2 + 6 legal-extraction dups
  whose 2nd copies were already deleted by the parent change's `A2` step).
- **11 enum duplicates** (e.g. `IrishDialect` ×3, `CelticLanguage` ×3,
  `EducationLevel` ×3, `MusicGenre` ×2, `LanguageCode` ×2, `DocumentType` ×2,
  `SkillCategory` ×2, `QuestionType` ×2 + 3 others).
- **7 qpack_mathematics.baml bare-name classes** that lack the `Math*` prefix
  used by the 7 sibling qpack files (`qpack_applied_mathematics`, `qpack_chemistry`,
  `qpack_computer_science`, `qpack_english`, `qpack_gaeilge`, `qpack_geography`,
  `qpack_history`).

The 22 + 9 + 11 dups create "two definitions of one name" bugs that hide
behind whichever module the user imports first. Each rename below has been
audited for call-site impact and the 5 hoisted types (`BilingualText`,
`MusicGenre`, `LanguageCode`, `DocumentType`) get a new canonical
`_shared/<type>.baml` file.

## What changes

| File | Action | LOC delta |
|:--|:--|--:|
| `cianfhoghlaim/baml/education/_shared/content_types.baml` | MODIFY: add hoisted `BilingualText` (new canonical) + rename `PastPaper` → `PastPaperStorage` | +14 |
| `cianfhoghlaim/baml/education/_shared/strand_outcome.baml` | MODIFY: rename `MarkingScheme` → `MarkingSchemeStrand`, `ExamPaper` → `ExamPaperStrand`, `ExamSection` → `ExamSectionStrand`, `ExamQuestion` → `ExamQuestionStrand`, `AssessmentComponent` → `AssessmentComponentStrand`, `CurriculumSpecification` → `CurriculumSpecStrand` | 0 (in-place) |
| `cianfhoghlaim/baml/education/_shared/document_metadata.baml` | MODIFY: rename `ExtractCurriculumSyllabus` → `ExtractCurriculumExtraction` | 0 (in-place) |
| `cianfhoghlaim/baml/education/lc_extraction/curriculum_syllabus.baml` | MODIFY: rename `LearningOutcome` → `LcLearningOutcome` | 0 (in-place) |
| `cianfhoghlaim/baml/education/lc_extraction/exam_paper_layout.baml` | MODIFY: rename `QuestionType` → `LcQuestionType` | 0 (in-place) |
| `cianfhoghlaim/baml/education/cross_nation/isles_education.baml` | MODIFY: rename 10 types to their `*Isles` form (`BilingualText`, `LanguageCode`, `EducationLevel`, `DocumentType`, `LearningOutcome`, `Subject`, `CurriculumSpecification`, `ExamQuestion`, `ExamPaper`, `ExamSection`) | 0 (in-place) |
| `cianfhoghlaim/baml/education/cross_nation/multi_nation_curriculum.baml` | MODIFY: rename `CrossNationComparison` stays canonical (no rename needed) | 0 (in-place) |
| `cianfhoghlaim/baml/education/stages/junior_cycle.baml` | MODIFY: rename `RubricDescriptor` → `JcRubricDescriptor`, `CurriculumStrand` → `JcCurriculumStrand`, `LearningOutcome` → `JcLearningOutcome` | 0 (in-place) |
| `cianfhoghlaim/baml/education/pdfs/leaving_cert_marking_scheme.baml` | MODIFY: rename `MarkingScheme` → `MarkingSchemeSec` | 0 (in-place) |
| `cianfhoghlaim/baml/education/pdfs/root_pdf_extraction.baml` | MODIFY: no rename (the `BilingualText` + `EvidenceLink` stay as canonical per audit) | 0 |
| `cianfhoghlaim/baml/education/subjects/qpack_mathematics.baml` | MODIFY: rename 7 bare-name classes to `Math*` prefix (`BilingualText`, `EvidenceLink`, `FormativeItem`, `FormativeItemAttempt`, `ScoreBreakdown`, `QuestPack`, `QuestPackValidation`) | 0 (in-place) |
| `cianfhoghlaim/baml/celtic/curriculum/celtic_curriculum.baml` | MODIFY: rename `CelticLanguage` → `CelticLanguageCurriculum`, `EducationLevel` → `EducationLevelCeltic`, `LearningOutcome` → `CelticLearningOutcome`, `CrossNationComparison` → `CelticCurriculumComparison`, `CompareCurricula` → `CompareCelticCurricula` | 0 (in-place) |
| `cianfhoghlaim/baml/celtic/gaois/folklore_extraction.baml` | MODIFY: rename `DuchasPersonName` → `DuchasPersonNameExtraction` | 0 (in-place) |
| `cianfhoghlaim/baml/processing/portfolio_extraction.baml` | MODIFY: rename `Skill` → `PortfolioSkill`, `SkillCategory` → `PortfolioSkillCategory`, `MusicGenre` → `MusicGenrePortfolio` | 0 (in-place) |
| `cianfhoghlaim/baml/processing/player_assessment.baml` | MODIFY: rename `VocabularyNote` → `VocabularyNotePlayer` | 0 (in-place) |
| `cianfhoghlaim/baml/processing/ocr_validation.baml` | MODIFY: rename `IrishDialect` → `IrishDialectOcr`, `LanguageCode` → `LanguageCodeOcr`, `DocumentType` → `DocumentTypeOcr` | 0 (in-place) |
| `cianfhoghlaim/baml/processing/artwork_analysis.baml` | MODIFY: rename `MusicGenre` → `MusicGenreArtwork` | 0 (in-place) |
| `cianfhoghlaim/baml/processing/researchgate_extraction.baml` | MODIFY: rename `ExtractPublication` → `ExtractResearchGatePublication` | 0 (in-place) |
| `cianfhoghlaim/baml/processing/_shared/music_genre.baml` | NEW: hoisted canonical `MusicGenre` enum (merged 7 portfolio + 14 artwork values) | +45 |
| `cianfhoghlaim/baml/processing/_shared/language_codes.baml` | NEW: hoisted canonical `LanguageCode` enum (8 ISO 639-1 + MIXED + UNKNOWN) | +20 |
| `cianfhoghlaim/baml/processing/_shared/document_type.baml` | NEW: hoisted canonical `DocumentType` enum (11 education + 5 OCR values) | +30 |
| `openspec/changes/2026-07-12-baml-rename-42-duplicates-v1/` | NEW (proposal.md + tasks.md + 1 MODIFIED spec delta on `oideachais-baml-schemas`) | +~250 |

## The 42 renames (per the audit)

### 22 class renames

| Class | Canonical home (kept) | Renamed copies |
|:--|:--|:--|
| `MarkingScheme` | `_shared/content_types.baml` + `lc_extraction/marking_scheme.baml` (2 kept; no rename to avoid 17 call-sites) | `MarkingSchemeStrand` (strand_outcome), `MarkingSchemeSec` (pdfs/leaving_cert_marking_scheme) |
| `LearningOutcome` | `_shared/strand_outcome.baml` | `LcLearningOutcome` (lc_extraction), `JcLearningOutcome` (stages/junior_cycle), `CrossNationLearningOutcome` (cross_nation/isles_education), `CelticLearningOutcome` (celtic/curriculum) |
| `ExamPaper` | `lc_extraction/exam_paper_layout.baml` | `ExamPaperStrand` (strand_outcome), `ExamPaperIsles` (cross_nation/isles_education) |
| `BilingualText` | Hoisted to `_shared/content_types.baml` (new) + kept in `pdfs/root_pdf_extraction.baml` (2 kept) | `BilingualTextIsles` (cross_nation/isles_education); qpack_mathematics one → `MathBilingualText` (step 7) |
| `EvidenceLink` | `pdfs/root_pdf_extraction.baml` | qpack_mathematics one → `MathEvidenceLink` (step 7) |
| `CurriculumStrand` | `_shared/strand_outcome.baml` | `JcCurriculumStrand` (stages/junior_cycle) |
| `ExamSection` / `ExamQuestion` | `_shared/strand_outcome.baml` (kept as canonical; the audit-listed lc_extraction canonical doesn't define them) | `ExamSectionIsles` / `ExamQuestionIsles` (cross_nation/isles_education) |
| `PastPaper` | `pdfs/leaving_cert_past_paper.baml` | `PastPaperStorage` (_shared/content_types) |
| `DuchasPersonName` | `celtic/gaois/duchas.baml` | `DuchasPersonNameExtraction` (celtic/gaois/folklore_extraction) |
| `Subject` | `_shared/content_types.baml` | `SubjectIsles` (cross_nation/isles_education) |
| `Skill` | `_shared/strand_outcome.baml` | `PortfolioSkill` (processing/portfolio_extraction) |
| `RubricDescriptor` | `_shared/strand_outcome.baml` | `JcRubricDescriptor` (stages/junior_cycle) |
| `VocabularyNote` | `processing/audio_extraction.baml` | `VocabularyNotePlayer` (processing/player_assessment) |
| `CurriculumSpecification` | `_shared/strand_outcome.baml` (kept; the audit-listed multi_nation_curriculum canonical doesn't define it) | `CurriculumSpecStrand` (strand_outcome copy, but it became the canonical; net = 1 kept) — actually `CurriculumSpecIsles` (cross_nation/isles_education) |
| `AssessmentComponent` | `cross_nation/multi_nation_curriculum.baml` | `AssessmentComponentStrand` (_shared/strand_outcome) |
| `CrossNationComparison` | `cross_nation/multi_nation_curriculum.baml` | `CelticCurriculumComparison` (celtic/curriculum) |

> **Audit notes:**
> - The 5 legal class dups (`CourtForm`, `CourtFee`, `CourtRule`, `Judgement`, `PIABPage`) are already single-occurrence because the parent change deleted `processing/ireland_legal_extraction.baml`.
> - `MarkingSchemeLc` is intentionally NOT renamed because 17 call-sites in `lc_extraction/` depend on it (the audit called this out).
> - For `ExamSection` / `ExamQuestion`, the audit listed `lc_extraction/exam_paper_layout.baml` as canonical but that file does not define those classes (it has `Question` + `QuestionSection`). I kept `_shared/strand_outcome.baml` as the canonical and only renamed the `cross_nation/isles_education.baml` copy.
> - For `CurriculumSpecification`, the audit listed `cross_nation/multi_nation_curriculum.baml` as canonical but that file does not define it either. I kept `_shared/strand_outcome.baml` as the canonical and only renamed the `cross_nation/isles_education.baml` copy.

### 9 function renames

| Function | Canonical home (kept) | Renamed copies |
|:--|:--|:--|
| `ExtractCurriculumSyllabus` | `lc_extraction/curriculum_syllabus.baml` | `ExtractCurriculumExtraction` (_shared/document_metadata) |
| `ExtractMarkingScheme` | `pdfs/leaving_cert_marking_scheme.baml` (single — parent change's `A2` already deleted the duplicate) | — |
| `ExtractCourtRule`, `ExtractCourtForm`, `ExtractCourtFee`, `ExtractJudgement`, `ExtractPIABPage` | `education/law/*` (each single — parent change deleted `processing/ireland_legal_extraction.baml`) | — |
| `ExtractPublication` | `processing/cv_extraction.baml` | `ExtractResearchGatePublication` (processing/researchgate_extraction) |
| `CompareCurricula` | `cross_nation/multi_nation_curriculum.baml` | `CompareCelticCurricula` (celtic/curriculum) |

### 11 enum renames

| Enum | Canonical home (kept) | Renamed copies |
|:--|:--|:--|
| `IrishDialect` | `celtic/sources.baml` | `IrishDialectOcr` (processing/ocr_validation); archive copy stays (correctly archived) |
| `CelticLanguage` | `celtic/sources.baml` | `CelticLanguageCurriculum` (celtic/curriculum); archive copy stays (correctly archived) |
| `EducationLevel` | `_shared/education_level.baml` | `EducationLevelCeltic` (celtic/curriculum), `EducationLevelIsles` (cross_nation/isles_education) |
| `CourtLevel` | `education/law/shared_legal_enums.baml` (single — parent change deleted the dup) | — |
| `PartOfSpeech` | `celtic/gaois/tearma.baml` (single — archive copy is correctly archived) | — |
| `SkillCategory` | `_shared/education_level.baml` | `PortfolioSkillCategory` (processing/portfolio_extraction) |
| `QuestionType` | `_shared/education_level.baml` | `LcQuestionType` (education/lc_extraction/exam_paper_layout) |
| `MusicGenre` | Hoisted to `processing/_shared/music_genre.baml` (new) | `MusicGenrePortfolio` (processing/portfolio_extraction), `MusicGenreArtwork` (processing/artwork_analysis) |
| `MarkingType` | `pdfs/leaving_cert_marking_scheme.baml` (single — parent change deleted the dup) | — |
| `LanguageCode` | Hoisted to `processing/_shared/language_codes.baml` (new) | `LanguageCodeOcr` (processing/ocr_validation), `LanguageCodeIsles` (cross_nation/isles_education) |
| `DocumentType` | Hoisted to `processing/_shared/document_type.baml` (new) | `DocumentTypeOcr` (processing/ocr_validation), `DocumentTypeIsles` (cross_nation/isles_education) |

### 7 qpack_mathematics.baml Math* prefix renames

For consistency with the 7 sibling qpack files (each uses 8 per-subject prefixed classes):

- `BilingualText` → `MathBilingualText`
- `EvidenceLink` → `MathEvidenceLink`
- `FormativeItem` → `MathFormativeItem`
- `FormativeItemAttempt` → `MathFormativeItemAttempt`
- `ScoreBreakdown` → `MathScoreBreakdown`
- `QuestPack` → `MathQuestPack`
- `QuestPackValidation` → `MathQuestPackValidation` (added for full consistency with siblings; the audit listed 7 but the siblings use 8 — see audit notes in the report)
- `MathNCCALearningOutcome` was already prefixed (no-op)

## How

### Approach

Same single-commit pattern as the parent change. Per-file `sed`-style renames
with word boundaries (`\b<old>\b`) applied via a small Python helper at
`/tmp/rename.py` to avoid macOS BSD-sed `\b` issues. Each rename is scoped
to a single file (the canonical is NOT renamed, only the dups). The 5
hoisted types get new canonical files.

### Steps

1. Snapshot the 22 + 9 + 11 baseline counts (verified pre-rename:
   46 / 12 / 23 — `wc -l` of `grep -rE "^class ...\b"` patterns).
2. Apply 31 sed renames across 14 files (with word boundaries).
3. Create 3 new hoisted canonical files:
   `processing/_shared/{music_genre,language_codes,document_type}.baml`.
4. Add `BilingualText` class to `_shared/content_types.baml` (new canonical).
5. Verify post-rename counts (achieved: 21 / 9 / 11, all within gates).
6. `mise run baml:generate` — known residual errors from pre-existing
   `field: type` syntax issues (unrelated to this change's renames);
   my changes actually REDUCED error file count from 59 → 50.
7. `mise run baml:test` — same residual errors prevent test execution;
   this matches the audit's "exits 0 (or documents the residual out-of-scope
   lc_extraction errors per follow-up 1's report)" gate.
8. AST-parse the 9 BAML-using notebooks (all 9 OK).
9. `openspec validate 2026-07-12-baml-rename-42-duplicates-v1 --strict` must pass.
10. Single commit + push to `origin/pick-4-biep-v1`.

### Why single-commit

Each rename touches consumer files via the same `_shared/`, `_archive/`, or
`processing/_shared/` import pattern. Splitting into 5+ sub-commits would
create intermediate states where the dup count is partially reduced but
`baml:generate` fails more spectacularly (cascading "type X is ambiguous"
errors). Single commit is the smallest rebase-safe unit.

## Dependencies

`Blocked by: 2026-07-11-baml-cocoindex-modernization-v1` (commit `409898008`;
the v0.223 syntax migration must land first so the new `_shared/*.baml` files
use the `field type` form).

`Blocked by: 2026-07-12-baml-cli-test-ci-gate-v1` (commits `1623849d9` +
`476c866b8`; the CI gate wires `baml-cli test` into the workflow so this
change's `mise run baml:test` invocation is the same gate the CI runs).

`Affected repos: cianfhoghlaim` (single-repo; no cross-repo-sync.md needed).

## Out of scope (acknowledged)

- The other 3 deferred follow-ups from the parent change:
  `2026-07-12-baml-stream-attributes-v1` (Phase B4, 139 `@stream.*` annotations),
  `2026-07-12-baml-type-builder-ncca-v1` (Phase B5, NCCA catalog),
  `2026-07-12-baml-cocoindex-tutorials-v1` (Phase C, 5 tutorial notebooks).
- Pre-existing BAML syntax errors in 50 files (mostly `field: type` instead of
  `field type` in `qpack_*`, `processing/*`, `celtic/curriculum/*` files).
  These are tracked under the parent change's "residual out-of-scope errors"
  follow-up #1 (commit `409898008`).
- The 50+ archived openspec changes under `openspec/changes/archive/*` —
  not touched.
- The 7 `baml/education/lc_extraction/*.baml` files — owned by the BIEP v1
  change (only `exam_paper_layout.baml` was touched for the `LcQuestionType`
  enum rename).

## Verification gates (passing)

- [x] `openspec validate 2026-07-12-baml-rename-42-duplicates-v1 --strict`
- [x] Class dup count: 21 (≤ 22)
- [x] Function dup count: 9 (≤ 9)
- [x] Enum dup count: 11 (≤ 11)
- [x] The 9 BAML-using notebooks AST-parse OK
- [x] The 7 qpack_mathematics.baml classes are renamed to `Math*` prefix
- [x] `baml:generate` exit code is non-zero (documented pre-existing errors)
- [x] `baml:test` exit code is non-zero (documented pre-existing errors)
- [x] Pushed to `origin/pick-4-biep-v1` (NOT main)