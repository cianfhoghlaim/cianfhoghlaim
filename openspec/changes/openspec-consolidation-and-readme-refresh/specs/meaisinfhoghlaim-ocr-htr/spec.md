## ADDED Requirements

The `meaisinfhoghlaim-ocr-htr` capability is created by this change.
The full Requirements + Scenarios are in the canonical spec at
`openspec/specs/meaisinfhoghlaim-ocr-htr/spec.md`.

### Requirement: 10 OCR models across 6 backends

The system SHALL provide 10 OCR models across 6 backends in
`meaisinfhoghlaim/ocr/adapters.py` and `meaisinfhoghlaim/ocr/model_registry.py`.

#### Scenario: Model registry is valid

- **WHEN** the `meaisinfhoghlaim/ocr/model_registry.py` registry is loaded
- **THEN** 10 models are listed across 6 backends

#### Scenario: Pylaia HTR

- **WHEN** the Pylaia HTR model is invoked on a historical Irish manuscript
- **THEN** the model returns the recognised text with character-level
  confidence scores

### Requirement: Irish HTR dataset

The system SHALL provide an Irish HTR dataset at
`meaisinfhoghlaim/ocr/irish_htr_dataset.py`.

#### Scenario: Dataset loads

- **WHEN** the dataset is loaded
- **THEN** the dataset returns (image, label) pairs in batches

### Requirement: VLM bridge for handwriting + math equations

The system SHALL provide a VLM bridge at
`meaisinfhoghlaim/pipelines/vlm_bridge.py`.

#### Scenario: Handwriting OCR

- **WHEN** the VLM bridge is invoked with a handwritten Irish page
- **THEN** the VLM returns the recognised text in Irish

#### Scenario: Math equation OCR

- **WHEN** the VLM bridge is invoked with a page of Irish math equations
- **THEN** the VLM returns the equations in LaTeX

### Requirement: Line segmentation

The system SHALL provide line segmentation at
`meaisinfhoghlaim/ocr/line_segmentation.py`.

#### Scenario: Page splits into lines

- **WHEN** the line segmentation module is invoked
- **THEN** the module returns a list of (y_min, y_max, image) tuples

### Requirement: Application-layer OCR for leabharlann

The system SHALL provide the application-layer `oideachais/ocr/`
wrapper.

#### Scenario: leabharlann handwritten_pages OCR

- **WHEN** the `oideachais/ocr/author_archive_ocr.py` wrapper is invoked
- **THEN** the wrapper calls the Pylaia HTR or VLM bridge
