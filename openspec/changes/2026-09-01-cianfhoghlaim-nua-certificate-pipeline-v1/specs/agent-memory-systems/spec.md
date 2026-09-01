## ADDED Requirements

### Requirement: Certificate pipeline MUST cite at least one NCCA policy page per claim

The Cianfhoghlaim agent-memory-systems capability MUST expose a
certificate pipeline (`meaisinfhoghlaim/certificate/pipeline.py`)
that produces an official-style Leaving Certificate (LC) or Junior
Certificate (JC) certificate for a learner, grounded in the 5
canonical NCCA policy PDFs at `data/ireland/ncca_policy/`.

Per the 2026-09-01-cianfhoghlaim-nua-certificate-pipeline-v1 change
(Phase 7 of the cianfhoghlaim-nua v6 era plan), every claim on
every generated certificate MUST carry at least one
`CertificationCitation` referencing a page from one of the 5 NCCA
policy PDFs.

The "UNOFFICIAL" banner MUST always be present (the certificate
is never an NCCA-issued credential).

#### Scenario: A learner requests a certificate

- **WHEN** `run_certificate_pipeline(learner_id, learner_name, subject_slug, stage, lo_codes, ncca_policy_pdfs)` runs
- **THEN** the response SHALL be a `CertificateRecord` with at least one `policy_citation` per `outcome` in the `outcomes` array
- **AND** every `policy_citation` SHALL have a `source_pdf`, `page`, `quote`, and `relevance` field
- **AND** the rendered PNG bytes SHALL be valid PNG (magic bytes `\x89PNG\r\n\x1a\n`)

#### Scenario: The NCCA award descriptor coverage check

- **WHEN** a certificate's `criteria.descriptor_vocabulary` is checked
- **THEN** `check_award_descriptor_coverage(vocabulary)` SHALL return `(covered, total)` for the 5 canonical NCCA descriptors
- **AND** `check_key_competency_coverage(competencies)` SHALL return `(covered, total)` for the 6 canonical NCCA Key Competencies (including Staying Well)

### Requirement: Certificate pipeline MUST run 7 stages end-to-end (OSS-first)

The Cianfhoghlaim agent-memory-systems capability MUST expose a
7-stage certificate pipeline at `meaisinfhoghlaim/certificate/pipeline.py`
that runs:

1. `extract_certification_criteria` — BAML extraction
2. `decompose_outcomes` — LO code decomposition
3. `extract_exam_paper` — exam paper reference
4. `search_official` — RAG over the 5 NCCA policy PDFs
5. `generate_certificate_background` — OSS image generation
   (flux_schnell or stdlib gradient fallback)
6. `compose_certificate` — PIL-free text overlay
7. `save_to_provenance` — Convex persistence

The OSS-first implementation MUST work in lightweight container
builds (no PIL / torch / transformers required at import time;
they're only loaded lazily when the canonical backend is requested).

#### Scenario: The pipeline runs end-to-end with stdlib-only

- **WHEN** `run_certificate_pipeline(learner_id="learner-1", learner_name="Test", subject_slug="chemistry", stage="scoil_sinsearach", lo_codes=["LC-CHEM-LO-3.1"], ncca_policy_pdfs=[("SC-L1-L2-Programme-Statement.pdf", "Sample text...")])` runs
- **THEN** the response SHALL be a `CertificateRecord` with `png_bytes` (valid PNG) and `pdf_bytes` (PDF placeholder)
- **AND** the `criteria.stage` field SHALL equal the input `stage`
- **AND** the `outcomes` array SHALL have at least one entry per LO code