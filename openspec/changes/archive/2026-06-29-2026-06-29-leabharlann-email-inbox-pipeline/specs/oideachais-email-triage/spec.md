# `oideachais-email-triage` capability spec — leabharlann-email-inbox-pipeline delta

`oideachais-email-triage` is a NEW capability of the
Cianfhoghlaim platform. This document is the change-side delta
file; the canonical home for the capability spec is
`openspec/specs/oideachais-email-triage/spec.md`.

The corresponding source code lives at:

- `cianfhoghlaim/pipelines/ingest/_oideachais_dlt_sources/leabharlann/email_inbox.py`
  (the MBOX DLT source)
- `cianfhoghlaim/core/baml/_oideachais_src/email.baml` (the
  ClassifyEmail / ExtractEmailThread / LinkEmailToResearch
  BAML functions)
- `cianfhoghlaim/embeddings/_oideachais_src/leabharlann_embedding.py`
  (the 4th v1 CocoIndex App `leabharlann_inbox_embedding`)
- `cianfhoghlaim/agents/adk/email_triage_agent.py` (the
  Google ADK `email_triage` agent on port 7778)
- `cianfhoghlaim/notebooks/_oideachais/dashboards/email_inbox_triage.py`
  (the marimo notebook with 5 sections — the primary manual
  surface)
- `cianfhoghlaim/cognify/cognee_integration/leabharlann_inbox_cognify.py`
  (the 4th leabharlann cognify dataset)
- `cianfhoghlaim/cognify/rules/leabharlann_inbox_cross_archive.py`
  (the 3 new cross-archive edge types)
- `cianfhoghlaim/stacks/mailcow-dockerized/` (the Mailcow
  stack with 4 per-account IMAP credentials)

The capability composes the leabharlann DLT + BAML + CocoIndex
+ Dagster + ADK + marimo + Cognee + Mailcow + openclaw
sub-systems into a single end-to-end email-triage surface.

## ADDED Requirements

### Requirement: End-to-end email ingestion from 4 accounts

The system SHALL ingest email from 4 accounts (DKIT.ie
Microsoft 365, 2 Gmail, Hotmail) into the leabharlann lakehouse
via the Mailcow `dovecot_imapsync_runner` ofelia job + a
`mailcow-export` companion container.

#### Scenario: Mailcow exports MBOX every 6 hours

- **GIVEN** 4 per-account IMAP credentials in Infisical
- **WHEN** the 6-hour `mailcow-export` cron fires
- **THEN** 4 `mailbox-<account>-<date>.mbox` files are
  written to `/srv/mailcow-exports/`
- **AND** every file is readable from the Dagster container

#### Scenario: DLT source parses the MBOX

- **WHEN** the `leabharlann_email_inbox_source()` source
  runs against the MBOX exports
- **THEN** the `inbox_index` resource yields 1 row per
  message (100 rows in the e2e demo)
- **AND** the `inbox_threads` resource yields 1 row per
  reconstructed thread (5 threads in the e2e demo)

### Requirement: BAML classification + thread extraction + research link

The system SHALL classify every email into 1 of 9 `EmailClass`
labels, extract structured thread metadata, and link the
legal threads to the top-3 Gemini Deep Research PDFs.

#### Scenario: Legal thread is auto-linked to 3 PDFs

- **GIVEN** a legal thread with `baml_class == "legal_case"`
- **WHEN** the `LinkEmailToResearch` BAML function runs with
  the top-20 candidate PDFs from `gemini_deep_research/law/`
- **THEN** it returns 3 `ResearchLink` rows
- **AND** the `linked_pdf_id` points to PDFs that
  semantically match the email body

#### Scenario: Spam email is classified correctly

- **GIVEN** a marketing email with `subject = "WIN A FREE
  iPHONE NOW"`
- **WHEN** `ClassifyEmail` runs
- **THEN** it returns `class_label == "spam_or_marketing"`
  with `confidence >= 0.9`

### Requirement: CocoIndex embedding into LanceDB

