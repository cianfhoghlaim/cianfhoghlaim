# Delta: ncca-leaving-cert-root-pdfs

## ADDED Requirements

### Requirement: 5 NCCA root-level PDFs as first-class assets

The system SHALL ingest the 5 NCCA root-level programme PDFs at
`cianfhoghlaim/leaving_certificate/*.pdf` as a first-class asset:

1. `key-competencies-in-senior-cycle_en.pdf` (1.2 MB, 14 pages) → the 5 NCCA Key Competencies
2. `the-potential-of-online-learning-environments_en.pdf` (1.5 MB) → online learning pedagogy
3. `the-potential-of-technology-to-support-online-certification-and-reporting.pdf` (1.6 MB) → certification guidance
4. `scr-advisory-report_en.pdf` (1.6 MB) → Chief Examiner commentary
5. `SC-L1-L2-Programme-Statement.pdf` (1.0 MB) → programme statement

The DLT source `dlt/british_isles/ie/education/ncca_root_pdfs.py` SHALL
read each PDF once and emit a `ncca_root_pdfs` DLT resource.

#### Scenario: NCCA root PDF DLT source runs

- **GIVEN** the 5 root-level PDFs are present at `cianfhoghlaim/leaving_certificate/*.pdf`
- **WHEN** the user materialises the `ncca_root_pdfs` Dagster asset
- **THEN** the asset emits 5 rows, one per PDF
- **AND** each row carries `{pdf_path, sha256, byte_size, page_count, ingested_at}`

### Requirement: BAML extraction of 5 root-level PDFs

The system SHALL extract structured data from each root-level PDF via 5
BAML functions in `baml/education/pdfs/root_pdf_extraction.baml`:

1. `ExtractKeyCompetencies(pdf) -> [5 Competency]` — the 5 NCCA Senior Cycle Key Competencies (Information Processing, Communication, Working with Others, Personal Effectiveness, Critical & Creative Thinking)
2. `ExtractOnlineLearningPedagogy(pdf) -> PedagogySet` — the online learning pedagogy section
3. `ExtractCertificationGuidance(pdf) -> CertGuidance` — the certification + reporting guidance
4. `ExtractSCRAdvisory(pdf) -> ExaminerCommentary` — the SEC Chief Examiner commentary
5. `ExtractProgrammeStatement(pdf) -> AimsExpectations` — the Senior Cycle L1 + L2 programme statement

Each function SHALL be bilingual EN + GA on every user-facing field.

#### Scenario: Key Competencies extracted from the PDF

- **GIVEN** the `key-competencies-in-senior-cycle_en.pdf` is at the ingest queue
- **WHEN** the user runs `b.ExtractKeyCompetencies(pdf_bytes)`
- **THEN** the function returns a `[Competency]` of length 5
- **AND** each `Competency` carries `{name_en, name_ga, definition_en, definition_ga, evidence: {source_pdf, source_page, excerpt_en, excerpt_ga}}`

### Requirement: CocoIndex embedding of 5 root-level PDFs

The system SHALL embed the extracted content from each root-level PDF into
LanceDB via the `root_pdfs_embedding.py` v1 CocoIndex App. The 5 tables
SHALL be `oideachais.lc.root.{key_competencies|online_learning|certification|scr_advisory|programme_statement}.<lang>`.

#### Scenario: Key Competencies embedded into LanceDB

- **GIVEN** the extracted 5 Key Competencies from BAML
- **WHEN** the CocoIndex v1 App runs
- **THEN** the 5 tables are populated with ≥5 rows each
- **AND** each row has a BGE-M3 1024-dim embedding

### Requirement: Dagster assets for 5 root-level PDFs

The system SHALL materialise the root-level PDF pipeline via 5 Dagster
assets in `dagster/defs/2_materials/root_pdf_assets.py`:

1. `root_key_competencies_extracted`
2. `root_online_learning_extracted`
3. `root_certification_extracted`
4. `root_scr_advisory_extracted`
5. `root_programme_statement_extracted`

Each asset SHALL be partitioned by `language ∈ {en, ga}` and SHALL depend
on the corresponding `ncca_root_pdfs` asset.

#### Scenario: Mathematics practice page uses the SCR Advisory

- **GIVEN** the user navigates to `/en/leaving-cert/mathematics/practice/complex-numbers`
- **WHEN** the page loads
- **THEN** the "Exam Layout Tips" section references the SCR Advisory asset
- **AND** the section header reads "Chief Examiner Commentary — Mathematics 2026"
- **AND** the commentary cites the source PDF page from `the-potential-of-technology-to-support-online-certification-and-reporting.pdf`

### Requirement: Cross-subject mastery agent

The system SHALL provide a `cross_subject_agent.py` ADK agent at
`cianfhoghlaim/agents/tuatha/agents/` that uses
`b.ExtractKeyCompetencies` output to provide cross-subject mastery
reasoning across the 8 NCCA subjects.

#### Scenario: Mathematics student asks "how does Information Processing apply to Geography?"

- **GIVEN** the user opens the CopilotKit sidebar on `/en/leaving-cert/mathematics`
- **WHEN** the user types "how does Information Processing apply to Geography?"
- **THEN** the orchestrator dispatches to `cross_subject_agent`
- **AND** the cross_subject_agent calls `b.ExtractKeyCompetencies` to get the 5 Key Competencies
- **AND** the cross_subject_agent returns a bilingual EN+GA explanation citing both Mathematics and Geography LOs
- **AND** the explanation appears in the CopilotKit sidebar as an inline `CiSkillTree` component

### Requirement: Teacher-facing marimo notebook

The system SHALL provide a marimo notebook at
`notebooks/root_pdfs_explorer.py` for teacher view of all 5 root PDF
extractions. The notebook SHALL render:
- A tab per root PDF (Key Competencies / Online Learning / Certification / SCR Advisory / Programme Statement)
- Each tab shows the extracted content + the source PDF reference + the BGE-M3 embedding visualised

#### Scenario: Teacher opens the root PDFs explorer

- **GIVEN** the teacher opens `notebooks/root_pdfs_explorer.py` in marimo
- **WHEN** the teacher selects the "Key Competencies" tab
- **THEN** the notebook renders the 5 NCCA Key Competencies with bilingual EN + GA labels
- **AND** each Competency has a click-through to the source PDF page
- **AND** the BGE-M3 embedding is visualised as a 2D scatter plot (UMAP projection)