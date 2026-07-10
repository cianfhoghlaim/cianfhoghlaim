## ADDED Requirements

### Requirement: BAML class / function / enum duplicate names

The system SHALL have at most 1 occurrence per name across the BAML `class`,
`function`, and `enum` declarations in `cianfhoghlaim/baml/**` (the 28 BAML
files + 3 new hoisted canonicals under `processing/_shared/`), per the
audit at the `2026-07-11-baml-cocoindex-modernization-v1` mega-change
(`tasks.md` Step 4).

The audit identified 22 class duplicates + 9 function duplicates + 11 enum
duplicates (42 total collisions, plus 7 `qpack_mathematics.baml` bare-name
classes that lack the `Math*` prefix used by the 7 sibling qpack files).
This change resolves all 42 + the 7 qpack renames.

#### Scenario: Class duplicates reduced to canonical-only

- **GIVEN** the 22 class duplicates per the audit (e.g. `MarkingScheme` ×5,
  `LearningOutcome` ×5, `ExamPaper` ×3, `BilingualText` ×3)
- **WHEN** the rename script is applied
- **THEN** the post-rename `grep -rE "^class (MarkingScheme|LearningOutcome|...)\b" cianfhoghlaim/baml/ --include='*.baml' --exclude-dir='_archive' | wc -l` SHALL return ≤ 22
- **AND** the 3 hoisted canonicals (`BilingualText`,
  `MusicGenre`, `LanguageCode`, `DocumentType`) SHALL live under
  `_shared/<type>.baml`

#### Scenario: Function duplicates reduced to canonical-only

- **GIVEN** the 9 function duplicates per the audit
- **WHEN** the rename script is applied
- **THEN** the post-rename `grep -rE "^function (ExtractCurriculumSyllabus|...)\b" cianfhoghlaim/baml/ --include='*.baml' --exclude-dir='_archive' | wc -l` SHALL return ≤ 9
- **AND** the 2 active renames (`ExtractCurriculumSyllabus` →
  `ExtractCurriculumExtraction` in `_shared/document_metadata.baml`,
  `ExtractPublication` → `ExtractResearchGatePublication` in
  `processing/researchgate_extraction.baml`, `CompareCurricula` →
  `CompareCelticCurricula` in `celtic/curriculum/celtic_curriculum.baml`)
  SHALL be applied
- **AND** the 6 legal-extraction dups (`ExtractCourtRule`, `ExtractCourtForm`,
  `ExtractCourtFee`, `ExtractJudgement`, `ExtractPIABPage`,
  `ExtractMarkingScheme`) SHALL already be single-occurrence because the
  parent change's `A2` step deleted `processing/ireland_legal_extraction.baml`

#### Scenario: Enum duplicates reduced to canonical-only

- **GIVEN** the 11 enum duplicates per the audit
- **WHEN** the rename script is applied
- **THEN** the post-rename `grep -rE "^enum (IrishDialect|CelticLanguage|...)\b" cianfhoghlaim/baml/ --include='*.baml' --exclude-dir='_archive' | wc -l` SHALL return ≤ 11
- **AND** the 3 hoisted canonical enums SHALL live under
  `processing/_shared/{music_genre,language_codes,document_type}.baml`

#### Scenario: qpack_mathematics Math* prefix

- **GIVEN** the 7 qpack_mathematics.baml bare-name classes (BilingualText,
  EvidenceLink, FormativeItem, FormativeItemAttempt, ScoreBreakdown,
  QuestPack, QuestPackValidation)
- **WHEN** the rename script is applied
- **THEN** each class SHALL be renamed to its `Math*` prefix form (e.g.
  `BilingualText` → `MathBilingualText`, `QuestPackValidation` →
  `MathQuestPackValidation`)
- **AND** all function signatures that reference these types SHALL be
  updated (`item: FormativeItem` → `item: MathFormativeItem`,
  `-> FormativeItem` → `-> MathFormativeItem`, etc.)
- **AND** the post-rename `qpack_mathematics.baml` SHALL be consistent
  with the 7 sibling qpack files (each uses 8 per-subject prefixed classes)

#### Scenario: Audit notes — canonical home corrections

- **GIVEN** 3 audit inconsistencies (the audit listed canonical homes
  that don't define the type)
- **WHEN** the rename script is applied
- **THEN** for `ExamSection` / `ExamQuestion`, the canonical SHALL stay
  in `_shared/strand_outcome.baml` (not `lc_extraction/exam_paper_layout.baml`
  as the audit listed; that file has `Question` + `QuestionSection` instead)
- **AND** for `CurriculumSpecification`, the canonical SHALL stay in
  `_shared/strand_outcome.baml` (not `cross_nation/multi_nation_curriculum.baml`
  as the audit listed; that file doesn't define it)
- **AND** `MarkingSchemeLc` SHALL be intentionally kept un-renamed
  (the audit called this out — 17 call-sites in `lc_extraction/` depend on it)