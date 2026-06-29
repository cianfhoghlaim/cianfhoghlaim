# `oideachais-semantic-search` capability spec — leabharlann-email-inbox-pipeline delta

The `oideachais-semantic-search` capability spec governs the
cross-corpus LanceDB HNSW search at
`cianfhoghlaim/core/lancedb/`. The BGE-M3 multilingual +
BGE-large-en-v1.5 English embedders are already in place.

This delta adds a 6th cross-corpus search helper
`search_emails` that queries the new
`oideachais_inbox_messages` LanceDB table and joins results
with the cognify graph for richer context.

## ADDED Requirements

### Requirement: `search_emails` cross-corpus search helper

The system SHALL expose a
`search_emails(query, account=None, legal_case=None,
status=None, limit=20)` helper at
`cianfhoghlaim/core/lancedb/search_emails.py` that queries
the new `oideachais_inbox_messages` LanceDB table and joins
results with the cognify graph.

#### Scenario: Legal-case filter

- **GIVEN** 100 emails in the inbox table
- **WHEN** `search_emails("HSE Ireland appeal", legal_case=True, limit=20)` runs
- **THEN** it returns 20 rows
- **AND** every returned row has a cognify-graph join to a
  `LegalCase` node
- **AND** the top result is the email whose body most closely
  matches the query

#### Scenario: Account filter

- **GIVEN** emails across 4 accounts
- **WHEN** `search_emails("...", account="dkit_ie", limit=20)` runs
- **THEN** it returns 20 rows
- **AND** every returned row has `account == "dkit_ie"`

#### Scenario: Status filter

- **GIVEN** 50 emails with `user_override_status ==
  "confirmed"` and 50 with `user_override_status == NULL`
- **WHEN** `search_emails("...", status="unconfirmed", limit=20)` runs
- **THEN** it returns 20 rows
- **AND** every returned row has
  `user_override_status IS NULL`

### Requirement: Email search joins the cognify graph

The system SHALL enrich the `search_emails` results with
cognify-graph joins for `LegalCase` + `ResearchPDF` +
`Person` nodes.

#### Scenario: Email linked to a research PDF

- **GIVEN** an email with 3 `ResearchLink` cognify-graph
  edges to 3 `ResearchPDF` nodes
- **WHEN** `search_emails(query)` returns the email
- **THEN** the result row includes a `research_links`
  field with the 3 PDF titles + links

#### Scenario: Email linked to a Person

- **GIVEN** an email with a `EmailAccount → Person` cognify
  edge
- **WHEN** `search_emails(query)` returns the email
- **THEN** the result row includes a `sender_person`
  field with the resolved Person's display name

## MODIFIED Requirements

*(None — the change only ADDS the 6th search helper; the 5
existing helpers are unchanged.)*

## REMOVED Requirements

*(None.)*
