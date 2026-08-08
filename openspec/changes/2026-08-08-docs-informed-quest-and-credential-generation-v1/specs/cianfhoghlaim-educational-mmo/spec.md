## MODIFIED Requirements

### Requirement: 8 NCCA Leaving Certificate Subjects

The system SHALL provide end-to-end per-subject pipelines for the 8
NCCA Leaving Certificate subjects: mathematics, applied_mathematics,
chemistry, geography, history, english, gaeilge, computer_science.
Each subject SHALL have a `qpack_<subject>.baml` file,
`dlt/subjects/<subject>/` source, `dagster/assets/<subject>_assets.py`,
`cocoindex/<subject>_embedding.py`, `agents/tuatha/<subject>_agent.py`,
`web/apps/cianfhoghlaim-mmo/src/routes/realm/<subject>.tsx`, and
`notebooks/leaving_cert/<subject>.py`. Every generation function in each
subject's `qpack_<subject>.baml` (`Generate<Subject>FormativeItem`,
`Generate<Subject>QuestPack`) SHALL take the current v3 extraction types
(`SyllabusDocument`, `ExamPaper`, `MarkingScheme` — as produced by the
`lc_extraction` BAML functions) as input and SHALL NOT reference the
superseded `_legacy/pdfs/leaving_cert_syllabus.baml` types. No generation
function SHALL contain a placeholder prompt body.

#### Scenario: Mathematics pipeline runs end-to-end

- **GIVEN** the 7 Mathematics PDFs in
  `cianfhoghlaim/leaving_certificate/mathematics/{en,ga}/`
- **WHEN** the user materialises the 6 Mathematics Dagster assets
- **THEN** the `math_syllabus_raw` asset produces ≥1 `MathSyllabusTopic` per topic
- **AND** the `math_quest_pack` asset produces ≥1 `FormativeItem` per learning outcome
- **AND** the `math_embedding` asset populates the LanceDB table
  `cianfhoghlaim.lc.mathematics.embeddings` with ≥1 BGE-M3 1024-dim
  vector per quest item
- **AND** the marimo notebook at
  `cianfhoghlaim/notebooks/leaving_cert/mathematics.py` renders
  the 8-subject NCCA syllabus landscape with bilingual EN + GA content

#### Scenario: Generated formative item cites real extraction, not a placeholder

- **GIVEN** a Mathematics `SyllabusDocument` record extracted by
  `ExtractCurriculumSyllabus` from a real ingested LC PDF, with
  `source_page` evidence
- **WHEN** `GenerateMathFormativeItem` is called with that
  `SyllabusDocument` as input
- **THEN** the returned `MathFormativeItem`'s content is traceable to
  the input `SyllabusDocument`'s `source_page`
- **AND** the BAML function body is not the literal string
  `"Auto-generated extraction prompt."`

#### Scenario: All 8 subjects have full pipelines

- **GIVEN** the per-subject PDF corpora are present
  (`cianfhoghlaim/leaving_certificate/<subject>/{en,ga}/`)
- **WHEN** the user runs `mise run dagster:oideachais`
- **THEN** all 8 subject asset groups are visible in the Dagster UI
- **AND** all 8 marimo notebooks render without error

### Requirement: Per-subject quest pack generation

The system SHALL generate formative quest packs keyed to NCCA learning
outcomes + past paper questions + marking schemes, for both the Leaving
Certificate and Junior Cycle programmes. Each quest pack SHALL be
bilingual EN + GA, and SHALL support the 3 NCCA levels (Higher /
Ordinary / Foundation where applicable) for Leaving Cert subjects. The
quest pack SHALL contain ≥1 `FormativeItem` per NCCA learning outcome,
with difficulty range 1-5, and SHALL reference the source NCCA PDF page
in its `evidence.source_page` field. Quest-pack generation functions
SHALL consume real extraction output (`SyllabusDocument`, `ExamPaper`,
`MarkingScheme`) — content SHALL NOT be generated from a learning-outcome
code string alone.

#### Scenario: Quest pack generated for a Mathematics LO

- **GIVEN** a Mathematics learning outcome `LC-MATHS-LO-2.4`
- **WHEN** the BAML function `GenerateMathFormativeItem(syllabus:
  SyllabusDocument, lo_code="LC-MATHS-LO-2.4", difficulty=3)` runs
- **THEN** the output is a `MathFormativeItem` with `text_en`, `text_ga`,
  `marking_scheme_en`, `marking_scheme_ga`, `evidence.source_page` ≥1,
  and `difficulty == 3`
- **AND** the output content reflects the actual syllabus text passed
  in, not a generic template

#### Scenario: Gaeilge quest pack is Irish-only

- **GIVEN** a Gaeilge learning outcome `LC-GAEL-LO-3.1`
- **WHEN** the BAML function `GenerateGaelFormativeItem("LC-GAEL-LO-3.1", difficulty=2)` runs
- **THEN** the output's `text_en` is null (Gaeilge is taught in Irish only)
- **AND** the output's `text_ga` is the canonical Irish phrasing
- **AND** the output's `marking_scheme_en` is null
- **AND** the output's `marking_scheme_ga` is the canonical Irish marking scheme

#### Scenario: Junior Cycle quest pack issues a JCPA-framework badge

