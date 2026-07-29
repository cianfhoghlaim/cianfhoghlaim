## ADDED Requirements

### Requirement: EU multilingual pipeline obeys the cross-region contract

The system MUST route the EU multilingual alignment pipeline through
the canonical cross-region path contract. The bilingual English +
Irish extraction files live at `dlt/european_union/<institution>/`
(unchanged), the bilingual extraction function is in
`baml/european_union/_shared/eu_document.baml`.

#### Scenario: A new bilingual extraction function is added

- **WHEN** a developer adds the
  `ExtractEUDocumentBilingualEnGa` function
- **THEN** it MUST live in
  `baml/european_union/_shared/eu_document.baml`
- **AND** it MUST be importable via
  `from cianfhoghlaim.baml_client import b`
- **AND** the function MUST accept `institution: EUInstitution`
  and `language: EULanguage` parameters
