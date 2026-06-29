# `author-archive-cross-corpus-kg` capability spec — leabharlann-email-inbox-pipeline delta

The `author-archive-cross-corpus-kg` capability spec governs
the 3 cross-archive FalkorDB edge types between the
author-archive DLT sources and the cognify graph
(LeabharlannBook → CurriculumArea, LeabharlannZotero →
CurriculumArea, LeabharlannGemini → LegalCase).

This delta adds 3 new cross-archive edge types that link the
new email-inbox graph to the existing legal-case +
research-PDF + person graphs.

## ADDED Requirements

### Requirement: `EmailThread → LegalCase` edge type

The system SHALL create an `EmailThread → LegalCase` edge
type in FalkorDB whenever a thread's `baml_class ==
"legal_case"`.

#### Scenario: Legal thread linked to legal case

- **GIVEN** a thread with `baml_class == "legal_case"`
- **WHEN** the cognify cross-archive rules run
- **THEN** a `(EmailThread)-[:RELATES_TO]->(LegalCase)` edge
  is created in FalkorDB
- **AND** the edge has `confidence`, `link_reason`, and
  `created_at` properties

### Requirement: `EmailThread → ResearchPDF` edge type

The system SHALL create an `EmailThread → ResearchPDF` edge
type in FalkorDB for every `LinkEmailToResearch` result.

#### Scenario: Research link created

- **GIVEN** a thread with 3 `ResearchLink` results
- **WHEN** the cognify cross-archive rules run
- **THEN** 3 `(EmailThread)-[:CITES]->(ResearchPDF)` edges
  are created in FalkorDB
- **AND** each edge has `link_confidence` and `snippet`
  properties

### Requirement: `EmailAccount → Person` edge type

The system SHALL create an `EmailAccount → Person` edge type
in FalkorDB by resolving the sender's full name from the
email's `From:` header.

#### Scenario: Sender resolved to a Person node

- **GIVEN** an email with `from = "Dr. Foo Bar <foo@hse.ie>"`
- **WHEN** the cognify cross-archive rules run
- **THEN** a `(EmailAccount)-[:OWNS]->(Person)` edge is
  created in FalkorDB
- **AND** the `Person` node has `display_name = "Dr. Foo
  Bar"` and `email = "foo@hse.ie"`

## MODIFIED Requirements

*(None — the change only ADDS 3 new edge types; the 3
existing edge types are unchanged.)*

## REMOVED Requirements

*(None.)*
