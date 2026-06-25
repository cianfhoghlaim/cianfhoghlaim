## MODIFIED Requirements

### Requirement: BAML functions are invoked by their consuming dlt sources
Every BAML function in `sruth/oideachais/baml_src/*.baml` MUST be
invoked by at least one Python file in the quadrant. Orphan BAML
functions (defined but never called) are forbidden in production
BAML files.

#### Scenario: A BAML function is defined but never called
- **WHEN** a BAML function is added to a `.baml` file
- **THEN** it MUST be called by a corresponding dlt source or
  Dagster asset in the same release
- **AND** if the consumer is not yet built, the function MUST be
  marked `@description("PLANNED — consumer not yet implemented")`
  in the BAML docstring

### Requirement: early_childhood.baml provides Aistear extraction
The oideachais quadrant SHALL provide an `early_childhood.baml`
module in `sruth/oideachais/baml_src/` that defines the BAML types and
function for the Aistear (early childhood) curriculum framework.

#### Scenario: The Aistear extraction is invoked
- **WHEN** `dlt_sources/ireland/aistear.py` runs and finds a PDF
  in the cache
- **THEN** it MUST call `b.ExtractAistearFramework(pdf_text, file_name)`
  to extract the framework structure
- **AND** the function MUST use `client LitellmClient`
- **AND** the function MUST return an `AistearFramework` with
  themes, principles, and learning_goals
