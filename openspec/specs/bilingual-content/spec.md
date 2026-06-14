# Bilingual Content Capability

## Purpose

`bilingual-content` is a capability of the Cianfhoghlaim platform. This document is the canonical capability spec; the corresponding source code lives in the appropriate quadrant. See `docs/00_index.md` for the quadrant map and `docs/00-core/CLAUDE.md` for the project identity.


## Background
Managing and serving curriculum content in both English and Irish languages with proper alignment and translation support.

## Requirements

### Requirement: Bilingual Content Storage
The system SHALL store content in both English and Irish with proper alignment.

#### Scenario: Parallel Content Storage
- **GIVEN** a curriculum concept with English and Irish definitions
- **WHEN** the content is stored
- **THEN** both language versions are linked by concept ID

#### Scenario: Missing Translation Handling
- **GIVEN** content that exists only in one language
- **WHEN** the content is retrieved
- **THEN** the system indicates which language is available

### Requirement: Language-Aware Routing
The system SHALL route users to content in their preferred language.

#### Scenario: URL-Based Language Selection
- **GIVEN** a user navigating to `/ga/calcalas/diorthaigh`
- **WHEN** the route is resolved
- **THEN** Irish content for derivatives is served

#### Scenario: Accept-Language Header
- **GIVEN** a request with `Accept-Language: ga`
- **WHEN** content is served without explicit language path
- **THEN** Irish content is preferred when available

### Requirement: Terminology Consistency
The system SHALL maintain consistent terminology across content.

#### Scenario: Glossary Lookup
- **GIVEN** a technical term like "Integer"
- **WHEN** translated for display
- **THEN** the consistent Irish term "Slánuimhir" is used

#### Scenario: Dialect Variants
- **GIVEN** a term with dialect variants
- **WHEN** displayed to user
- **THEN** the appropriate dialect or standard form is shown

### Requirement: Translation Quality
The system SHALL ensure translation quality for educational content.

#### Scenario: Mathematical Term Translation
- **GIVEN** a mathematical concept like "Pythagorean Theorem"
- **WHEN** translated to Irish
- **THEN** the correct form "Teoirim Pythagoras" is used

## Data Model

```json
{
  "concept_id": "PYTHAG_THEOREM",
  "name_en": "Theorem of Pythagoras",
  "name_ga": "Teoirim Pythagoras",
  "definition_en": "The square of the hypotenuse equals...",
  "definition_ga": "An chearnog ar an taobhagan..."
}
```

## Dialect Support

```cypher
(:Word {lemma: "Look"}) -[:HAS_FORM]-> (:Form {text: "Feach", dialect: "Standard"})
(:Word {lemma: "Look"}) -[:HAS_FORM]-> (:Form {text: "Amharc", dialect: "Ulster"})
```
