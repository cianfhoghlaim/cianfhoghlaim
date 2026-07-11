# Spec Delta: meaisinfhoghlaim-platform

## MODIFIED Requirements

### Requirement: 12 Python OCR/VLM/memory packages in the dagster-local image

The system SHALL keep the `12 Python OCR/VLM/memory packages in the dagster-local image` requirement inside the main `## Requirements` section of `openspec/specs/meaisinfhoghlaim-platform/spec.md`. This requirement SHALL begin with a normative SHALL/MUST statement so OpenSpec strict validation parses it correctly.

The `dagster-local` Docker image SHALL install the Python packages required for the v4 OCR/VLM/memory stack: OCR packages, VLM packages, document-to-markdown packages, in-process GGUF runtime support, memory packages, and the Hugging Face CLI package.

#### Scenario: Requirement is parsed by strict validation

- **GIVEN** `openspec/specs/meaisinfhoghlaim-platform/spec.md`
- **WHEN** `openspec validate meaisinfhoghlaim-platform --strict` runs
- **THEN** the spec is valid
- **AND** this requirement is visible under the main `## Requirements` section

#### Scenario: The dagster image imports all required packages

- **WHEN** the `dagster-local` image runs a Python import smoke test for the declared OCR/VLM/memory packages
- **THEN** the command SHALL exit 0 with no `ImportError`

### Requirement: pyproject.toml extra `ocr-vision-full`

The system SHALL keep the `pyproject.toml extra ocr-vision-full` requirement inside the main `## Requirements` section of `openspec/specs/meaisinfhoghlaim-platform/spec.md` so it is visible to strict validation.

The `cianfhoghlaim/pyproject.toml` SHALL provide an `ocr-vision-full` optional-dependency group and a `dev-with-vision` composite extra for the dev notebooks that require the OCR/VLM stack.

#### Scenario: dev-with-vision installs all required dependencies

- **WHEN** `uv pip install -e '.[dev-with-vision]'` runs
- **THEN** the environment SHALL contain the OCR, VLM, doc-to-markdown, memory, notebook, and quality-tool dependencies required by the v4 dev notebook set

### Requirement: 25 dev marimo notebooks for LC5 + Gemini

The system SHALL keep the `25 dev marimo notebooks for LC5 + Gemini` requirement inside the main `## Requirements` section of `openspec/specs/meaisinfhoghlaim-platform/spec.md` so it is visible to strict validation.

The system SHALL provide working dev notebooks for the LC5 and Gemini pipelines, with parseable `@app.cell` cells, SQL-backed exploration, and visualisations.

#### Scenario: All dev notebooks parse

- **WHEN** the notebook parse smoke test runs across the LC5 and Gemini notebook directories
- **THEN** all notebooks SHALL parse without syntax errors

### Requirement: Agent + OCR thin-shim canonicalisation

The system SHALL use `from cianfhoghlaim...` for actual Python import examples in active OpenSpec specs. The older `from oideachais...` examples are logical quadrant shorthand only and MUST NOT be used as real code-import examples.

#### Scenario: A consumer imports the same agent via both paths

- **GIVEN** the canonical agent lives at `cianfhoghlaim/agents/curriculum_agent.py`
- **AND** the thin-shim re-exports it at `cianfhoghlaim/agents/adk/curriculum_agent.py`
- **WHEN** a consumer imports `curriculum_agent` through a real Python import example
- **THEN** the example uses `from cianfhoghlaim.agents.adk.curriculum_agent import curriculum_agent`
- **AND** the imported object is the same object exposed by the canonical model-layer module
