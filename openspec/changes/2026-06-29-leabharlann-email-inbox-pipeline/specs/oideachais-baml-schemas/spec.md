# `oideachais-baml-schemas` capability spec — leabharlann-email-inbox-pipeline delta

The `oideachais-baml-schemas` capability spec governs the BAML
extraction schemas used across the oideachais lakehouse. The
canonical 6 BAML files are `clients.baml`, `curriculum.baml`,
`culture.baml`, `document.baml`, `gaois.baml`, `code_intel.baml`
at `cianfhoghlaim/core/baml/`.

This delta adds a 7th BAML file `email.baml` with 3 classes
and 3 functions (`ClassifyEmail`, `ExtractEmailThread`,
`LinkEmailToResearch`) for the new email-inbox pipeline.

## ADDED Requirements

### Requirement: `email.baml` BAML file

The system SHALL ship
`cianfhoghlaim/core/baml/_oideachais_src/email.baml` with 3
classes (`EmailClassificationResult`, `EmailThread`,
`ResearchLink`) and 3 functions (`ClassifyEmail`,
`ExtractEmailThread`, `LinkEmailToResearch`).

#### Scenario: BAML client regenerates

- **WHEN** `baml_cli generate` runs
- **THEN** `baml_client.b.ClassifyEmail`,
  `baml_client.b.ExtractEmailThread`, and
  `baml_client.b.LinkEmailToResearch` are callable from
  Python

#### Scenario: 4 BAML test cases pass

- **GIVEN** 4 test threads in `email.baml` (1 legal HSE, 1
  medical CPTSD, 1 academic QUB admin, 1 spam)
- **WHEN** `baml_cli test email.baml` runs
- **THEN** all 4 tests pass

#### Scenario: `ClassifyEmail` returns 9-label enum

- **GIVEN** an email with subject "Re: HSE Ireland complaint
  follow-up" and body "Following up on my FOI request to HSE
  Ireland regarding the Galway mental health unit..."
- **WHEN** `b.ClassifyEmail(email_subject, email_body,
  sender_domain="hse.ie", recipient_domain="...")` runs
- **THEN** it returns `class_label="legal_case"`,
  `urgency_score=0.85`, `summary_5_words="HSE FOI follow-up
  request"`

#### Scenario: `LinkEmailToResearch` returns 3 PDFs

- **GIVEN** a legal email body and 20 candidate PDFs from
  `gemini_deep_research/law/`
- **WHEN** `b.LinkEmailToResearch(email_body,
  candidate_pdfs)` runs
- **THEN** it returns 3 `ResearchLink` rows with
  `linked_pdf_id` pointing to PDFs that semantically match the
  email body

### Requirement: `EmailClass` enum (9 labels)

The system SHALL use the `EmailClass` enum with 9 labels:
`legal_case`, `medical_access`, `academic_admin`,
`personal_correspondence`, `institutional_correspondence`,
`spam_or_marketing`, `newsletter`, `automated_notification`,
`other`.

#### Scenario: Enum covers all 9 labels

- **WHEN** `ClassifyEmail` is called on 100 sample emails
- **THEN** every returned `class_label` is one of the 9
  allowed values

## MODIFIED Requirements

*(None — the change only ADDS `email.baml` to the 6 existing
BAML files.)*

## REMOVED Requirements

*(None.)*
