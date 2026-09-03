## MODIFIED Requirements

### Requirement: PDF processing uses all 5 OCR converters and all 24 OCR models

The PDF processing pipeline SHALL use all 5 converters in
`meaisinfhoghlaim/document_factory/converters/` (deepseekocr, docling,
marker, pymupdf4llm, unstructured) AND all 24 OCR models in
`meaisinfhoghlaim/models/registry.py` for the
`pdf_ocr_compare` asset.

#### Scenario: Compare 5 converters on 1 PDF

- **WHEN** `pdf_ocr_compare` is run on a single mathematics PDF
- **THEN** all 5 converters produce a markdown output + 24 OCR models
  produce a text output
- **AND** the 5×24 comparison is written to a Ragas eval table