The system SHALL embed every email into the
`oideachais_inbox_messages` LanceDB table with
BAAI/bge-large-en-v1.5 (1024-d, cosine + FTS).

#### Scenario: 1 mbox → 100 vectors

- **GIVEN** a single mbox file with 100 messages
- **WHEN** `cocoindex update leabharlann_inbox_embedding` runs
- **THEN** the App yields 100 rows in
  `oideachais_inbox_messages` with stable `id`s

#### Scenario: Hybrid search returns ranked results

- **WHEN** `search_inbox("HSE Ireland malpractice appeal", baml_class="legal_case")` runs
- **THEN** it returns 20 rows ranked by RRF-fused cosine +
  BM25 score

### Requirement: Google ADK `email_triage` agent

The system SHALL expose a Google ADK `email_triage` agent on
the oideachais stack (port 7778) with 4 tools:
`classify_email_thread`, `summarise_thread`,
`link_thread_to_research`, `find_loose_threads`.

#### Scenario: `find_loose_threads` returns prioritised threads

- **GIVEN** 100 threads across 4 accounts
- **WHEN** `find_loose_threads(account="dkit_ie", days_idle_min=7)` runs
- **THEN** it returns threads where the user has not replied
  in ≥ 7 days
- **AND** sorts the results by `urgency_score` DESC

### Requirement: Marimo notebook (primary manual surface)

The system SHALL provide a marimo notebook
`email_inbox_triage.py` with 5 sections (Loose threads,
Legal-case prioritisation, Medical-access prioritisation,
Thread explorer, Hybrid search) as the primary manual-tagging
+ dev surface.

#### Scenario: Notebook launches

- **WHEN** the user runs `marimo run email_inbox_triage.py`
- **THEN** the notebook launches at `http://localhost:2718`
- **AND** all 5 sections render against the live DuckLake +
  LanceDB data

### Requirement: Cognee cognify + cross-archive edges

The system SHALL cognify the email-inbox data into a 4th
leabharlann Cognee dataset `oideachais_email_inbox` with 4
node types (EmailThread, EmailAccount, LegalCase,
ResearchLink) and 3 cross-archive edge types
(EmailThread → LegalCase, EmailThread → ResearchPDF,
EmailAccount → Person).

#### Scenario: 100 emails → 100 EmailThread nodes + 3 edges per legal thread

- **WHEN** the cognify job runs
- **THEN** 100 `EmailThread` nodes are created
- **AND** every legal-class thread has 3
  `EmailThread → ResearchPDF` edges
- **AND** every thread has 1 `EmailThread → LegalCase` edge
  (if legal) or 0 (if not)

### Requirement: openclaw WebChat email sub-UI (secondary surface)

The system SHALL expose a lightweight WebChat sub-UI at
`openclaw.cianfhoghlaim.ie/email` that loads the next loose
thread and asks the user to confirm/override the BAML
classification. The marimo notebook remains the primary
manual surface.

#### Scenario: User confirms classification

- **WHEN** the user clicks "Confirm" on a loose-thread card
- **THEN** a row is upserted into
  `leabharlann_inbox_user_overrides` with
  `user_label=<BAML_class>`, `overridden=false`

### Requirement: 10 appropriate PDFs per subdir (e2e demo corpus)

The system SHALL curate 10 appropriate PDFs per non-empty
subdir of `leabharlann/gemini_deep_research/` for the
end-to-end demo (60 PDFs total across 6 subdirs;
`identity/` is empty on disk).

#### Scenario: 60 demo PDFs validated

- **GIVEN** the 60 curated PDFs (10 per subdir × 6 subdirs)
- **WHEN** the `leabharlann_email_full_stack_demo` asset
  materialises
- **THEN** the asset validates that all 60 PDFs are present
  on disk under `/Users/cianmacandeisigh/dev/kings_college_galway/leabharlann/gemini_deep_research/<subdir>/`
- **AND** the asset materialises 1 sample legal thread
  linked to 3 PDFs from the law subdir

## MODIFIED Requirements

*(None — this is a NEW capability; no prior Requirements to
modify.)*

## REMOVED Requirements

*(None.)*