- **GIVEN** a Junior Cycle learning outcome for a subject with Junior
  Cycle coverage
- **WHEN** a student completes the generated formative item at ≥80%
- **THEN** a `SkillTreeBadge` is issued with `framework="ncca-jc"`
- **AND** the badge's `competency_code` matches the Junior Cycle LO code

### Requirement: 2D TanStack Start game client

The system SHALL provide a TanStack Start 2D game client at
`cianfhoghlaim/web/apps/cianfhoghlaim-mmo/` on port 3080 with routes
for the 8 subject realms, the student badge wallet, the cross-subject
mastery dashboard, the teacher view, and the public Merkle anchor
verification page. The client SHALL use BetterAuth (email/password +
SIWE wallet) for authentication, Convex for real-time state, and
CopilotKit AG-UI for streaming agent chat. The client SHALL be
bilingual EN + GA throughout. Subject realm pages SHALL render quest
content fetched from a real Convex query against generated content —
no hardcoded item counts or non-functional buttons. **No Babylon.js, no
SpacetimeDB.**

#### Scenario: Subject realm page renders real quest content

- **GIVEN** the user navigates to `/realm/mathematics`
- **WHEN** the page loads
- **THEN** the page displays the Mathematics realm header (bilingual)
- **AND** the page lists ≥1 quest pack fetched via a Convex query
  against the `questPacks` table, not a hardcoded count
- **AND** the "Start" button has a working `onClick` handler that
  begins a quest attempt

#### Scenario: Student badge wallet renders

- **GIVEN** a student has ≥1 `SkillTreeBadge` in Convex
- **WHEN** the user navigates to `/student/<id>/badges`
- **THEN** the page displays ≥1 badge card with the badge id, framework,
  level, subject, competency code, date earned, and on-chain anchor
- **AND** the page links to the public verification page for each badge

#### Scenario: Cross-subject mastery dashboard renders

- **GIVEN** a student has badges in ≥2 subjects
- **WHEN** the user navigates to `/student/<id>/mastery`
- **THEN** the page displays a FalkorDB-backed visualisation of the
  student's mastery across the 8 NCCA subjects

#### Scenario: Public anchor verification page renders

- **GIVEN** a date `2026-07-01` has a published Merkle anchor
- **WHEN** the user navigates to `/anchor/2026-07-01`
- **THEN** the page displays the Merkle root and the Base L2 tx_hash
- **AND** the page accepts a badge `id + evidence_hash` and verifies
  the Merkle path against the on-chain root

## ADDED Requirements

### Requirement: Junior Cycle subject coverage

The system SHALL provide docs-informed quest-pack generation for the
NCCA Junior Cycle programme, for the subset of the 8 Leaving Cert
subjects that also have Junior Cycle equivalents plus any Junior-Cycle-
only subjects, using the same real-extraction-input pattern as the
Leaving Cert requirement above. Junior Cycle content SHALL be wired to
the existing Junior Cycle DLT ingestion sources
(`dlt_sources/british_isles/ireland/education/junior_cycle*.py`).

#### Scenario: Junior Cycle Mathematics content is generated from real extraction

- **GIVEN** a Junior Cycle Mathematics syllabus PDF has been ingested
  and extracted into a `SyllabusDocument` record
- **WHEN** the Junior Cycle generation function runs against that record
- **THEN** the output `FormativeItem` references the extracted
  `source_page`
- **AND** the badge issued on completion has `framework="ncca-jc"`

### Requirement: England GCSE + A-Level subject coverage

The system SHALL provide docs-informed quest-pack generation for
England's GCSE and A-Level qualifications, mirroring the Leaving Cert
pattern, consuming England's existing real extraction output
(`baml_src/british_isles/england/education/{curriculum_syllabus,
exam_paper_layout,marking_scheme}.baml`). England content is English-
only (no bilingual EN + GA requirement).

#### Scenario: England GCSE quest pack generated from real extraction

- **GIVEN** an England GCSE subject's `SyllabusDocument` and `ExamPaper`
  records extracted from real ingested board PDFs (AQA, OCR, or Edexcel)
- **WHEN** the corresponding `Generate<Subject>QuestPack` function runs
- **THEN** the output quest pack's items reference the extracted
  `source_page` evidence
- **AND** the output is scoped to the correct exam board

### Requirement: Badge key-competency and evidence-type grounding

Every `SkillTreeBadge` SHALL carry a `key_competencies` field (one or
more of the NCCA's 7 senior-cycle key competencies: thinking and
solving problems, being creative, communicating, working with others,
participating in society, cultivating wellbeing, managing learning and
self) and an `evidence_type` field distinguishing formative-item
evidence from Classroom-Based-Assessment-style evidence, per the
terminology in the NCCA's own commissioned research
(`leaving_certificate/the-potential-of-technology-to-support-online-
certification-and-reporting.pdf`).

#### Scenario: Badge issued with key-competency tagging

- **GIVEN** a student completes a Mathematics formative item requiring
  problem-solving
- **WHEN** `issue_badge()` is called
- **THEN** the resulting `SkillTreeBadge`'s `key_competencies` includes
  `"thinking_and_solving_problems"`
- **AND** the badge's `evidence_type` is set correctly for the
  evidence kind that triggered issuance
