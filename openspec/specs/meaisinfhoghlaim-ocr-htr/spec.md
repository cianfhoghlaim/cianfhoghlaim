# Meaisínfhoghlaim OCR & HTR Capability

## Purpose

`meaisinfhoghlaim-ocr-htr` is a capability of the Cianfhoghlaim
platform. The corresponding source code lives at `meaisinfhoghlaim/ocr/`
(10 OCR models across 6 backends) and `oideachais/ocr/` (the
application-layer OCR for the leabharlann handwritten_pages resource).
See `docs/00_index.md` for the quadrant map and `docs/00-core/CLAUDE.md`
for the project identity.

This spec was created by the `openspec-consolidation-and-readme-refresh`
change and supersedes the old `agent-frameworks` spec's "OCR
backends" section (which is now in `oideachais/ocr/`) plus the
meaisinfhoghlaim/ocr/ Python module.

## Background

The OCR + HTR (handwritten text recognition) stack for Celtic-language
documents. The 10 OCR models across 6 backends are:

- **Pylaia** — open-source HTR via CTC + Connectionist Temporal
  Classification (best for historical manuscripts)
- **TrOCR** — Microsoft's transformer-based OCR (best for printed
  English text)
- **PaddleOCR** — Baidu's multi-language OCR (best for CJK + Latin
  scripts)
- **Tesseract** — the Apache-licensed OCR (best for clean printed
  text)
- **dots.ocr** — the small multilingual OCR (best for low-resource
  languages)
- **VLM-based OCR** — vision-language model OCR (best for
  handwriting + Irish mathematical equations; uses the
  `meaisinfhoghlaim/pipelines/vlm_bridge.py` VLM adapter)

The 6 backends are exposed via `meaisinfhoghlaim/ocr/adapters.py` and
the model registry at `meaisinfhoghlaim/ocr/model_registry.py`. The
Irish HTR dataset is at
`meaisinfhoghlaim/ocr/irish_htr_dataset.py`.

The application-layer `oideachais/ocr/` (the `author_archive_ocr.py` and
`pylaia_comparison.py` modules) wraps these for the leabharlann
handwritten_pages resource and the leabharlann handwritten equations
pipeline.

## Requirements

### Requirement: 10-model 6-backend OCR registry

The system SHALL provide 10 OCR models across 6 backends in
`meaisinfhoghlaim/ocr/adapters.py` and `meaisinfhoghlaim/ocr/model_registry.py`.

#### Scenario: Model registry is valid

- **GIVEN** the `meaisinfhoghlaim/ocr/model_registry.py` registry
- **WHEN** the registry is loaded
- **THEN** 10 models are listed across 6 backends (Pylaia, TrOCR,
  PaddleOCR, Tesseract, dots.ocr, VLM)

#### Scenario: Pylaia HTR

- **GIVEN** a historical Irish manuscript scan
- **WHEN** the Pylaia HTR model is invoked
- **THEN** the model returns the recognised text with character-level
  confidence scores

### Requirement: Irish HTR dataset

The system SHALL provide an Irish HTR dataset at
`meaisinfhoghlaim/ocr/irish_htr_dataset.py` for fine-tuning the Pylaia
HTR model on Irish manuscripts.

#### Scenario: Dataset loads

- **GIVEN** the Irish HTR dataset module
- **WHEN** the dataset is loaded
- **THEN** the dataset returns (image, label) pairs in batches
- **AND** the labels are Unicode-normalised (NFC) Irish text

### Requirement: VLM bridge for handwriting + math equations

The system SHALL provide a VLM bridge at
`meaisinfhoghlaim/pipelines/vlm_bridge.py` for handwriting + Irish
mathematical equation OCR.

#### Scenario: Handwriting OCR

- **GIVEN** a scanned page of handwritten Irish text
- **WHEN** the VLM bridge is invoked with the page image
- **THEN** the VLM returns the recognised text in Irish
- **AND** the response includes a confidence score

#### Scenario: Math equation OCR

- **GIVEN** a scanned page with Irish mathematical equations
- **WHEN** the VLM bridge is invoked
- **THEN** the VLM returns the equations in LaTeX

### Requirement: Line segmentation

The system SHALL provide line segmentation at
`meaisinfhoghlaim/ocr/line_segmentation.py` for splitting scanned
pages into individual text lines before OCR.

#### Scenario: Page splits into lines

- **GIVEN** a scanned page of text
- **WHEN** the line segmentation module is invoked
- **THEN** the module returns a list of (y_min, y_max, image) tuples
  for each text line

### Requirement: Application-layer OCR for leabharlann

The system SHALL provide the application-layer `oideachais/ocr/` wrapper
that the leabharlann handwritten_pages resource uses.

#### Scenario: leabharlann handwritten_pages OCR

- **GIVEN** a UoG artefact with handwritten mathematical equations
- **WHEN** the `oideachais/ocr/author_archive_ocr.py` wrapper is
  invoked
- **THEN** the wrapper calls the Pylaia HTR or VLM bridge
- **AND** the recognised text is indexed in the LanceDB
  `author_archive_equations` table

### Requirement: OCR evaluation

The system SHALL provide OCR evaluation at
`meaisinfhoghlaim/ocr/comparison_runner.py` and
`meaisinfhoghlaim/ocr/gaelic_metrics.py`.

#### Scenario: CER / WER computed

- **GIVEN** a recognised text + the ground truth
- **WHEN** the comparison runner is invoked
- **THEN** the runner returns the Character Error Rate (CER) and
  Word Error Rate (WER)
- **AND** the gaelic metrics module returns the diacritic-preservation
  rate + the Irish-specific normalisation accuracy

## Cross-references

- [`meaisinfhoghlaim/ocr/`](../../meaisinfhoghlaim/ocr/) (the 10 OCR models)
- [`oideachais/ocr/`](../../oideachais/ocr/) (the application-layer wrapper)
- [`.agents/skills/document-intelligence/SKILL.md`](../../.agents/skills/document-intelligence/SKILL.md)
- [`.agents/skills/data-engineer/SKILL.md`](../../.agents/skills/data-engineer/SKILL.md)
- [`openspec/specs/meaisinfhoghlaim-platform/spec.md`](meaisinfhoghlaim-platform/spec.md) (the quadrant overview)
- [`openspec/specs/oideachais-leabharlann/spec.md`](../oideachais-leabharlann/spec.md) (the upstream leabharlann pipeline)
