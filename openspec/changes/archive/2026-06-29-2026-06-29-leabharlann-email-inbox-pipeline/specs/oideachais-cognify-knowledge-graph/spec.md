# `oideachais-cognify-knowledge-graph` capability spec — leabharlann-email-inbox-pipeline delta

The `oideachais-cognify-knowledge-graph` capability spec governs
the 5-stage cross-stage cognify + 3 leabharlann cognify datasets
+ 3 cross-archive FalkorDB edge types. The cognify rules live
at `cianfhoghlaim/cognify/rules/`.

This delta adds a 4th leabharlann cognify dataset
(`oideachais_email_inbox`) and 3 new cross-archive edge types
that link the email inbox graph to the existing legal-case +
research-PDF + person graphs.

## ADDED Requirements

### Requirement: `oideachais_email_inbox` cognify dataset

The system SHALL add a 4th leabharlann cognify dataset
`oideachais_email_inbox` to Cognee with 4 node types:
`EmailThread`, `EmailAccount`, `LegalCase`, `ResearchLink`.

#### Scenario: Cognify ingest succeeds

- **GIVEN** the 5 new Dagster inbox assets have materialised
  (100 emails + 5 threads + 3 research links)
- **WHEN** the Cognee cognify job runs on the
  `oideachais_email_inbox` dataset
- **THEN** 100 `EmailThread` nodes + 4 `EmailAccount` nodes +
  N `LegalCase` nodes + M `ResearchLink` nodes are created

### Requirement: `EmailThread → LegalCase` cross-archive edge

The system SHALL create an `EmailThread → LegalCase` edge in
FalkorDB whenever a thread's `baml_class == "legal_case"`.

#### Scenario: Legal thread linked to legal case

- **GIVEN** a thread with `baml_class == "legal_case"`
- **WHEN** the cognify cross-archive rules run
- **THEN** a `(EmailThread)-[:RELATES_TO]->(LegalCase)` edge
  is created in FalkorDB
- **AND** the edge has `confidence`, `link_reason`, and
  `created_at` properties

### Requirement: `EmailThread → ResearchPDF` cross-archive edge

The system SHALL create an `EmailThread → ResearchPDF` edge in
FalkorDB for every `LinkEmailToResearch` result.

#### Scenario: Research link created

- **GIVEN** a thread with 3 `ResearchLink` results
- **WHEN** the cognify cross-archive rules run
- **THEN** 3 `(EmailThread)-[:CITES]->(ResearchPDF)` edges
  are created in FalkorDB
- **AND** each edge has `link_confidence` and `snippet`
  properties

### Requirement: `EmailAccount → Person` cross-archive edge

The system SHALL create an `EmailAccount → Person` edge in
FalkorDB by resolving the sender's full name.

#### Scenario: Sender resolved to a Person node

- **GIVEN** an email with `from = "Dr. Foo Bar <foo@hse.ie>"`
- **WHEN** the cognify cross-archive rules run
- **THEN** a `(EmailAccount)-[:OWNS]->(Person)` edge is
  created in FalkorDB
- **AND** the `Person` node has `display_name = "Dr. Foo Bar"`
  and `email = "foo@hse.ie"`

## MODIFIED Requirements

*(None — the change only ADDS the 4th cognify dataset and 3
new edge types. The 3 existing cross-archive edges
(LeabharlannBook → CurriculumArea, LeabharlannZotero →
CurriculumArea, LeabharlannGemini → LegalCase) are
unchanged.)*

## REMOVED Requirements

*(None.)*
