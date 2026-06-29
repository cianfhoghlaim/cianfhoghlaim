# `oideachais-marimo-dashboards` capability spec — leabharlann-email-inbox-pipeline delta

The `oideachais-marimo-dashboards` capability spec governs the
11 Marimo notebooks for the 5 educational stages + Ireland
curriculum analysis + 6 leabharlann subdir analyses +
cross-domain. The notebooks live at
`cianfhoghlaim/notebooks/_oideachais/dashboards/`.

This delta adds a 12th notebook
`email_inbox_triage.py` for the new email-inbox pipeline. The
notebook is the **primary manual-tagging + dev surface** (per
the user's preference for marimo over WebChat for dev work).

## ADDED Requirements

### Requirement: `email_inbox_triage.py` marimo notebook

The system SHALL provide a marimo notebook at
`cianfhoghlaim/notebooks/_oideachais/dashboards/email_inbox_triage.py`
with 5 sections: Loose threads, Legal-case prioritisation,
Medical-access prioritisation, Thread explorer, Hybrid
search.

#### Scenario: Notebook launches

- **WHEN** the user runs `marimo run email_inbox_triage.py`
- **THEN** the notebook launches at `http://localhost:2718`
- **AND** all 5 sections render against the live DuckLake +
  LanceDB data

#### Scenario: Section 1 — Loose threads table

- **GIVEN** the `find_loose_threads` ADK tool is reachable
- **WHEN** the user opens Section 1
- **THEN** the notebook calls `find_loose_threads(account="dkit_ie", days_idle_min=7)`
- **AND** renders a table sorted by `urgency_score` DESC
- **AND** every row has an "Open thread" button that calls
  ADK `/agents/email_triage` to summarise the thread

#### Scenario: Section 2 — Legal-case prioritisation with linked PDFs

- **GIVEN** 50 emails with `baml_class == "legal_case"`
- **WHEN** the user opens Section 2
- **THEN** the notebook renders a table of the 50 legal-case
  emails
- **AND** a 2nd column shows the 3 linked
  `gemini_deep_research/law/*.pdf` PDFs per email
- **AND** clicking a row calls `link_thread_to_research(thread_id, k=5)`
  on the ADK agent

#### Scenario: Section 3 — Medical-access prioritisation

- **GIVEN** 30 emails with `baml_class == "medical_access"`
- **WHEN** the user opens Section 3
- **THEN** the notebook renders a table of the 30
  medical-access emails
- **AND** a 2nd column shows the 3 linked
  `gemini_deep_research/medical/*.pdf` PDFs per email

#### Scenario: Section 4 — Thread explorer

- **WHEN** the user opens Section 4
- **THEN** the notebook renders a `mo.ui.tree` of all threads
  for the selected account + date range
- **AND** every thread node has a "Summarise" button that
  calls `summarise_thread(thread_id, max_chars=500)` on the
  ADK agent

#### Scenario: Section 5 — Hybrid search

- **WHEN** the user types a query in Section 5
- **THEN** the notebook calls
  `search_inbox(query, account=None, baml_class=None, limit=20)`
- **AND** renders the 20 results in a table with the cosine
  + BM25 scores visible
- **AND** the top result is highlighted

#### Scenario: ADOPT ANTI-PHISH layout

- **WHEN** the notebook is opened
- **THEN** its visual layout follows the
  `spaces/anti-phish/2_Classical_Machine_Learning_Models.ipynb`
  pattern: numbered `1_*`, `2_*`… section headers, `mo.sql`
  for DuckLake reads, altair for charts

## MODIFIED Requirements

*(None — the change only ADDS the 12th notebook; the 11
existing notebooks are unchanged.)*

## REMOVED Requirements

*(None.)*
