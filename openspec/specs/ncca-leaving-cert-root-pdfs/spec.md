# NCCA Leaving Cert Root PDFs Capability

## Purpose

`ncca-leaving-cert-root-pdfs` is a capability of the Cianfhoghlaim
platform. The corresponding source code lives at:
- `cianfhoghlaim/leaving_certificate/*.pdf` (the 5 NCCA root-level programme PDFs)
- `cianfhoghlaim/dlt/british_isles/ie/education/ncca_root_pdfs.py` (the DLT source)
- `cianfhoghlaim/baml/education/pdfs/root_pdf_extraction.baml` (the 5 BAML extraction functions)
- `cianfhoghlaim/cocoindex/root_pdfs_embedding.py` (the v1 CocoIndex App)
- `cianfhoghlaim/dagster/defs/2_materials/root_pdf_assets.py` (the 5 Dagster assets)
- `cianfhoghlaim/agents/tuatha/agents/cross_subject_agent.py` (the cross-subject mastery agent)
- `cianfhoghlaim/notebooks/root_pdfs_explorer.py` (the teacher-facing marimo notebook)

This is the canonical openspec spec for the 5 NCCA root-level programme
PDFs.

## Background

The 5 NCCA root-level programme PDFs are the cross-subject foundation
documents that ground the entire Leaving Cert curriculum:

1. `key-competencies-in-senior-cycle_en.pdf` (1.2 MB, 14 pages) — the 5 NCCA Key Competencies (Information Processing, Communication, Working with Others, Personal Effectiveness, Critical & Creative Thinking)
2. `the-potential-of-online-learning-environments_en.pdf` (1.5 MB) — the online learning pedagogy
3. `the-potential-of-technology-to-support-online-certification-and-reporting.pdf` (1.6 MB) — the certification + reporting guidance
4. `scr-advisory-report_en.pdf` (1.6 MB) — the Chief Examiner commentary
5. `SC-L1-L2-Programme-Statement.pdf` (1.0 MB) — the Senior Cycle L1 + L2 programme statement

The 5 NCCA Key Competencies are the foundation of the Brown Ajah
theming: they are the 5 surviving gifts of the Tuatha Dé Danann
(Communicating = Brigid, Personal Effectiveness = Dian Cecht,
Information Processing = Ogma, Working with Others + Critical &
Creative Thinking = Lugh's samildanach).

## Requirements

### Requirement: 5 NCCA root-level PDFs as first-class assets

The system SHALL ingest the 5 NCCA root-level programme PDFs as a
first-class asset via `dlt/british_isles/ie/education/ncca_root_pdfs.py`.

### Requirement: BAML extraction of 5 root-level PDFs

The system SHALL extract structured data via 5 BAML functions in
`baml/education/pdfs/root_pdf_extraction.baml`:
1. `ExtractKeyCompetencies(pdf) -> [Competency]` (length 5)
2. `ExtractOnlineLearningPedagogy(pdf) -> PedagogySet`
3. `ExtractCertificationGuidance(pdf) -> CertGuidance`
4. `ExtractSCRAdvisory(pdf) -> ExaminerCommentary`
5. `ExtractProgrammeStatement(pdf) -> AimsExpectations`

### Requirement: CocoIndex embedding of 5 root-level PDFs

The system SHALL embed the extracted content into LanceDB via the
`root_pdfs_embedding.py` v1 CocoIndex App.

### Requirement: Dagster assets for 5 root-level PDFs

The system SHALL materialise the root-level PDF pipeline via 5 Dagster
assets in `dagster/defs/2_materials/root_pdf_assets.py`.

### Requirement: Cross-subject mastery agent

The system SHALL provide a `cross_subject_agent.py` ADK agent that uses
`b.ExtractKeyCompetencies` output to provide cross-subject mastery
reasoning.

### Requirement: Teacher-facing marimo notebook

The system SHALL provide a marimo notebook at
`notebooks/root_pdfs_explorer.py` for teacher view of all 5 root PDF
extractions.

## See also

- [cianfhoghlaim-leaving-cert-portal](../cianfhoghlaim-leaving-cert-portal/spec.md) — the consuming portal
- [oideachais-baml-schemas](../oideachais-baml-schemas/spec.md) — the BAML extraction patterns
- [oideachais-cocoindex-v1-migration](../oideachais-cocoindex-v1-migration/spec.md) — the v1 CocoIndex App pattern
- [leaving-cert-2026](../_changes/leaving-cert-2026/) — the related prior change